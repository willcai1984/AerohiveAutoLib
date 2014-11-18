#!/usr/bin/python
# Filename: scp.py
# Function: scp something to all server or server list
# coding:utf-8
# Author: Well
###Example:python scp.py -src 'console.py telnet.py' -a 
import pexpect, sys, argparse, re, time, os

def str_to_list(string, is_debug=False):
    input_list=string.split(',')
    str_list=[]
    for input_member in input_list:
        index1=re.search(r'[\D+]',input_member)
        index2=re.search(r'^\d+-\d+$',input_member)
        ###when index1 is None, match format'x'
        if index1==None:
            str_list.append(int(input_member))
        ###If index1 is Not None(True), need check index2, index2 should be True, match 'x-x' 
        elif index1 and index2:
            input_member_range_list=re.findall(r'\d+',input_member)
            ###need switch to int() before calculate
            input_member_range=int(input_member_range_list[1])-int(input_member_range_list[0])
            ###Judge if input_range is more than 0
            ######if equal to 0 add the member to the list 
            if input_member_range == 0:
                str_list.append(int(input_member_range_list[0]))
            ######if the range is >0 add the member in order
            elif input_member_range > 0:
                ###range() cannot cover the last one, so you need add 1 for the last
                for str_member in range(int(input_member_range_list[0]),int(input_member_range_list[1])+1):
                    ###primary mode is int, do not need switch 
                    str_list.append(int(str_member))
            else:
                print '''This parameter %s is not match format, the first member should less than the second ''' % input_member
                return None
        else:
            print '''This parameter %s is not match format, please enter correct format such as 'x,x,x' or 'x-x,x-x,x' ''' % input_member
            return None
    return str_list

def scp_file(src, dst, passwd, prompt, timeout):
    timeout = int(timeout)
    ###set private var
    is_passwd=False
    is_prompt=False
    ###start login process
    scp_command='scp %s %s' %(src, dst)
    scp_result=pexpect.spawn(scp_command)
    scp_result.logfile_read = sys.stdout
    index=scp_result.expect([pexpect.TIMEOUT,'yes.*no.*','password.*'],timeout=timeout)
    if index == 0:
        print 'Timeout when execute scp command'
        print 'Before is %s, After is %s' % (scp_result.before,scp_result.after)
        scp_result.close(force=True)
    elif index == 1:
        print 'Need auth firstly, send yes to confirm scp'
        scp_result.sendline('yes')
        index=scp_result.expect([pexpect.TIMEOUT,'password.*'],timeout=timeout)
        if index == 0:
            print 'Timeout when send yes to confirm'
            print 'Before is %s, After is %s' % (scp_result.before,scp_result.after)
            scp_result.close(force=True)
        elif index == 1:
            is_passwd=True
            print 'From auth mode jump to passwd mode'
        else:
            print 'No match expect value when send yes to confirm'
            print 'Before is %s, After is %s' % (scp_result.before,scp_result.after)
            scp_result.close(force=True)
    elif index == 2:
        is_passwd=True
        print 'Meet passwd mode successfully'
    else:
        print 'No match expect value execute scp command'
        print 'Before is %s, After is %s' % (scp_result.before,scp_result.after)
        scp_result.close(force=True)
    if is_passwd:
        scp_result.sendline(passwd)
        index=scp_result.expect([pexpect.TIMEOUT,pexpect.EOF,prompt],timeout=timeout)
        if index == 0:
            print 'Timeout when send password'
            print 'Before is %s, After is %s' % (scp_result.before,scp_result.after)
            scp_result.close(force=True)
        elif index == 1:
            print 'Execute scp command successfully'
            return True
        elif index == 2:
            is_prompt=True
            print 'From password mode jump to prompt mode'           
        else:
            print 'No match expect value when send password'
            print 'Before is %s, After is %s' % (scp_result.before,scp_result.after)
            scp_result.close(force=True)
    if is_prompt:
        print 'Meet prompt mode successfully'                           
    return scp_result



parse = argparse.ArgumentParser(description='scp file to servers')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')

parse.add_argument('-m', '--prompt', required=False, default='.*@.*~.*#', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=20, type=int, dest='timeout',
                    help='Time out value for every execute cli step')

parse.add_argument('-src', '--srcfile', required=False, default='telnet.py ssh.py console.py', dest='src_file',
                    help='source file path')

parse.add_argument('-dst', '--dstfile', required=False, default='10.155.41.10:/opt/auto_main/bin/', dest='dst_file',
                    help='dst file path')

parse.add_argument('-a', '--all', required=False, action='store_true',dest='is_all',
                    help='list')

def main():
    args = parse.parse_args() 
    passwd = args.passwd
    prompt = args.prompt
    src=args.src_file
    dst=args.dst_file
    scp_list=[dst]
    timeout = args.timeout
    os.system('dos2unix %s' % src)
    is_all = args.is_all
    if is_all:
        scp_list=[]
        for i in range(8,15):
            scp_list.append('10.155.44.%s0:/opt/auto_main/bin/' % i)
        for i in range(1,5):
            scp_list.append('10.155.81.%s0:/opt/auto_main/bin/' % i)
    for scp in scp_list:
        scp_result=scp_file(src, scp, passwd, prompt, timeout)
    return scp_result
            
if __name__ == '__main__':
    console_result = main()
    if console_result:
        print 'Console successfully, exit 0'
        sys.exit(0)
    else:
        print 'Console failed, exit 1'
        sys.exit(1)
