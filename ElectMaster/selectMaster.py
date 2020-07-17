#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/17 11：20
# @Author  : Zile Song
# @Software: PyCharm

import socket
import traceback
from kazoo.client import KazooClient
from kazoo.client import KazooState
from RPC.rpcClient import *
from RPC.rpcServer import *


class ElectMaster(object):

    def __init__(self):
        self.path = '/soul/master'
        self.server_path = '/soul/master/server'
        self.zk = KazooClient(hosts="192.168.5.139:2181", timeout=10)
        self.zk.start()
        self.zk.add_listener(self.my_listener)
        self.rpc_server = None
        self.rpc_client = ThreadClient()

    def create_instance(self):
        instance = self.path + '/' + socket.gethostbyname(socket.gethostname()) + '-'
        self.zk.create(path=instance, value=b"", ephemeral=True, sequence=True, makepath=True)

    def create_server_node(self):
        instance = self.server_path + '/' + 'rpcServer' + '-' + socket.gethostbyname(socket.gethostname()) + '-'
        self.zk.create(path=instance, value=b"", ephemeral=True, sequence=True, makepath=True)

    def check_rpc_server(self):
        instance_list = self.zk.get_children(self.server_path)
        for str1 in instance_list:
            if str1.split('-')[0] == 'rpcServer':
                return str1.split('-')[1]
        return 'no_server'

    def start_rpc_client(self, instance):
        url = "http://" + instance + ":8888"
        try:
            self.rpc_client.connect_server(url)
            self.rpc_client.start()
        except Exception:
            print("error:连接rpc服务异常")

    # 选主逻辑: master节点下, 所有ephemeral+sequence类型的节点中, 编号最大的获得领导权.
    def choose_master(self):
        print("*****选主开始*****")
        # 监听服务节点
        # self.zk.get_children(path=self.server_path, watch=self.my_watcher)
        instance_list = self.zk.get_children(self.path)
        print("获取节点信息")
        print(instance_list)
        instance_list.remove('server')
        instance_list = remove_str(instance_list,'server')
        print(instance_list)
        temp = self.zk.get_children(self.server_path)
        print(temp)
        instance = min(instance_list).split('-')[0]
        print("最大节点信息："+instance)
        print("当前节点信息："+socket.gethostbyname(socket.gethostname()))
        url = "http://" + instance + ":8888"
        # 被选为Master
        if instance == socket.gethostbyname(socket.gethostname()):
            print("我被选为主节点，rpc_server开始启动")
            # 创建服务节点
            self.create_server_node()
            self.zk.get_children(path=self.server_path, watch=self.my_watcher)
            if self.rpc_server is None:
                self.rpc_server = ThreadServer()
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
            print("我被选为从节点，rpc_client开始启动")
            self.zk.get_children(path=self.server_path, watch=self.my_watcher)
            try:
                if self.rpc_server.is_alive():
                    self.rpc_server.close()
                    self.rpc_server.join()
            except Exception:
                pass
            if self.rpc_client.is_alive():
                self.rpc_client.stop()
                self.rpc_client.join()
                self.rpc_client = ThreadClient()
                self.rpc_client.connect_server(url)
                self.rpc_client.start()
            else:
                self.rpc_client.connect_server(url)
                self.rpc_client.start()
            print("rpc_client启动成功")
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
            print("监听到/server下子节点变化")
            self.choose_master()
        else:
            print("监听到未识别的事件")


def remove_str(str_list, string):
    for str1 in str_list:
        if str1.split('-')[0] == string:
            str_list.remove(string)
    return str_list
