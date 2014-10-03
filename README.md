tunnelling
==========

Tunnelling is a python library (and a little main program) to do port forwarding through tunnels in python using paramiko 
(useful when you need tunnels inside other python program)

I probably copied some code from somewhere (I did this some time ago and I don't remember the sources), if you know them please tell me :)

It made only local tunnels (and does not support "tunnel chains" [yet])

Howto
=====
You can see an example in the main program inside the tunnelling/tunnelling.py file

1. Create the port forwarder
+ Connect to server:port with user
+ (if a key file is used the password is not necessary)
pfw = PortForwarder(server, port, user, forward_list, key_filename=args.key, password=args.password)

2. Start the connection and tunnels
pfw.start()

3. Close connection and tunnels when finish
pfw.stop()

Example of PortForwarder call
=============================

pfw = PortForwarder('192.168.1.1', 22, myuser, [(2222,192.168.1.45,22),], key_filename='~/.ssh/id_rsa', password=None)
Equivalent to:
$ ssh myuser@192.168.1.1 -p 22 -i ".ssh/id_rsa" -L2222:192.168.1.45:22

Usage of main
=============

./tunnelling.py myuser@192.168.1.1 -k ~/.ssh/id_rsa 2222:192.168.1.45:22
