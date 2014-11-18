1. support ssh login self
self(miss'Last login: Sun Apr  7 23:27:40 2013 from 10.155.30.109' )
[root@hztb1-mpc ~]# ssh root@10.155.40.10 -p 22
root@10.155.40.10's password: 
[root@hztb1-mpc ~]# 
remote
[root@hztb1-mpc ~]# ssh root@10.155.40.20 -p 22
The authenticity of host '10.155.40.20 (10.155.40.20)' can't be established.
RSA key fingerprint is 5a:e4:1a:1a:88:b7:bc:48:c5:77:e3:d8:f8:14:2f:33.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.155.40.20' (RSA) to the list of known hosts.
root@10.155.40.20's password: 
Last login: Sun Apr  7 23:27:40 2013 from 10.155.30.109
[root@hztb2-mpc ~]# 