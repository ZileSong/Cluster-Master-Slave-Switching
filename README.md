# Cluster：Master_Slave_Switching
zookeeper实现主从切换，xmlrpc实现时间同步。

目标：从四台主机选出一台当做Master，其他的为Slave。要求：
1）Slave的系统时间与Master同步；
2）Master下线后，再从剩下的Slave中选出一台当做Master；
3）下线主机再次上线后自动变为Slave。

思路：
1）时间同步—Slave通过python的XMLRPC调用Master中的时间获取函数获得Master的系统时间；
2）通过Zookeeper（kazoo库封装了接口）实现集群间的状态同步；
3）选举触发机制—通过watch服务节点状态触发。
