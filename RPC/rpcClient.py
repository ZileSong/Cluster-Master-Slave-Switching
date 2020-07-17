#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 09：20
# @Author  : Zile Song
# @Software: PyCharm

import time
import threading
from xmlrpc.client import ServerProxy


class ThreadClient(threading.Thread):
    def __init__(self, url="http://localhost:8888"):
        self.URL = url
        self.stop_thread = False
        threading.Thread.__init__(self)

    def get_master_time(self, server):
        master_time = server.get_system_time()
        return master_time

    def connect_server(self, url):
        self.URL = url

    def stop(self):
        self.stop_thread = True

    def run(self):
        try:
            server = ServerProxy(self.URL)
            print(server)
            while True:
                print("即将调用RPC函数")
                master_time = self.get_master_time(server)
                print("调用成功，返回值为："+master_time)
                time.sleep(5)
                if self.stop_thread:
                    break
        except Exception:
            print("error：连接RPC服务器超时")


if __name__ == '__main__':
    threadClient = ThreadClient()
    threadClient.connect_server("http://192.168.136.1:8888")
    print(threadClient.URL)
    threadClient.run()
