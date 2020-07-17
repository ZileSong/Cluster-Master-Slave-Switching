#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 10：10
# @Author  : Zile Song
# @Software: PyCharm

import time
from selectMaster import ElectMaster

node = ElectMaster()
# 向zk注册自己
node.create_instance()
instance = node.check_rpc_server()
if instance == 'no_server':
    # 进行选主
    node.choose_master()
else:
    node.zk.get_children(path=node.server_path, watch=node.my_watcher)
    node.start_rpc_client(instance)

while 1:
    time.sleep(10)
