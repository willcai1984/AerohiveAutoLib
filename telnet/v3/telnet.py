#!/usr/bin/python
# Filename: telnet.py
# Function: telnet target execute cli
# coding:utf-8
# Author: Well
# Example command:telnet.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse,re

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage

class telnet_host:
    def __init__(self, ip, user, passwd, serial='', is_debug=False, absolute_logfile='', prompt='[$#>?]'):
        self.ip=ip
        self.user=user
        self.passwd=passwd
        self.is_debug=is_debug
        self.serial=serial
        self.prompt=prompt
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
    
    def login_via_ip(self):
        ip=self.ip
        user=self.user
        passwd=self.passwd
        is_debug=self.is_debug
        telnet_login_command='telnet %s' % (ip)
        debug('''Telnet host via IP''', is_debug)
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
    
    def login_via_serial(self):
        ip=self.ip
        user=self.user
        passwd=self.passwd
        is_debug=self.is_debug
        serial=self.serial
        prompt=self.prompt
        telnet_login_command='telnet %s %s' % (ip, serial)
        debug('''Telnet host via serial''', is_debug)
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
        ###0 timeout
        ###1 PC's network is not ready
        ###2 Host serial num is not active or the serial is in used
        ###3 Other product such as dell switch and cisco serial server
        ###4 Login normal  
        index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Unable .* Connection refused','Escape character is'], timeout=5)
        if index  == 0:
            print 'Telnet host timeout, please cnfirm you can reach the host'
            telnet_login_result.close(force=True)
            return None
        ###No route to the host
        elif index == 1:
            print 'No route to the host, please check your network and confirm you can reach the host %s' % ip
            telnet_login_result.close(force=True)
            return None
        elif index == 2:
            print 'telnet: Unable to connect to remote host: Connection refused, please confirm the serial num %s is alive' % serial
            telnet_login_result.close(force=True)
            return None
        ###Welcome to Aerohive product
        elif index == 3:
            debug('Welcome to Aerohive product', is_debug)
            telnet_login_result.sendline('')
            debug('''Step2 send 'Enter' to confirm login''',is_debug)
#            telnet_login_result.sendline(user)
#            debug('''Step2 send user name '%s' to confirm login''' % user, is_debug)
            ###0 May meet aerohive pruduct powerdown on vmwarw ---EOF, telnet command is EOF already
            ###1 If the cisco serial server's port connect nothing, would stay'Escape character is '^]'.' when you send 'enter', cannot diff it from the normal way ,use timeout to mark it
            ###2 aerohive product login---login
            ###3 aerohive product already login---#
            ###4 aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
            index = telnet_login_result.expect([pexpect.EOF, pexpect.TIMEOUT, prompt, 'Use the Aerohive.*<yes|no>:','login',], timeout=3)
            if index == 0:
                print 'The serial num %s not exist, please check' % serial
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                print '''TimeOut when send 'Enter' to confirm login or the serial port is no alive, fail in step 2'''
                telnet_login_result.close(force=True)
                return None
            elif index == 2:
                debug('Login successfully, can execute cli now',is_debug)
            elif index == 3:
                debug('Login successfully, but it is the first time to login after reset the device, send no to confirm not use default configure',is_debug)
                telnet_login_result.sendline('no')
                telnet_login_result.expect(prompt)
                debug('Login successfully, can execute cli now',is_debug)
            elif index == 4:
                debug('Welcome to Aerohive product', is_debug)
                telnet_login_result.sendline(user)
                debug('Step3 send user to confirm login', is_debug)
                ### 0 = time out
                ### 1 = login correctly but meet the first time enter after reset 
                ### 2 = login correctly and can execute cli now
                index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=2)
                if index == 0:
                    print '''TimeOut when send user to confirm login, fail in step 3'''
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('''Step 4 send password to confirm login''',is_debug)
                    telnet_login_result.sendline(passwd)
                    index = telnet_login_result.expect([pexpect.TIMEOUT, 'login', prompt],timeout=2)
                    if index == 0:
                        print '''TimeOut when send password to confirm login, fail in step 4''' 
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        print '''Username or password is incorrect, please check, fail in step 4''' 
                        telnet_login_result.close(force=True)
                        return None                        
                    elif index == 2:
                        debug('''login Aerohive product successfully, can execute cli now ''',is_debug)
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
    
    def logout_via_ip(self,spawn_child):
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
    
    def logout_via_serial(self,spawn_child):
        telnet_login_result=spawn_child
        debug('....................Quit login status....................', self.is_debug)
        telnet_login_result.sendcontrol('d')
        telnet_login_result.expect('login')
        debug('....................Free serial port....................', self.is_debug)
        telnet_login_result.sendcontrol(']')
        telnet_login_result.expect('telnet>')
        telnet_login_result.sendline('quit')
        telnet_login_result.expect('Connection closed')
        debug('Free %s %s successfully' % (self.host,self.serial_num), self.is_debug)
        return telnet_login_result

def telnet_execute_cli(ip,user,passwd,cli_list,serial,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd):
    ###Is_shell is not used in this func
    timeout=int(timeout)
    ###In linux, no matter how many '/' between father folder and child folder
    absolute_logfile=logdir+'/'+logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    ###set class
    telnet=telnet_host(ip, user, passwd, serial, is_debug, absolute_logfile,prompt)
    ###login
    ###check the if has serial port, if yes, use telnet.login_via_serial(), else, use telnet.login_via_ip()
    if serial:
        telnet_host_login=telnet.login_via_serial()
    else:
        telnet_host_login=telnet.login_via_ip()
    ###execute cli
    if telnet_host_login:
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
                        telnet_host_execute=telnet.execute_command(cli_list[cli_index], prompt, timeout, telnet_host_login)
                    elif cli_index == shell_index:
                        telnet_host_execute=telnet.execute_command('_shell', '[Pp]assword:', timeout, telnet_host_login)
                        telnet_host_execute.sendline(shellpasswd)
                        index = telnet_host_execute.expect([pexpect.TIMEOUT,'[Pp]assword:','\w+:~\$'], timeout=timeout)
                        if index == 0:
                            print '''TimeOut when send shell password to confirm enter shell mode'''
                            telnet_host_execute.close(force=True)
                            return None
                        elif index == 1:
                            print '''Shell password is incorrect'''
                            telnet_host_execute.close(force=True)
                            return None
                        elif index == 2:
                            debug('Enter shell mode successfully, can execute shell command now')            
                    elif cli_index == exit_index:
                        telnet_host_execute=telnet.execute_command(cli_list[cli_index], 'Welcome back to CLI console!.*#', timeout, telnet_host_login)
                    else:
                        telnet_host_execute=telnet.execute_command(cli_list[cli_index], '\w+:~\$', timeout, telnet_host_login)           
            ######if no, should logout auto
            else:
                debug(''' 'exit' is not in the CLI list,need logout automatically''', is_debug)
                for cli_index in range(len(cli_list)):
                    if cli_index < shell_index:
                        telnet_host_execute=telnet.execute_command(cli_list[cli_index], prompt, timeout, telnet_host_login)
                    elif cli_index == shell_index:
                        telnet_host_execute=telnet.execute_command('_shell', '[Pp]assword:', timeout, telnet_host_login)
                        telnet_host_execute.sendline(shellpasswd)
                        index = telnet_host_execute.expect([pexpect.TIMEOUT,'[Pp]assword:','\w+:~\$'], timeout=timeout)
                        if index == 0:
                            print '''TimeOut when send shell password to confirm enter shell mode'''
                            telnet_host_execute.close(force=True)
                            return None
                        elif index == 1:
                            print '''Shell password is incorrect'''
                            telnet_host_execute.close(force=True)
                            return None
                        elif index == 2:
                            debug('Enter shell mode successfully, can execute shell command now', is_debug)
                        else:
                            telnet_host_execute=telnet.execute_command(cli_list[cli_index], '\w+:~\$', timeout, telnet_host_login)
            ### logout the shell mode auto
                debug('Send ctrl+d to logout the shell mode')
                telnet_host_execute.sendcontrol('d')
                index = telnet_host_execute.expect([pexpect.TIMEOUT,'Welcome back to CLI console!.*#'],timeout=5)
                if index == 0:
                    print '''TimeOut when send ctrl+d to logout shell mode'''
                    telnet_host_execute.close(force=True)
                    return None
                elif index == 1:
                    debug('Send ctrl+d to logout the shell mode successfully.', is_debug)
        else:
            debug(''' '_shell' is not in the CLI list''', is_debug)
            for cli in cli_list:
                telnet_host_execute=telnet.execute_command(cli, prompt, timeout, telnet_host_login)
                if telnet_host_execute:
                    pass
                else:
                    print 'Execute cli failed'
                    return None
    else:
        print 'Telnet login failed'
        return None
    
    ###logout
    ###check the if has serial port, if yes, use telnet.logout_via_serial(), else, use telnet.logout_via_ip()
    if serial:
        telnet_host_logout=telnet.logout_via_serial(telnet_host_execute)
    else:
        telnet_host_logout=telnet.logout_via_ip(telnet_host_execute)
    return telnet_host_logout

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

parse.add_argument('-v', '--command', required=False, action='append', default=[], dest='cli_list',
                    help='The command you want to execute')

parse.add_argument('-sp', '--shellpasswd', required=False, default=False, dest='shellpasswd',
                    help='Shell password for enter to shell mode')

parse.add_argument('-debug', '--debug', required=False, default=False,action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False,action='store_true', dest='is_shell',
                    help='enable shell mode')

parse.add_argument('-i', '--interface', required=False, default='', dest='serial',
                    help='Serial number')

parse.add_argument('-n', '--nowaite', required=False, default=False, action='store_true', dest='is_waite',
                    help='enable waite mode')

parse.add_argument('-f', '--file', required=False, default=False, dest='configfilepath',
                    help='The path of configurefile')

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
    serial=args.serial
    config_file_path=args.configfilepath
    ###check is config_file_path is null, if yes, use cli_list,if no, use config_file_path
    if config_file_path:
        debug('file_path flag is set, ignore all -v parameters')
        try:
            with open(config_file_path, mode='r') as config_file_open:
                read_cli_list=config_file_open.readlines()
                ### with'\n' in the parameters' end
            execute_cli_list=[]
            for cli in read_cli_list:
                execute_cli_list.append(re.sub('[\r\n]','',cli))   
        except IOError:
            print 'Your file path %s is wrong or the file is not exist' % config_file_path
        else:
            debug('Open configure file successfully')
    else:
        execute_cli_list=cli_list
    try:
        telnet_result=telnet_execute_cli(ip,user,passwd,execute_cli_list,serial,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd)
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
