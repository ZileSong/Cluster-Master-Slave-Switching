#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 11：20
# @Author  : Zile Song
# @Software: PyCharm

import socket
import traceback
from kazoo.client import KazooClient
from kazoo.client import KazooState
from RPC.rpcServer import *


class ElectMaster(object):

    def __init__(self):
        self.path = '/soul/master'
        self.server_path = '/soul/master/server'
        self.zk = KazooClient(hosts="192.168.5.139:2181", timeout=10)
        self.zk.start()
        self.zk.add_listener(self.my_listener)
        self.rpc_server = None

    def create_instance(self):
        instance = self.path + '/' + socket.gethostbyname(socket.gethostname()) + '-'
        self.zk.create(path=instance, value=b"", ephemeral=True, sequence=True, makepath=True)

    def create_server_node(self):
        instance = self.server_path + '/' + 'rpcServer' + '-' + socket.gethostbyname(socket.gethostname()) + '-'
        self.zk.create(path=instance, value=b"", ephemeral=True, sequence=True, makepath=True)

    def check_rpc_server(self):
        if self.zk.exists(self.server_path):
            instance_list = self.zk.get_children(self.server_path)
            for str1 in instance_list:
                if str1.split('-')[0] == 'rpcServer':
                    return str1.split('-')[1]
        return 'no_server'

    # 选主逻辑: master节点下, 所有ephemeral+sequence类型的节点中, 编号最大的获得领导权.
    def choose_master(self):
        print("*****选主开始*****")
        instance_list = self.zk.get_children(self.path)
        print("获取节点信息")
        print(instance_list)
        instance_list = remove_str(instance_list, 'server')
        print(instance_list)
        if self.zk.exists(self.server_path):
            temp = self.zk.get_children(self.server_path)
            print(temp)
        instance = min(instance_list).split('-')[0]
        print("当选节点信息："+instance)
        print("当前节点信息："+socket.gethostbyname(socket.gethostname()))
        url = "http://" + instance + ":8888"
        # 被选为Master
        if instance == socket.gethostbyname(socket.gethostname()):
            print("我被选为主节点，rpc_server开始启动")
            # 创建服务节点
            self.create_server_node()
            self.zk.get_children(path=self.server_path, watch=self.my_watcher)
            if self.rpc_server is None:
                self.rpc_server = ThreadServer(instance)
                self.rpc_server.start()
                print("开始提供rpc服务")
            else:
                if self.rpc_server.is_alive():
                    print("服务已存在，开始提供rpc服务")
                else:
                    try:
                        self.rpc_server.start()
                        print("开始提供rpc服务")
                    except RuntimeError:
                        rpc_server = ThreadServer()
                        rpc_server.start()
                        print("开始提供rpc服务")
        # 被选为Slave
        else:
            print("我被选为从节点，继续监听/soul/master/server")
            if self.rpc_server is not None:
                try:
                    self.rpc_server.close()
                except Exception:
                    print("error：关闭rpc服务异常")
            self.zk.get_children(path=self.server_path, watch=self.my_watcher)
        print("*****选主完成*****")

    def my_listener(self, state):
        if state == KazooState.LOST:
            print("会话超时:KazooState.LOST")
            while True:
                try:
                    self.create_instance()
                    self.zk.get_children(path=self.server_path, watch=self.my_watcher)
                    print("会话超时:重建会话完成!")
                    break
                except Exception:
                    traceback.print_exc()
        elif state == KazooState.SUSPENDED:
            print("会话超时:KazooState.SUSPENDED")
        elif state == KazooState.CONNECTED:
            print("会话超时:KazooState.CONNECTED")
        else:
            print("会话超时:非法状态")

    def my_watcher(self, event):
        if event.state == "CONNECTED" and event.type == "CREATED" or event.type == "DELETED" or event.type == "CHANGED" or event.type == "CHILD":
            print("监听到/soul/master/server下子节点变化")
            self.choose_master()
        else:
            print("监听到未识别的事件")


def remove_str(str_list, string):
    for str1 in str_list:
        if str1.split('-')[0] == string:
            str_list.remove(string)
    return str_list
