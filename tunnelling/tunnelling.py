#!/usr/bin/env python

"""
Tunnelling is a SSH tunnelling library (useful when you need to do tunnels inside other python programs)
"""

import select
import SocketServer
import paramiko
from threading import Thread, Event



class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler (SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip', (self.chain_host, self.chain_port), self.request.getpeername())
        except Exception, e:
            #print('Incoming request to %s:%d failed: %s' % (self.chain_host, self.chain_port, repr(e)))
            return
        if chan is None:
            print('Incoming request to %s:%d was rejected by the SSH server.' % (self.chain_host, self.chain_port))
            return
        #print('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(), chan.getpeername(), (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)
        chan.close()
        self.request.close()
        #print('Tunnel closed from %r' % (self.request,))
        #print('Tunnel closed from %r' % (self.request.getpeername(),))

class Tunnel():

    def __init__(self, ssh_client, local_port, remote_host, remote_port):
        self.c = ssh_client
        self.trans = self.c.get_transport()
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port


    def startTunnel(self):
        class SubHandler(Handler):
            chain_host = self.remote_host
            chain_port = self.remote_port
            ssh_transport = self.c.get_transport()
        my_signal = Event()
        my_signal.clear()
        def ThreadTunnel():
            self.t = ForwardServer(('127.0.0.1', self.local_port), SubHandler)
            my_signal.set() 
            self.t.serve_forever()
        Thread(target=ThreadTunnel).start()
        my_signal.wait()

    def stopTunnel(self):
        self.t.shutdown()
        #self.trans.close()
        #self.c.close()
        self.t.socket.close()
        

class PortForwarder(object):
    """
    Create connection to a server and port and do all the port forwarding jobs
    forward_list = List( (String) Local Port, (String) Address, (String) Remote Port)
    
    self.start() and self.stop() makes the connection and tunnels and stops them
    """
    def __init__(self, server, port, username, forward_list, key_filename=None, password=None):
        self.client = None
        self.server = server
        self.port = port
        self.username = username
        self.forward_list = forward_list
        self.key_filename = key_filename
        self.password = password
        self.look_for_keys = True if self.key_filename else False
        
    def start(self):    
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
        
        
        self.client.connect(self.server, self.port, username=self.username, key_filename=self.key_filename,
                           look_for_keys=self.look_for_keys, password=self.password)
       
        self.t_list = []
        for idx, (lport, rhost, rport) in enumerate(self.forward_list):
            tun = Tunnel(self.client, int(lport), rhost, int(rport))
            tun.startTunnel()
            self.t_list.append(tun)
            lport = tun.t.socket.getsockname()[1]
            print 'Tunnel active: %s:%s:%s' %(lport, rhost, rport)
            self.forward_list[idx][0] = lport
    
    def stop(self):
        for t in self.t_list:
            t.stopTunnel()
        self.client.close()
        

def main():
    import argparse
    def getArguments():
        """Argparse configuration and parsing
        Returns: arguments parsed
        """
        
        argparser = argparse.ArgumentParser(description='PyTunnel Forwarder')
        argparser.add_argument('server',
                            metavar='<server>',
                            help='Server Address')
        argparser.add_argument('-p','--port',        
                            dest='port',
                            type=int,
                            default=22,
                            metavar='<port>',
                            help='Server Port')
        argparser.add_argument('-u','--user',        
                            dest='user',
                            default='root',
                            metavar='<user>',
                            help='user')
        argparser.add_argument('-k','--key',        
                            dest='key',
                            metavar='<key>',
                            help='Key Filename')
        argparser.add_argument('-P','--Password',        
                            dest='password',
                            metavar='<password>',
                            help='Password')
        argparser.add_argument('forward_list',
                            nargs='+',
                            metavar='<port:host:hostport>',
                            help='List of forward tunnels')
    
        args = argparser.parse_args()
        return args
    
    args = getArguments()
    if len(args.server.split('@')) == 2:
        server = args.server.split('@')[1]
        user = args.server.split('@')[0] if not args.user else args.user
    else:
        server = args.server
        user = args.user
    
    
    forward_list = [fw.split(':') for fw in args.forward_list]
    
    pfw = PortForwarder(server, args.port, user, forward_list, key_filename=args.key, password=args.password)
    
    pfw.start()

    
    try:    
        while True:
            pass
    except KeyboardInterrupt:
        pfw.stop()
            
    
    exit(0)
    
if __name__=='__main__':
    main()
    
    
