1. add bumped check for the first login
one console issue. priority not high. you can process it in your free time.

https://10.155.40.240/Index.php?mod=Automation&act=HistoryJobs_StepReport&jobid=20130317-9964&tcid=2381

[Enter `^Ec?' for help]
[bumped root@10.155.41.10]

DEBUG logfile path is /logs/log20130317-9964/br_tb_check.xml_na3//show_ver_br2.br.log
DEBUG Host name is as below
DEBUG 10.155.41.231
DEBUG Serial name is as below
DEBUG br1-br100
console br1-br100 process start, init parameters............
DEBUG console login command is "console -M 10.155.41.231 br1-br100 -f -l root"
DEBUG Step1 send console command to login host
DEBUG Before is ...
DEBUG [
DEBUG After is ...
DEBUG bumped

2.Add show log.* check and add more enter for it
[root@hztb1-mpc ~]# python console.py -d 'localhost' -e 'tb1-AP340-2' -v 'show logging buff'
console tb1-AP340-2 process start, init parameters............
[Enter `^Ec?' for help]

AH-030fc0#show logging buff
                                                                                                                                   ^[[66;132R


3.Add support AP login already status, not ctrl+eco
[root@hztb3-mpc ~]# /opt/auto_main/bin/console.py -d localhost -e tb3-AP340-2 -b -sp "AfG6QpPu2J5btLsH" -v "_shell" -v "" -v "rm -f /etc/rsapublickey.pem" -v "" -v "exit" -m "AH.*#|~"
console tb3-AP340-2 process start, init parameters............
[Enter `^Ec?' for help]
[connecting...up]

AH-03b600#[connecting...up]

AH-03b600#[connecting...up]

AH-03b600#[connecting...up]

4. add \ for $ in prompt