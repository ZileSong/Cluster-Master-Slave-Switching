#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 10：05
# @Author  : Zile Song
# @Software: PyCharm

import datetime
import time
import threading
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class ThreadServer(threading.Thread):
    def __init__(self, host='192.168.136.1', port=8888):
        self._host = host
        self._port = port
        self._Server = ThreadXMLRPCServer((self._host, self._port), allow_none=True)
        threading.Thread.__init__(self)

    def close(self):
        self._Server.shutdown()

    def run(self):
        self._Server.register_function(get_system_time, "get_system_time")
        print(self._host)
        print("Listening for Client(by new thread)")
        self._Server.serve_forever()


def get_system_time():
        system_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return system_time


if __name__ == '__main__':
    threadServer = ThreadServer()
    str = get_system_time()
    print(str)
    threadServer.start()
    while 1:
        time.sleep(2)
    #threadServer.close()
    #time.sleep(20)
    #threadServer.start()

    #print("server will close")
    #time.sleep(10)
    #threadServer.close()
    #print("server end")
