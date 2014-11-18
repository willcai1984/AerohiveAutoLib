#!/usr/bin/python
# Filename: telnet.py
# Function: telnet target execute cli
# coding:utf-8
# Author: Well
# Example command:telnet.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse,re,time

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage

class telnet_host:
    def __init__(self, ip, user, passwd, serial='', is_debug=False, absolute_logfile='', prompt='[$#>]'):
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
            self.absolute_logfile_open=open(absolute_logfile, mode = 'w')
        print 'Telnet %s process start, init parameters............' % ip
    
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            ###close the mode a file firstly
            self.absolute_logfile_open.close()
            absolute_logfile=self.absolute_logfile
            ###sub 28 blanks and \r
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile=absolute_logfile_open.read()
            correct_logfile=re.sub(' {28}|\r','',originate_logfile)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.write(correct_logfile)            
        print 'Telnet %s process over.' % self.ip

    def login_via_ip(self,login_ip_timeout=2):
        ip=self.ip
        user=self.user
        passwd=self.passwd
        prompt=self.prompt
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
        ###0 timeout
        ###1 PC nerwork is abnormal
        ###2 Aerohive produce normally login
        ###3 General network product normally login
        index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Welcome to Aerohive Product.*login:', 'Connected.*Escape character.*Password:'], timeout=login_ip_timeout)
        if index  == 0:
            print 'Telnet host timeout, please confirm you can reach the host'
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
            index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=login_ip_timeout)
            if index == 0:
                print '''TimeOut when send user name to confirm login, fail in step 2''' 
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                telnet_login_result.sendline(passwd)
                debug('Step3 send password to confirm login', is_debug)
                ### 0 = time out
                ### 1 = incorrect password
                ### 2 = login correctly but meet the first time enter after reset 
                ### 3 = login correctly and can execute cli now
                index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', 'Use the Aerohive.*no>:', 'Aerohive Networks Inc.*#'], timeout=login_ip_timeout)
                if index == 0:
                    print '''TimeOut when send password to confirm login, fail in step 3'''
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    print '''User name or password is incorrect, please check, fail in step 3'''
                    telnet_login_result.close(force=True)
                    return None
                elif index == 2:
                    debug('''Step 4 login correctly but this is the first login after reset, send no to exit the rest status''',is_debug)
                    telnet_login_result.sendline('no')
                    index = telnet_login_result.expect([pexpect.TIMEOUT, prompt],timeout=login_ip_timeout)
                    if index == 0:
                        print '''TimeOut when send no to not init by default configure after reset, fail in step 4''' 
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        debug('''Step 5 send no to not init by default configure after reset successfully,could execute CLI now ''',is_debug)
                elif index == 3:
                    debug('''Step 4 login successfully and can execute CLI now ''',is_debug)
        ###general network product(such as dell switch)
        elif index == 3:
            debug('Welcome to General network product', is_debug)
            debug('''Step2 send password to confirm login''', is_debug)
            telnet_login_result.sendline(passwd)
            index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', prompt], timeout=login_ip_timeout)
            if index == 0:
                print '''TimeOut when send password to confirm login, fail in step 2'''
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                ###telnet process can be inited automatically for next login,so there only need to kill the process
                print 'Login password is incorrect, fail in step 2'
                telnet_login_result.close(force=True)
                return None
            elif index == 2:
                debug('login switch successfully, ready to enter enable mode')
        return telnet_login_result
    
    def login_via_serial(self,login_serial_timeout=5):
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
        ###3 normal login/ serial num is linked nothing/serial login switch(meet password) 
        index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Unable .* Connection refused','Escape character is'], timeout=login_serial_timeout)
        if index  == 0:
            print 'Telnet host timeout, please confirm you can reach the host'
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
            ###2 Aerohive product already login---#
            ###3 Aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
            ###4 Aerohive product login normally
            ###5 login switch via serial(meet password) 
            index = telnet_login_result.expect([pexpect.EOF, pexpect.TIMEOUT, prompt, 'Use the Aerohive.*no>:','login','[Pp]assword'], timeout=login_serial_timeout)
            if index == 0:
                print 'The serial num %s not exist or in using, please check' % serial
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
                index=telnet_login_result.expect([pexpect.TIMEOUT,prompt],timeout=login_serial_timeout)
                if index == 0:
                    print 'Timeout when send no to confirm not use default configure'
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('Login successfully, can execute cli now',is_debug)
            elif index == 4:
                debug('Welcome to Aerohive product', is_debug)
                telnet_login_result.sendline(user)
                debug('Step3 send user to confirm login', is_debug)
                ### 0 = time out
                ### 1 = login normally step 2(password)
                index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=login_serial_timeout)
                if index == 0:
                    print '''TimeOut when send user to confirm login, fail in step 3'''
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('''Step 4 send password to confirm login''',is_debug)
                    telnet_login_result.sendline(passwd)
                    ### 0 time out
                    ### 1 username or password incorrect
                    ### 2 login normally step 3(login successfully)
                    ### 3 login successfully but it's the first time to login after reset
                    index = telnet_login_result.expect([pexpect.TIMEOUT, 'login', prompt,'Use the Aerohive.*no>:'],timeout=login_serial_timeout)
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
                    elif index == 3:
                        debug('Login successfully, but it is the first time to login after reset the device, send no to confirm not use default configure',is_debug)
                        telnet_login_result.sendline('no')
                        index=telnet_login_result.expect([pexpect.TIMEOUT,prompt],timeout=login_serial_timeout)
                        if index == 0:
                            print 'Timeout when send no to confirm not use default configure'
                            telnet_login_result.close(force=True)
                            return None
                        elif index == 1:
                            debug('Login successfully, can execute cli now',is_debug)
            ###login sw via serial
            elif index == 5:
                debug('Welcome to general network product', is_debug)
                telnet_login_result.sendline(passwd)
                index=telnet_login_result.expect([pexpect.TIMEOUT,prompt],timeout=login_serial_timeout)
                if index == 0:
                    print 'Timeout when send no to confirm not use default configure'
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('Login successfully, can execute cli now',is_debug)                       
        return telnet_login_result
    
    def execute_command(self,cli,cli_expect,timeout,spawn_child):
        is_debug=self.is_debug
        telnet_login_result=spawn_child
        telnet_login_result.sendline(cli)
        ###2 may meet some display command cannot show all the parameters,need send '' to continue
        index=telnet_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:','-- More --'], timeout=timeout)
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
        elif index == 4:
            debug('H3C product, cannot show all in a page, send blank to continue',is_debug)
            while index:
                ###only need send ' ' only, no need 'enter'
                telnet_login_result.send(' ')
                index=telnet_login_result.expect([cli_expect,'-- More --'], timeout=timeout)                    
        return telnet_login_result
    
    def execute_command_via_tuple_list(self,cli_tuple_list,timeout,spawn_child,ctrl_index_list=[]):
        is_debug=self.is_debug
        telnet_login_result=spawn_child
        if ctrl_index_list:
            for cli,cli_expect in cli_tuple_list:
                if cli_tuple_list.index((cli,cli_expect)) in ctrl_index_list:
                    debug('Send ctrl command',is_debug)
                    cli=re.sub(r'ctrl-','',cli)
                    debug('Send command is ctrl-%s' % cli, is_debug)
                    telnet_login_result.sendcontrol(cli)
                else:
                    debug('Send normal command',is_debug)
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
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        telnet_login_result.send(' ')
                        index=telnet_login_result.expect([cli_expect,'--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        telnet_login_result.send(' ')
                        index=telnet_login_result.expect([cli_expect,'More:'], timeout=timeout)   
        else:
            for cli,cli_expect in cli_tuple_list:
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
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        telnet_login_result.send(' ')
                        index=telnet_login_result.expect([cli_expect,'--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        telnet_login_result.send(' ')
                        index=telnet_login_result.expect([cli_expect,'More:'], timeout=timeout)            
        return telnet_login_result
    
    
    def logout_via_ip(self,spawn_child,logout_ip_timeout=2):
        telnet_login_result=spawn_child
        debug('....................Quit login status....................',self.is_debug)
#        ###Solution 1 only support Aerohive product
#        telnet_login_result.sendcontrol('d')
#        ###cannot expect 'Connection closed by foreign host.*#' due to  there is a EOF after 'Connection closed by foreign host' before '#'
#        ###ctrl+d kill the child and raise pexpect.EOF
#        telnet_login_result.expect('Connection closed by foreign host')
        ###solution 2 support Dell switch and Aerohive product
        telnet_login_result.sendcontrol(']')
        index=telnet_login_result.expect([pexpect.TIMEOUT,'telnet>'],timeout=logout_ip_timeout)
        if index== 0:
            print '''TimeOut when send ctrl+] to enter telnet prompt status'''
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            telnet_login_result.sendline('quit')
            index=telnet_login_result.expect([pexpect.TIMEOUT,'Connection closed.'],timeout=logout_ip_timeout)
            if index==0:
                print '''TimeOut when send quit to logout serial login status'''
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                debug('Free %s successfully' % self.ip, self.is_debug)
        return telnet_login_result
    
    def logout_via_serial(self,spawn_child,logout_serial_timeout=5):
        telnet_login_result=spawn_child
        debug('....................Quit login status....................', self.is_debug)
        telnet_login_result.sendcontrol('d')
        ###send enter to confirm dell sw mode or AP mode 
        telnet_login_result.sendline('')
        ### 1 AP mode
        ### 2 switch mode
        index=telnet_login_result.expect([pexpect.TIMEOUT,'login:','#'],timeout=logout_serial_timeout)
        if index == 0:
            print '''TimeOut when send ctrl+d to logout noraml login status'''
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            debug('Logout AP successfully', self.is_debug)
        elif index == 2:
            debug('Switch mode, no need logout AP', self.is_debug)
        debug('....................Free serial port....................', self.is_debug)
        telnet_login_result.sendcontrol(']')
        index=telnet_login_result.expect([pexpect.TIMEOUT,'telnet>'],timeout=logout_serial_timeout)
        if index == 0:
            print '''TimeOut when send ctrl+] to to enter telnet prompt status'''
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            telnet_login_result.sendline('quit')
            index = telnet_login_result.expect([pexpect.TIMEOUT,'Connection closed'],timeout=logout_serial_timeout)
            if index == 0:
                print '''TimeOut when send quit to logout serial login status'''
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                debug('Free %s %s successfully' % (self.ip,self.serial), self.is_debug)
            
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
    ######serial is string mode, need to switch to int firstly
    serial=int(serial)
    if serial != 23 and serial:
        debug('serial mode login',is_debug)
        telnet_host_login=telnet.login_via_serial()
    else:
        debug('ip mode login',is_debug)
        telnet_host_login=telnet.login_via_ip()
    ###execute cli
    if telnet_host_login:
        cli_tuple_list=[]
        reset_regex=re.compile('^reset config$')
        reboot_regex=re.compile('^reboot$')
        ### Means save config tftp:.* current or save config tftp:.* bootstrap
        save_config_regex=re.compile('^save config tftp:.* (current|bootstrap)')
        save_image_regex=re.compile('^save image tftp:.*')
        ###shell use other solution, may meet incorrect status
        shell_regex=re.compile('^_shell$')
        shell_exit_regex=re.compile('^exit$')
        enble_regex=re.compile('^enable$')
        country_regex=re.compile('^boot-param country-code.*')
        ctrl_regex=re.compile('ctrl-.*')
        ###collect ctrl command index and instead sendline to sendctrl when meet the index
        ctrl_index_list=[]
        ctrl_index=0
        for cli in cli_list:
            ### be careful the speacial chara such ?, need add r before it
            #pass
            if reset_regex.search(cli):
                cli_tuple_list.append((cli,r'bootstrap configuration.*'))
                cli_tuple_list.append(('y','rebooting'))
                ctrl_index=ctrl_index + 2
            #pass
            elif reboot_regex.search(cli):
                cli_tuple_list.append((cli,r'Do you really want to reboot.*'))
                cli_tuple_list.append(('y',r'rebooting'))
                ctrl_index=ctrl_index + 2               
            #pass , select prompt can goto next is this step is failed
            elif save_config_regex.search(cli):
                cli_tuple_list.append((cli,r'configuration.*'))
                cli_tuple_list.append(('y',prompt))
                ctrl_index=ctrl_index + 2
            #pass , select prompt can goto next is this step is failed
            elif save_image_regex.search(cli):
                cli_tuple_list.append((cli,r'update image.*'))
                cli_tuple_list.append(('y',prompt))
                ctrl_index=ctrl_index + 2
            #pass...may consider the incorrect password status
            elif shell_regex.search(cli):
                cli_tuple_list.append((cli,'[Pp]assword:'))
                cli_tuple_list.append((shellpasswd,prompt))
                ctrl_index=ctrl_index + 2
            #pass
            elif shell_exit_regex.search(cli):
                cli_tuple_list.append((cli,'Welcome back to CLI console!.*#'))
                ctrl_index=ctrl_index + 1          
            elif enble_regex.search(cli):
                cli_tuple_list.append((cli,'[Pp]assword'))
                cli_tuple_list.append((passwd,prompt))
                ctrl_index=ctrl_index + 1               
            elif country_regex.search(cli):
                cli_tuple_list.append((cli,'To apply radio setting for the new country code.*'))
                cli_tuple_list.append(('y',prompt))
                ctrl_index=ctrl_index + 2
                
            elif ctrl_regex.search(cli):
                cli_tuple_list.append((cli,prompt))
                ctrl_index_list.append(ctrl_index)
            else:
                cli_tuple_list.append((cli,prompt))
                ctrl_index=ctrl_index + 1
        debug('cli_tuple_list is as below',is_debug)
        debug(cli_tuple_list,is_debug)
        debug('ctrl_index_list is as below',is_debug)
        debug(ctrl_index_list,is_debug)                                       
        telnet_host_execute=telnet.execute_command_via_tuple_list(cli_tuple_list, timeout, telnet_host_login,ctrl_index_list)
    else:
        print 'Telnet login failed'
        return None
    
    ###logout
    ###check the if has serial port, if yes, use telnet.logout_via_serial(), else, use telnet.logout_via_ip()
    if serial != 23 and serial:
        debug('serial mode logout',is_debug)
        telnet_host_logout=telnet.logout_via_serial(telnet_host_execute)
    else:
        debug('ip mode logout',is_debug)
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

parse.add_argument('-o', '--timeout', required=False, default=10,type=int, dest='timeout',
                    help='Time out value for every execute cli step')

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

parse.add_argument('-i', '--interface', required=False, default=23, type=int, dest='serial',
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
    is_reboot = False
    if 'reboot' in execute_cli_list:
        is_reboot = True
        debug('set reboot flag to True',is_debug)
    is_reset = False
    if 'reset config' in execute_cli_list:
        is_reset = True
        debug('set reset flag to True',is_debug)
    try:
        telnet_result=telnet_execute_cli(ip,user,passwd,execute_cli_list,serial,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd)
    except Exception, e:
        print str(e)
    else:
        if is_reset:
            debug('reset flag set to True, wait 30s', is_debug)
            time.sleep(30)
        if is_reboot:
            debug('reboot flag set to True, wait 30s', is_debug)
            time.sleep(30)
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
