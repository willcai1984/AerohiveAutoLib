#!/usr/bin/python
# Filename: telnet.py
# Function: telnet target execute cli
# coding:utf-8
# Author: Well
# Example command:telnet.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse,re,os

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
#            ###close the mode a file firstly
#            self.absolute_logfile_open.close()
#            absolute_logfile=self.absolute_logfile
#            ###sub 28 blanks and \r
#            with open(absolute_logfile, mode='r') as absolute_logfile_open:
#                originate_logfile=absolute_logfile_open.read()
#            correct_logfile=re.sub(' {28}|\r','',originate_logfile)
#            with open(absolute_logfile, mode='w') as absolute_logfile_open:
#                absolute_logfile_open.write(correct_logfile)
            ###v12
            self.absolute_logfile_open.close()
            absolute_logfile=self.absolute_logfile
            ###sub 28 blanks and \r
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile_list=absolute_logfile_open.readlines()
            correct_logfile_list=[]
            for log in originate_logfile_list:
                correct_log=re.sub(' {28}|\r','',log)
                correct_logfile_list.append(correct_log)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.writelines(correct_logfile_list)
##            logfile_originate=self.absolute_logfile
##            logfile_backup=self.absolute_logfile+'.backup'
##            sub_cp_cli='cp %s %s' % (logfile_originate,logfile_backup)            
##            sub_r_cli='tr -d "\r" <%s >%s' % (logfile_backup,logfile_originate)
##            sub_28blank_cli='''sed "s/                            //g" -i %s''' % logfile_originate
##            os.system(sub_cp_cli)
##            os.system(sub_r_cli)
##            debug('resub \r successfully',self.is_debug)
##            os.system(sub_28blank_cli)
##            debug('resub blank successfully',self.is_debug)
###            sub_cli='''sed -e "s/\\r//g" -e "s/                            //g" -i %s''' % self.absolute_logfile
###            os.system(sub_cli)
###            debug('resub \r and bland successfully',self.is_debug)
        print 'Telnet %s process over.' % self.ip
    ###v7 add support meet user first index == 3&4
    ###v10 modify login timeout from 2 to 10
    def login_via_ip(self,login_ip_timeout=10):
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
        ###v10 index confuse, modify index
        nor_index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Welcome to Aerohive Product.*login:', 'Connected.*Escape character.*Password:','Connected.*User Name:'], timeout=login_ip_timeout)
        ###v10 add retry func
        ###v10 retry func logic is set 2 indexs one is normal and the other is retry, match any index ,can get the correspond status
        ###modify all the elif to if and or
        retry_times=2
        retry_num=0
        retry_index=0
        if nor_index == 0:
            while retry_index == 0:
                retry_num += 1
                debug('%s time retry begin' % retry_num, is_debug)
                retry_index = telnet_login_result.expect([pexpect.TIMEOUT, 'No route to host', 'Welcome to Aerohive Product.*login:', 'Connected.*Escape character.*Password:','Connected.*User Name:'], timeout=login_ip_timeout)
                debug('%s time retry over' % retry_num, is_debug)
                ###add retry_num check here, when retry_num = retry_times, return none
                if retry_num == retry_times:
                    print 'Retry %s times and still failed, close the expect child and return none' % retry_times
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
                    telnet_login_result.close(force=True)
                    return None
        ###No route to the host
        ###v10 modify elif to if
        if nor_index == 1:
            print 'No route to the host, please check your network and confirm you can reach the host %s' % ip
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after
            telnet_login_result.close(force=True)
            return None
        ###Welcome to Aerohive product
        ###Modify elif to if
        if nor_index == 2 or retry_index == 2:
            debug('Welcome to Aerohive product', is_debug)
            telnet_login_result.sendline(user)
            debug('''Step2 send user name '%s' to confirm login''' % user, is_debug)
            index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=login_ip_timeout)
            if index == 0:
                print '''TimeOut when send user name to confirm login, fail in step 2''' 
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                telnet_login_result.sendline(passwd)
                debug('Step3 send password to confirm login', is_debug)
                ### 0 = time out
                ### 1 = incorrect password
                ### 2 = login correctly but meet the first time enter after reset 
                ### 3 = login correctly and can execute cli now
                ### v11 modify to 
                index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', 'Use the Aerohive.*no>:', prompt], timeout=login_ip_timeout)
                if index == 0:
                    print '''TimeOut when send password to confirm login, fail in step 3'''
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    print '''User name or password is incorrect, please check, fail in step 3'''
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
                    telnet_login_result.close(force=True)
                    return None
                elif index == 2:
                    debug('''Step 4 login correctly but this is the first login after reset, send no to exit the rest status''',is_debug)
                    telnet_login_result.sendline('no')
                    index = telnet_login_result.expect([pexpect.TIMEOUT, prompt],timeout=login_ip_timeout)
                    if index == 0:
                        print '''TimeOut when send no to not init by default configure after reset, fail in step 4''' 
                        print 'before is %s' % telnet_login_result.before
                        print 'after is %s' % telnet_login_result.after
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        debug('''Step 5 send no to not init by default configure after reset successfully,could execute CLI now ''',is_debug)
                elif index == 3:
                    debug('''Step 4 login successfully and can execute CLI now ''',is_debug)
        ###general network product(such as dell switch)
        ###v10 modify elif to if
        if nor_index == 3 or nor_index == 4 or retry_index == 3 or retry_index == 4:
            debug('Welcome to General network product', is_debug)
            if nor_index == 4 or retry_index == 4:
                debug('Meet the need username status, send username to confirm login', is_debug)
                telnet_login_result.sendline(user)
                telnet_login_result.expect('[Pp]assword')
            debug('''Step2 send password to confirm login''', is_debug)
            telnet_login_result.sendline(passwd)
            index = telnet_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', prompt], timeout=login_ip_timeout)
            if index == 0:
                print '''TimeOut when send password to confirm login, fail in step 2'''
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                ###telnet process can be inited automatically for next login,so there only need to kill the process
                print 'Login password is incorrect, fail in step 2'
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after
                telnet_login_result.close(force=True)
                return None
            elif index == 2:
                debug('login switch successfully, ready to enter enable mode')
        return telnet_login_result
    ###v10 modify login timeout from 2 to 10
    def login_via_serial(self,login_serial_timeout=10):
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
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after            
            telnet_login_result.close(force=True)
            return None
        ###No route to the host
        elif index == 1:
            print 'No route to the host, please check your network and confirm you can reach the host %s' % ip
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after            
            telnet_login_result.close(force=True)            
            return None
        elif index == 2:
            print 'telnet: Unable to connect to remote host: Connection refused, please confirm the serial num %s is alive' % serial
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after            
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
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after                
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                print '''TimeOut when send 'Enter' to confirm login or the serial port is no alive, fail in step 2'''
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after                
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
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after                    
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
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
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
                        print 'before is %s' % telnet_login_result.before
                        print 'after is %s' % telnet_login_result.after 
                        telnet_login_result.close(force=True)
                        return None
                    elif index == 1:
                        print '''Username or password is incorrect, please check, fail in step 4''' 
                        print 'before is %s' % telnet_login_result.before
                        print 'after is %s' % telnet_login_result.after
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
                            print 'before is %s' % telnet_login_result.before
                            print 'after is %s' % telnet_login_result.after
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
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('Login successfully, can execute cli now',is_debug)                       
        return telnet_login_result
    
#    def execute_command(self,cli,cli_expect,timeout,spawn_child):
#        is_debug=self.is_debug
#        telnet_login_result=spawn_child
#        telnet_login_result.sendline(cli)
#        ###2 may meet some display command cannot show all the parameters,need send '' to continue
#        index=telnet_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:','-- More --'], timeout=timeout)
#        if index == 0:
#            print '''TimeOut when execute CLI, fail in Execute CLI parter'''
#            print 'before is %s' % telnet_login_result.before
#            print 'after is %s' % telnet_login_result.after
#            telnet_login_result.close(force=True)
#            return None
#        elif index == 1:
#            debug('%s' % cli,is_debug)
#        elif index == 2:
#            debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
#            ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
#            more_num=0
#            while index:
##                ###only need send ' ' only, no need 'enter'
##                telnet_login_result.send(' ')
#                ###v12 modify blank to enter to forbin log match AH.*#(ignore \n\r)
#                telnet_login_result.sendline('')
#                index=telnet_login_result.expect([cli_expect,'--More--'], timeout=timeout)
#                more_num=more_num+1
#                debug('Meet more %s times' % more_num,is_debug)
#        elif index == 3:
#            debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
#            while index:
#                ###only need send ' ' only, no need 'enter'
#                telnet_login_result.send(' ')
#                index=telnet_login_result.expect([cli_expect,'More:'], timeout=timeout)
#        elif index == 4:
#            debug('H3C product, cannot show all in a page, send blank to continue',is_debug)
#            while index:
#                ###only need send ' ' only, no need 'enter'
#                telnet_login_result.send(' ')
#                index=telnet_login_result.expect([cli_expect,'-- More --'], timeout=timeout)                    
#        return telnet_login_result
    
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
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
                    telnet_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli,is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
                    ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
                    more_index=0
                    while index:
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        ### v12 modify blank to enter to forbin log generate AH.*#
                        more_index += 1
#                        debug('Meet more %s times' % more_index, is_debug)
                        telnet_login_result.sendline('')
#                        telnet_login_result.send(' ')
                        index=telnet_login_result.expect([cli_expect,'--More--'], timeout=timeout)
                    debug('Meet more %s times' % more_index, is_debug)
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
                    print 'before is %s' % telnet_login_result.before
                    print 'after is %s' % telnet_login_result.after
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
    
    ###v10 modify login timeout from 2 to 10
    def logout_via_ip(self,spawn_child,logout_ip_timeout=10):
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
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            telnet_login_result.sendline('quit')
            index=telnet_login_result.expect([pexpect.TIMEOUT,'Connection closed.'],timeout=logout_ip_timeout)
            if index==0:
                print '''TimeOut when send quit to logout serial login status'''
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after
                telnet_login_result.close(force=True)
                return None
            elif index == 1:
                debug('Free %s successfully' % self.ip, self.is_debug)
        return telnet_login_result
    ###v10 modify login timeout from 2 to 10
    def logout_via_serial(self,spawn_child,logout_serial_timeout=10):
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
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after
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
            print 'before is %s' % telnet_login_result.before
            print 'after is %s' % telnet_login_result.after
            telnet_login_result.close(force=True)
            return None
        elif index == 1:
            telnet_login_result.sendline('quit')
            index = telnet_login_result.expect([pexpect.TIMEOUT,'Connection closed'],timeout=logout_serial_timeout)
            if index == 0:
                print '''TimeOut when send quit to logout serial login status'''
                print 'before is %s' % telnet_login_result.before
                print 'after is %s' % telnet_login_result.after
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
        ###v10 add support more general status
        exit_regex=re.compile('^exit$')
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
            elif exit_regex.search(cli):
                ###v10 add support more general status
#                cli_tuple_list.append((cli,'Welcome back to CLI console!.*#'))
                cli_tuple_list.append((cli,prompt))
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
###v12 modify the prompt to AH-\w+#.*
parse.add_argument('-m', '--prompt', required=False, default='AH-\w+#.*', dest='prompt',
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
    ###v4 transfer \$ to \\$
    prompt=args.prompt
    prompt=re.sub('\$','\\$',prompt)
    timeout=args.timeout
    logdir=args.logdir
    logfile=args.logfile
    cli_list=args.cli_list
    is_debug=args.is_debug
    shellpasswd=args.shellpasswd
    is_shell=args.is_shell
    serial=args.serial
    config_file_path=args.configfilepath
    ###v9 add support both -v and -f
    ###python telnet.py -d '10.68.121.59' -v 'show ver' -debug
    ###sys.argv=['telnet.py', '-d', '10.68.121.59', '-v', 'show ver', '-debug']
#    debug('parse is as below',is_debug)
#    debug(parse,is_debug)
#    debug('args is as below',is_debug)
#    debug(args,is_debug)
    ###check is config_file_path is null, if yes, use cli_list,if no, use config_file_path
    if config_file_path:
        debug('config file flag is set, special process the cli_list')
        para_list = sys.argv
        v_argv_list = []
        f_argv_list = []
        ### get the index of the -v and -f parameters, may have the same parameters in the list, so cannot use list.index to get the index
        para_index = 0
        for para in para_list:
            if para == '-v':
                v_argv_list.append(para_index)
            if para == '-f':
                f_argv_list.append(para_index)
            para_index+=1
        debug('para_list is as below',is_debug)
        debug(para_list,is_debug)
        debug('v_command_index_list is as below',is_debug)
        debug(v_argv_list,is_debug)
        debug('f_command_index_list is as below',is_debug)
        debug(f_argv_list,is_debug)
        try:
            with open(config_file_path, mode='r') as config_file_open:
                read_cli_list=config_file_open.readlines()
                ### with'\n' in the parameters' end
            file_cli_list=[]
            for cli in read_cli_list:
                file_cli_list.append(re.sub('[\r\n]','',cli))   
        except IOError:
            print 'Your file path %s is wrong or the file is not exist' % config_file_path
        else:
            debug('Open configure file successfully',is_debug)
        ###v9 -f is the only one
        ###v9 if the index < f_index append v_para, and then and f_para, add the v_para at the last(index > f_index)
        execute_cli_list=[]
        ###v11 add support -f only,check if v_argv_list is null
        if v_argv_list:
            debug('Both -v -f flag exist',is_debug)
            ###v9 add a flag to check if v_index is the first time more than f_index only support one -f
            is_first_more=1
            for v_index in v_argv_list:
                if v_index < f_argv_list[0]:
                    execute_cli_list.append(para_list[v_index+1])
                else:
                    if is_first_more:
                        ###v9 is the first time add file configure firstly and then add v_index, set the flag to 0 at the last
                        ###v9 extend list cannot use append, should use extend
                        execute_cli_list.extend(file_cli_list)
                        execute_cli_list.append(para_list[v_index+1])
                        is_first_more=0
                    else:
                        ###v9 else add v_index only
                        execute_cli_list.append(para_list[v_index+1])
        ###v11 -f only
        else:
            debug('Only -f flag exist',is_debug)
            execute_cli_list.extend(file_cli_list)
    else:
        debug('Only -v flag exist',is_debug)
        execute_cli_list=cli_list
    debug('Execute cli list is as below...', is_debug) 
    debug(execute_cli_list,is_debug)
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
