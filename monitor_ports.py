#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import time
import threading
import os
import fcntl
import struct
from contextlib import closing
import Queue

def check_port(*args):
    q, host, port = args
    for i in xrange(3):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) == 0:
                break
            else:
                if i == 2:
                    q.put(port)


def get_interface_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s',
                            ifname[:15]))[20:24])

def get_lan_ip():
    ip = socket.gethostbyname(socket.gethostname())
    if ip.startswith("127.") and os.name != "nt":
        interfaces = [
            "eth0"
            ]
        for ifname in interfaces:
            try:
                ip = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip


if __name__ == "__main__":
    TCP_IP = get_lan_ip()
    TCP_PORT = [5091, 802, 80, 896, 806]
    que = Queue.Queue(maxsize=len(TCP_PORT))

    jobs = []
    for port in TCP_PORT:
        p = threading.Thread(target=check_port, args=(que, TCP_IP, port))
        jobs.append(p)

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    for i in xrange(que.qsize()):
        msg = "TCP port {} down !".format(que.get())
        print msg
