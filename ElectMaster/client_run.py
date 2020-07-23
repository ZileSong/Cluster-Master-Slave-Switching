#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/7/22 17:09
# @Author  : Zile Song
# @Software: PyCharm
import time
import sched
from RPC.rpcClient import RPCClient
from selectMaster import ElectMaster

schedule = sched.scheduler(time.monotonic, time.sleep)


def get_url():
    node = ElectMaster()
    url = node.check_rpc_server()
    if url != 'no_server':
        return url
    else:
        while url == 'no_server':
            time.sleep(10)
            url = node.check_rpc_server()
        return url


def process(inc):
    url = get_url()
    url = "http//:"+url+":8888"
    rpc_client = RPCClient(url)
    ret = rpc_client.sync_sys_time()
    print(ret)
    schedule.enter(inc, 0, process, (inc,))


def main(inc=3600):
    schedule.enter(0, 0, process, (inc,))
    schedule.run()


main(20)
