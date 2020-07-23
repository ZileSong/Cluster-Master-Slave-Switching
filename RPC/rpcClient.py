#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 09：20
# @Author  : Zile Song
# @Software: PyCharm

import subprocess
import time
from xmlrpc.client import ServerProxy


class RPCClient(object):
    def __init__(self, url="http//:localhost:8888"):
        self.URL = url

    def connect_server(self):
        try:
            server = ServerProxy(self.URL)
            return server
        except Exception:
            print("error：连接RPC服务器超时")
            return 0

    def sync_sys_time(self):
        server = self.connect_server()
        if server != 0:
            master_time = server.get_system_time()
            print(master_time)
            try:
                time.strptime(master_time, "%Y-%m-%d %H:%M:%S")
                pobj_set_ntp = subprocess.Popen('timedatectl set-ntp false', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                pobj_set_time = subprocess.Popen('timedatectl set-time "'+master_time+'"', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return True
            except Exception:
                return False

        else:
            print("error:connect to server failed")
            return False
