#!/usr/bin/env python
# Filename: telnet.py
# Function: telnet target execute cli
# coding:utf-8
# Author: Well
# Example command:telnet.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage

class telnet_host:
    def __init__(self, ip, user, passwd, is_debug=False, absolute_logfile=''):
        self.ip=ip
        self.user=user
        self.passwd=passwd
        self.is_debug=is_debug
        self.absolute_logfile=absolute_logfile
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open=open(absolute_logfile, mode = 'a')
        print 'Telnet %s process start, init parameters............' % ip
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open.close()
        print 'Telnet %s process over.' % self.ip
    def login(self):
        ip=self.ip
        user=self.user
        passwd=self.passwd
        is_debug=self.is_debug
        telnet_login_command='telnet %s' % (ip)
        debug('''Telnet login command is "%s"''' % telnet_login_command, is_debug)
        debug('Step1 send telnet command to login host', is_debug)
        telnet_login_result=pexpect.spawn(telnet_login_command)
        ###Judge if the log file has been set, if yes, redirect the log to file
        ###else to stdout
        if self.absolute_logfile == './stdout':
            #telnet_login_result.logfile=sys.stdout
            #telnet_login_result.logfile_send=sys.stdout
            telnet_login_result.logfile_read=sys.stdout
        else:
            #telnet_login_result.logfile=self.absolute_logfile_open
            #telnet_login_result.logfile_send=self.absolute_logfile_open
            telnet_login_result.logfile_read=self.absolute_logfile_open
        index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Welcome to Aerohive Product.*login:', 'Connected.*Escape character.*Password:'], timeout=2)
        if index  == 0:
            print 'Telnet host timeout, please cnfirm you can reach the host'
            print telnet_login_result.before, telnet_login_result.after
            telnet_login_result.close(force=True)
            return None
        ###No route to the host
        elif index == 1:
            print 'No route to the host, please check your network and confirm you can reach the host %s' % ip
            telnet_login_result.close(force=True)
            return None
        ###Welcome to Aerohive product
        elif index == 2:
            debug('Welcome to Aerohive product', is_debug)
            telnet_login_result.sendline(user)
            debug('''Step2 send user name '%s' to confirm login''' % user, is_debug)
            index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=2)
            if index == 0:
                print '''TimeOut when send user name to confirm login, fail in step 2''' 
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                telnet_login_result.sendline(passwd)
                debug('Step3 send password to confirm login', is_debug)
                ### 0 = time out
                ### 1 = login correctly but meet the first time enter after reset 
                ### 2 = login correctly and can execute cli now
                index = telnet_login_result.expect([pexpect.TIMEOUT, 'Use the Aerohive.*<yes|no>:','Aerohive Networks Inc.*#'], timeout=2)
                if index == 0:
                    print '''TimeOut when send password to confirm login, fail in step 3'''
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('''Step 4 login correctly but this is the first login after reset, send no to exit the rest status''',is_debug)
                    telnet_login_result.sendline('no')
                    index = telnet_login_result.expect([pexpect.TIMEOUT, self.prompt],timeout=2)
                    if index == 0:
                        print '''TimeOut when send no to not init by default configure after reset, fail in step 4''' 
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        debug('''Step 5 send no to not init by default configure after reset successfully,could execute CLI now ''',is_debug)
                elif index == 2:
                    debug('''Step 4 login successfully and can execute CLI now ''',is_debug)
        ###general network product(such as dell switch)
        elif index == 3:
            debug('Welcome to General network product', is_debug)
            debug('''Step2 send password to confirm login''', is_debug)
            telnet_login_result.sendline(passwd)
            index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', '\w+>'], timeout=2)
            if index == 0:
                print '''TimeOut when send password to confirm login, fail in step 2'''
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                print 'Login password is incorrect, fail in step 2'
                telnet_login_result.close(force=True)
                return None
            elif index == 2:
                debug('''Step3 send 'enable' to enter enable mode''', is_debug)
                telnet_login_result.sendline('enable')
                index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=2)
                if index == 0:
                    print '''TimeOut when send 'enable' to enter enable mode, fail in step 3'''
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('''Step4 send password to enter enable mode''', is_debug)
                    telnet_login_result.sendline(passwd)
                    index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', '\w+#'], timeout=2)
                    if index == 0:
                        print '''TimeOut when send password to confirm enter enable mode, fail in step 4'''
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        print 'Enable password is incorrect, fail in step 4'
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 2:
                        debug('''Enter general network product enable mode successfully''', is_debug)
        return telnet_login_result
    
    def execute_command(self,cli,cli_expect,timeout,spawn_child):
        is_debug=self.is_debug
        telnet_login_result=spawn_child
        telnet_login_result.sendline(cli)
        ###2 may meet some display command cannot show all the parameters,need send '' to continue
        index=telnet_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:'], timeout=timeout)
        if index == 0:
            print '''TimeOut when execute CLI, fail in Execute CLI parter'''
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            debug('%s' % cli,is_debug)
        elif index == 2:
            debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
            ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
            while index:
                ###only need send ' ' only, no need 'enter'
                telnet_login_result.send(' ')
                index=telnet_login_result.expect([cli_expect,'--More--'], timeout=timeout)
        elif index == 3:
            debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
            while index:
                ###only need send ' ' only, no need 'enter'
                telnet_login_result.send(' ')
                index=telnet_login_result.expect([cli_expect,'More:'], timeout=timeout)            
        return telnet_login_result
    
    def logout(self,spawn_child):
        telnet_login_result=spawn_child
        debug('....................Quit login status....................',self.is_debug)
#        ###Solution 1 only support Aerohive product
#        telnet_login_result.sendcontrol('d')
#        ###cannot expect 'Connection closed by foreign host.*#' due to  there is a EOF after 'Connection closed by foreign host' before '#'
#        ###ctrl+d kill the child and raise pexpect.EOF
#        telnet_login_result.expect('Connection closed by foreign host')
        ###solution 2 support Dell switch and Aerohive product
        telnet_login_result.sendcontrol(']')
        telnet_login_result.expect('telnet>')
        telnet_login_result.sendline('quit')
        telnet_login_result.expect('Connection closed.')
        return telnet_login_result

def telnet_execute_cli(ip,user,passwd,cli_list,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd):
    ###Is_shell is not used in this func
    timeout=int(timeout)
    ###In linux, no matter how many '/' between father folder and child folder
    absolute_logfile=logdir+'/'+logfile
    ###set class
    telnet=telnet_host(ip, user, passwd, is_debug, absolute_logfile)
    ###login
    telnet_aerohive_login=telnet.login()
    ###execute cli
    if telnet_aerohive_login:
    ###Check if '_shell' in clilist
        if '_shell' in cli_list:
            ###get the '_shell' index
            shell_index=cli_list.index('_shell')
            debug(''' '_shell' is in the CLI list, and the index is %s''' % shell_index, is_debug)
            ### check if 'exit' in cli_list(for exist shell mode)
            ###### if yes, can logout normally, between shell_index and exit_index' prompt is set to shell prompt, other is normal prompt
            if 'exit' in cli_list:
                exit_index=cli_list.index('exit')
                debug(''' 'exit' is in the CLI list, and the index is %s, can logout the shell mode normally''' % exit_index, is_debug)
                for cli_index in range(len(cli_list)):
                    if cli_index < shell_index or cli_index > exit_index:
                        telnet_aerohive_execute=telnet.execute_command(cli_list[cli_index], prompt, timeout, telnet_aerohive_login)
                    elif cli_index == shell_index:
                        telnet_aerohive_execute=telnet.execute_command('_shell', '[Pp]assword:', timeout, telnet_aerohive_login)
                        telnet_aerohive_execute.sendline(shellpasswd)
                        index = telnet_aerohive_execute.expect([pexpect.TIMEOUT,'[Pp]assword:','\w+:~\$'], timeout=timeout)
                        if index == 0:
                            print '''TimeOut when send shell password to confirm enter shell mode'''
                            telnet_aerohive_execute.close(force=True)
                            return None
                        elif index == 1:
                            print '''Shell password is incorrect'''
                            telnet_aerohive_execute.close(force=True)
                            return None
                        elif index == 2:
                            debug('Enter shell mode successfully, can execute shell command now')            
                    elif cli_index == exit_index:
                        telnet_aerohive_execute=telnet.execute_command(cli_list[cli_index], 'Welcome back to CLI console!.*#', timeout, telnet_aerohive_login)
                    else:
                        telnet_aerohive_execute=telnet.execute_command(cli_list[cli_index], '\w+:~\$', timeout, telnet_aerohive_login)           
            ######if no, should logout auto
            else:
                debug(''' 'exit' is not in the CLI list,need logout automatically''', is_debug)
                for cli_index in range(len(cli_list)):
                    if cli_index < shell_index:
                        telnet_aerohive_execute=telnet.execute_command(cli_list[cli_index], prompt, timeout, telnet_aerohive_login)
                    elif cli_index == shell_index:
                        telnet_aerohive_execute=telnet.execute_command('_shell', '[Pp]assword:', timeout, telnet_aerohive_login)
                        telnet_aerohive_execute.sendline(shellpasswd)
                        index = telnet_aerohive_execute.expect([pexpect.TIMEOUT,'[Pp]assword:','\w+:~\$'], timeout=timeout)
                        if index == 0:
                            print '''TimeOut when send shell password to confirm enter shell mode'''
                            telnet_aerohive_execute.close(force=True)
                            return None
                        elif index == 1:
                            print '''Shell password is incorrect'''
                            telnet_aerohive_execute.close(force=True)
                            return None
                        elif index == 2:
                            debug('Enter shell mode successfully, can execute shell command now', is_debug)
                        else:
                            telnet_aerohive_execute=telnet.execute_command(cli_list[cli_index], '\w+:~\$', timeout, telnet_aerohive_login)
            ### logout the shell mode auto
                debug('Send ctrl+d to logout the shell mode')
                telnet_aerohive_execute.sendcontrol('d')
                index = telnet_aerohive_execute.expect([pexpect.TIMEOUT,'Welcome back to CLI console!.*#'],timeout=5)
                if index == 0:
                    print '''TimeOut when send ctrl+d to logout shell mode'''
                    telnet_aerohive_execute.close(force=True)
                    return None
                elif index == 1:
                    debug('Send ctrl+d to logout the shell mode successfully.', is_debug)
        else:
            debug(''' '_shell' is not in the CLI list''', is_debug)
            for cli in cli_list:
                telnet_aerohive_execute=telnet.execute_command(cli, prompt, timeout, telnet_aerohive_login)
                if telnet_aerohive_execute:
                    pass
                else:
                    print 'Execute cli failed'
                    return None
    else:
        print 'Telnet login failed'
        return None
    
    ###logout
    telnet_aerohive_logout=telnet.logout(telnet_aerohive_execute)
    return telnet_aerohive_logout

parse = argparse.ArgumentParser(description='Telnet host to execute CLI')
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')

parse.add_argument('-m', '--prompt', required=False, default='AH.*#', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default='60', dest='timeout',
                    help='Process time out')

parse.add_argument('-l', '--logdir', required=False, default='.', dest='logdir',
                    help='The log file dir')

parse.add_argument('-z', '--logfile', required=False, default='stdout', dest='logfile',
                    help='The log file name')

parse.add_argument('-v', '--command', required=True, action='append', default=[], dest='cli_list',
                    help='The command you want to execute')

parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='shellpasswd',
                    help='Shell password for enter to shell mode')

parse.add_argument('-debug', '--debug', required=False, default=False,action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False,action='store_true', dest='is_shell',
                    help='enable shell mode')


def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.user
    passwd=args.passwd
    prompt=args.prompt
    timeout=args.timeout
    logdir=args.logdir
    logfile=args.logfile
    cli_list=args.cli_list
    is_debug=args.is_debug
    shellpasswd=args.shellpasswd
    is_shell=args.is_shell
    try:
        telnet_result=telnet_execute_cli(ip,user,passwd,cli_list,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd)
    except Exception, e:
        print str(e)
    else:
        return telnet_result
            
if __name__=='__main__':
    telnet_result=main()
    if telnet_result:
        telnet_result.close()
        print 'Telnet successfully, exit 0'
        sys.exit(0)
    else:
        print 'Telnet failed, exit 1'
        sys.exit(1)