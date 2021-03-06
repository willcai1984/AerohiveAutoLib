#!/usr/bin/python
# Filename: console.py
# Function: login target execute cli via console server
# coding:utf-8
# Author: Well
# Example command: console.py -i 782 -e tb1-ap350-3 -v "show run" -d localhost -u admin -p aerohive -m "AH.*#"
# Transmit command: console -M localhost tb1-ap350-3 -f -l root
import pexpect, sys, argparse, re, time

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage

class console_host:
    def __init__(self, ip, serialname, user, passwd, is_debug=False, absolute_logfile='', prompt='[$#>]'):
        self.ip=ip
        self.serialname=serialname
        self.user=user
        self.passwd=passwd
        self.is_debug=is_debug
        self.prompt=prompt
        self.absolute_logfile=absolute_logfile
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open=open(absolute_logfile, mode = 'a')
        print 'console %s process start, init parameters............' % serialname
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
        print 'console %s process over.' % self.ip
        
    def login(self,retry_times=5,login_timeout=5):
        ip=self.ip
        serialname=self.serialname
        user=self.user
        passwd=self.passwd
        is_debug=self.is_debug
        prompt=self.prompt
        console_login_command='console -M %s %s -f -l root' % (ip,serialname)
        debug('''console login command is "%s"''' % console_login_command, is_debug)
        debug('Step1 send console command to login host', is_debug)
        console_login_result=pexpect.spawn(console_login_command)
        ###Judge if the log file has been set, if yes, redirect the log to file
        ###else to stdout
        if self.absolute_logfile == './stdout':
            #console_login_result.logfile=sys.stdout
            #console_login_result.logfile_send=sys.stdout
            console_login_result.logfile_read=sys.stdout
        else:
            #console_login_result.logfile=self.absolute_logfile_open
            #console_login_result.logfile_send=self.absolute_logfile_open
            console_login_result.logfile_read=self.absolute_logfile_open
        ###0 timeout
        ###1 no this console name in the localhost
        ###2 normal login
        index = console_login_result.expect([pexpect.TIMEOUT, 'localhost: console .* not found','Enter .* for help.*'], timeout=login_timeout)
        if index  == 0:
            print 'console host timeout, please confirm you can reach the host'
            console_login_result.close(force=True)
            return None
        elif index == 1:
            print 'The hostname %s is not aliveable in the localhost, please confirm' % serialname
            console_login_result.close(force=True)
            return None
        elif index == 2:
            ####check if is the reboot status(reboot status no need to type 'enter' will show something on the screen)(before boot load, for the reset status not waite 30s)
            ###0 non reboot status
            ###1 reboot status
            ### cannot use [\w\s]+,may meet the point you do not want
            ### timeout value set to 1.1s and can more than auto boot interval
            is_reboot_before_bootload = console_login_result.expect([pexpect.TIMEOUT, '[\w]+'],timeout=1.1)
            nor_index = 0
            retry_index = 0
            retry_num = 0
            nor_retry_index = 0
            nor_retry_num = 0                    
            if is_reboot_before_bootload:
                debug('Reboot before bootload status', is_debug)
                debug('Before is ...',is_debug)
                debug(console_login_result.before,is_debug)
                debug('After is ...',is_debug)
                debug(console_login_result.after,is_debug)
                ###v4 check if meet the bumped status
                if console_login_result.after == 'bumped':
                    debug('Meet Bumped mode, send enter twice')
                    ###v6 send twice enter, may generate twice prompt, may influence next step
#                    console_login_result.sendline('')
#                    console_login_result.sendline('')
                    ###v6 use retry to forbid confuse
                    while retry_index == 0:
                        retry_num += 1
                        debug('%s time retry begin' % retry_num, is_debug)
                        console_login_result.sendline('')
                        retry_index = console_login_result.expect([pexpect.TIMEOUT, 'Welcome to Aerohive Product.*login','[Pp]assword',prompt], timeout=login_timeout)
                        debug('%s time retry over' % retry_num, is_debug)
                        ###add retry_num check here, when retry_num = retry_times, return none
                        if retry_num == retry_times:
                            print 'Retry %s times and still failed, close the expect child and return none' % retry_times
                            console_login_result.close(force=True)
                            return None 
#               while retry_index == 0 and retry_num <= retry_times :
                ###retry till match the key words or the retry times you set                    
                else:
                    debug('Meet Reboot before bootload mode, waite for power on successfully')
                    while retry_index == 0:
                        retry_num += 1
                        ### only use expect func for forbin enter bottload mode
                        debug('%s time retry begin' % retry_num, is_debug)
                        ### v5 add prompt for already login status
                        retry_index = console_login_result.expect([pexpect.TIMEOUT, 'Welcome to Aerohive Product.*login','[Pp]assword',prompt], timeout=login_timeout)
                        debug('%s time retry over' % retry_num, is_debug)
                        ###add retry_num check here, when retry_num = retry_times, return none
                        if retry_num == retry_times:
                            print 'Retry %s times and still failed, close the expect child and return none' % retry_times
                            console_login_result.close(force=True)
                            return None
            else:
                debug('Reboot after bootload status or normal(no reboot) status',is_debug)
                console_login_result.sendline('')
                debug('''Step2 send 'Enter' to confirm login''',is_debug)
                ###0 May meet aerohive pruduct powerdown on vmwarw ---EOF, console command is EOF already
                ###1 If the cisco console server's port connect nothing, would stay'Escape character is '^]'.' when you send 'enter', cannot diff it from the normal way ,use timeout to mark it
                ###2 Aerohive product already login---#
                ###3 Aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
                ###4 Aerohive product login normally
                ###5 login switch via console(meet password) 
                nor_index = console_login_result.expect([pexpect.EOF, pexpect.TIMEOUT, prompt, 'Use the Aerohive.*no>:','Welcome to Aerohive Product.*login','[Pp]assword'], timeout=login_timeout)
                if nor_index == 0:
                    print 'The hostname %s not exist or in using, please check' % serialname
                    console_login_result.close(force=True)
                    return None
#                elif nor_index == 1:
#                    print '''TimeOut when send 'Enter' to confirm login or the hostname is no alive, fail in step 2'''
#                    console_login_result.close(force=True)
#                    return None
#                elif nor_index == 2:
#                    debug('Login successfully, can execute cli now',is_debug)
                elif nor_index == 3:
                    debug('Login successfully, but it is the first time to login after reset the device, send no to confirm not use default configure',is_debug)
                    console_login_result.sendline('no')
                    index=console_login_result.expect([pexpect.TIMEOUT,prompt],timeout=login_timeout)
                    if index == 0:
                        print 'Timeout when send no to confirm not use default configure'
                        console_login_result.close(force=True)
                        return None
                    elif index == 1:
                        debug('Login successfully, can execute cli now',is_debug)
                elif nor_index == 1:
                    ###retry retry_times times to type 'enter' to confirm login
                    nor_retry_times=retry_times
                    while nor_retry_index == 0:
                        nor_retry_num += 1
                        ### only use expect func 
                        debug('%s time retry begin' % nor_retry_num, is_debug)
                        ### v5 the first time is send ctrl+eco, the other is enter directly
                        if nor_retry_num == 1:
                            console_login_result.sendcontrol('e')
                            console_login_result.send('co')
                            console_login_result.expect('connecting...up.*')
                            console_login_result.sendline('')
                        else:
                            console_login_result.sendline('')
                        ###v4 miss prompt for already login 
                        nor_retry_index = console_login_result.expect([pexpect.TIMEOUT, 'Welcome to Aerohive Product.*login.*','[Pp]assword.*', prompt], timeout=login_timeout)
                        debug('%s time retry over' % nor_retry_num, is_debug)
                        ###add retry_num check here, when retry_num = retry_times, return none
                        if nor_retry_num == nor_retry_times:
                            print 'Retry %s times and still failed, close the expect child and return none' % nor_retry_times
                            console_login_result.close(force=True)
                            return None
                ### when index == 1 or 4 or 5 enter to retry mode
                elif nor_index ==4 or nor_index ==5:
                    debug('Normal login start',is_debug)
            
            ###v4 already login successfully
            ### add retry_index == 3 for already login bumped status
            if nor_index == 2 or retry_index == 3 or nor_retry_index == 3:
                debug('Login successfully, can execute cli now',is_debug)
                if nor_index == 2:
                    debug('Normal login successfully(already login)')
                if retry_index == 3:
                    debug('Bumped login successfully(already login)')
                if nor_retry_index == 3:
                    debug('Sendline not take effort, retry(already login)') 
            ###execute normal login status and this is new check
            ###AP
            if nor_index == 4 or retry_index == 1 or nor_retry_index == 1:
                debug('Welcome to Aerohive product', is_debug)
                console_login_result.sendline(user)
                debug('Step3 send user to confirm login', is_debug)
                ### 0 = time out
                ### 1 = login normally step 2(password)
                index = console_login_result.expect([pexpect.TIMEOUT, '[Pp]assword'], timeout=login_timeout)
                if index == 0:
                    print '''TimeOut when send user to confirm login, fail in step 3'''
                    console_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('''Step 4 send password to confirm login''',is_debug)
                    console_login_result.sendline(passwd)
                    ### 0 time out
                    ### 1 username or password incorrect
                    ### 2 login normally step 3(login successfully)
                    ### 3 login successfully but it's the first time to login after reset
                    index = console_login_result.expect([pexpect.TIMEOUT, 'login', prompt,'Use the Aerohive.*no>:'],timeout=login_timeout)
                    if index == 0:
                        print '''TimeOut when send password to confirm login, fail in step 4''' 
                        console_login_result.close(force=True)
                        return None
                    elif index == 1:
                        print '''Username or password is incorrect, please check, fail in step 4''' 
                        console_login_result.close(force=True)
                        return None                        
                    elif index == 2:
                        debug('''login Aerohive product successfully, can execute cli now ''',is_debug)
                    elif index == 3:
                        debug('Login successfully, but it is the first time to login after reset the device, send no to confirm not use default configure',is_debug)
                        console_login_result.sendline('no')
                        index=console_login_result.expect([pexpect.TIMEOUT,prompt],timeout=login_timeout)
                        if index == 0:
                            print 'Timeout when send no to confirm not use default configure'
                            console_login_result.close(force=True)
                            return None
                        elif index == 1:
                            debug('Login successfully, can execute cli now',is_debug)
                ###login sw via console
            if nor_index == 5 or retry_index == 2 or nor_retry_index == 2:
                debug('Welcome to general network product', is_debug)
                console_login_result.sendline(passwd)
                index=console_login_result.expect([pexpect.TIMEOUT,prompt,'[Pp]assword'],timeout=login_timeout)
                if index == 0:
                    print 'Timeout when send no to confirm not use default configure'
                    console_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('Login successfully, can execute cli now',is_debug)
                elif index == 2:
                    print 'Incorrect password, please check'
                    console_login_result.close(force=True)
                    return None                        
                                               
        return console_login_result
    
    def execute_command(self,cli,cli_expect,timeout,spawn_child):
        is_debug=self.is_debug
        console_cli_result=spawn_child
        console_cli_result.sendline(cli)
        ###2 may meet some display command cannot show all the parameters,need send '' to continue
        index=console_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:','-- More --'], timeout=timeout)
        if index == 0:
            print '''TimeOut when execute CLI, fail in Execute CLI parter'''
            console_cli_result.close(force=True)
            return None
        elif index == 1:
            debug('%s' % cli,is_debug)
        elif index == 2:
            debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
            ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
            while index:
                ###only need send ' ' only, no need 'enter'
                console_cli_result.send(' ')
                index=console_cli_result.expect([cli_expect,'--More--'], timeout=timeout)
        elif index == 3:
            debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
            while index:
                ###only need send ' ' only, no need 'enter'
                console_cli_result.send(' ')
                index=console_cli_result.expect([cli_expect,'More:'], timeout=timeout)
        elif index == 4:
            debug('H3C product, cannot show all in a page, send blank to continue',is_debug)
            while index:
                ###only need send ' ' only, no need 'enter'
                console_cli_result.send(' ')
                index=console_cli_result.expect([cli_expect,'-- More --'], timeout=timeout)             
        return console_cli_result
    
    def execute_command_via_tuple_list(self,cli_tuple_list,timeout,spawn_child,ctrl_index_list=[]):
        is_debug=self.is_debug
        console_cli_result=spawn_child
        if ctrl_index_list:
            for cli,cli_expect in cli_tuple_list:
                if cli_tuple_list.index((cli,cli_expect)) in ctrl_index_list:
                    debug('Send ctrl command',is_debug)
                    cli=re.sub(r'ctrl-','',cli)
                    debug('Send command is ctrl-%s' % cli, is_debug)
                    console_cli_result.sendcontrol(cli)
                else:
                    debug('Send normal command',is_debug)
                    console_cli_result.sendline(cli)
                ###2 may meet some display command cannot show all the parameters,need send '' to continue
                index=console_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:','-- More --'], timeout=timeout)
                if index == 0:
                    print '''TimeOut when execute CLI, fail in Execute CLI parter'''
                    console_cli_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli,is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
                    ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
                    while index:
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        console_cli_result.send(' ')
                        index=console_cli_result.expect([cli_expect,'--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        console_cli_result.send(' ')
                        index=console_cli_result.expect([cli_expect,'More:'], timeout=timeout)
                elif index == 4:
                    debug('H3C product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        console_cli_result.send(' ')
                        index=console_cli_result.expect([cli_expect,'-- More --'], timeout=timeout)      
        else:
            for cli,cli_expect in cli_tuple_list:
                console_cli_result.sendline(cli)
                ###2 may meet some display command cannot show all the parameters,need send '' to continue
                index=console_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:','-- More --'], timeout=timeout)
                if index == 0:
                    print '''TimeOut when execute CLI, fail in Execute CLI parter'''
                    console_cli_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli,is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
                    ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
                    while index:
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        console_cli_result.send(' ')
                        index=console_cli_result.expect([cli_expect,'--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        console_cli_result.send(' ')
                        index=console_cli_result.expect([cli_expect,'More:'], timeout=timeout)
                elif index == 4:
                    debug('H3C product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        console_cli_result.send(' ')
                        index=console_cli_result.expect([cli_expect,'-- More --'], timeout=timeout)               
        return console_cli_result
    
    def logout(self,spawn_child,logout_timeout=5):
        console_logout_result=spawn_child
        ###send control+d may cause reset enter to bootload mode, so comment these part
#        debug('....................Quit login status....................', self.is_debug)
#        console_logout_result.sendcontrol('d')
#        ###send enter to confirm dell sw mode or AP mode 
#        console_logout_result.sendline('')
#        ### 1 AP mode
#        ### 2 switch mode
#        index=console_logout_result.expect([pexpect.TIMEOUT,'login:','#'],timeout=logout_timeout)
#        if index == 0:
#            print '''TimeOut when send ctrl+d to logout noraml login status'''
#            console_logout_result.close(force=True)
#            return None
#        elif index == 1:
#            debug('Logout AP successfully', self.is_debug)
#        elif index == 2:
#            debug('Switch mode, no need logout AP', self.is_debug)
        debug('....................Free console port....................', self.is_debug)
        console_logout_result.sendcontrol('e')
        console_logout_result.send('c.')
        index=console_logout_result.expect([pexpect.TIMEOUT,'disconnect'],timeout=logout_timeout)
        if index == 0:
            print '''TimeOut when send ctrl+ec. to to logout console prompt status'''
            console_logout_result.close(force=True)
            return None
        elif index == 1:
            debug('Free %s successfully' % (self.ip), self.is_debug)       
        return console_logout_result

def console_execute_cli(ip,serialname,user,passwd,cli_list,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd,retry_times):
    ###Is_shell is not used in this func
    timeout=int(timeout)
    retry_times=int(retry_times)
    ###In linux, no matter how many '/' between father folder and child folder
    absolute_logfile=logdir+'/'+logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    debug('Host name is as below', is_debug)
    debug(ip,is_debug)
    debug('Serial name is as below', is_debug)
    debug(serialname,is_debug)
    ###set class
    console=console_host(ip, serialname, user, passwd, is_debug, absolute_logfile,prompt)
    ###login
    ###v5 add retry_times for login
    console_host_login=console.login(retry_times)
    ###execute cli
    if console_host_login:
        cli_tuple_list=[]
        ###V4 Add special check on show log for confusion code 
        log_regex=re.compile('^show log.*')
        reset_regex=re.compile('^reset config$')
        ###V6
        reset_boot_regex=re.compile('^reset config bootstrap$')
        reboot_regex=re.compile('^reboot$')
        ### Means save config tftp:.* current or save config tftp:.* bootstrap
        save_config_regex=re.compile('^save config tftp:.* (current|bootstrap)')
        save_image_regex=re.compile('^save image tftp:.*')
        ###shell use other solution, may meet incorrect status
        shell_regex=re.compile('^_shell$')
        #v6 add support more general status
        exit_regex=re.compile('^exit$')
        enble_regex=re.compile('^enable$')
        country_regex=re.compile('^boot-param country-code.*')
        ctrl_regex=re.compile('ctrl-.*')
        ###collect ctrl command index and instead sendline to sendctrl when meet the index
        ctrl_index_list=[]
        ctrl_index=0
        for cli in cli_list:
            ### V4 Add special check on show log for confusion code 
            ### add enter for show log.* to forbin confuse code
            if log_regex.search(cli):
                cli_tuple_list.append((cli,'\w+.*'))
                ### v4 this should expect prompt, other status should be included in execute except
                cli_tuple_list.append(('',prompt))
                ctrl_index=ctrl_index + 2
            ### be careful the speacial chara such ?, need add \ before it(raw mode cannot transmit ? and $)
            #pass
            ###V6 need to reboot
            elif reset_boot_regex.search(cli):
                cli_tuple_list.append((cli,r'bootstrap configuration.*'))
                cli_tuple_list.append(('y',prompt))
                ctrl_index=ctrl_index + 2
            ###v6 reset waite to login
            elif reset_regex.search(cli):
                cli_tuple_list.append((cli,r'bootstrap configuration.*'))
                ###V6 modify rebooting to prompt to forbin enter to bootload
                cli_tuple_list.append(('y',prompt))
                ###V6 for waite to login
                cli_tuple_list.append(('','login:'))
                ctrl_index=ctrl_index + 3
            #pass
            elif reboot_regex.search(cli):
                cli_tuple_list.append((cli,r'Do you really want to reboot.*'))
                ###V6 modify rebooting to prompt to forbin enter to bootload
                cli_tuple_list.append(('y',prompt))
                ###V6 for waite to login
                cli_tuple_list.append(('','login:'))
                ctrl_index=ctrl_index + 3               
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
            #v6 add support more general status
            elif exit_regex.search(cli):
                #v6 add support more general status
#                cli_tuple_list.append((cli,'Welcome back to CLI console!.*#'))
                cli_tuple_list.append((cli,prompt))                
                ctrl_index=ctrl_index + 1          
            elif enble_regex.search(cli):
                cli_tuple_list.append((cli,'[Pp]assword'))
                cli_tuple_list.append((passwd,prompt))
                ctrl_index=ctrl_index + 1               
            elif country_regex.search(cli):
                ###beta modefy the expect to match the special status
                cli_tuple_list.append((cli,'To apply radio setting.*it now\?'))
                cli_tuple_list.append(('y',prompt))
                ###V6 for waite to login
                cli_tuple_list.append(('','login:'))
                ###V6 modify 2 to 3
                ctrl_index=ctrl_index + 3
                
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
        console_host_execute=console.execute_command_via_tuple_list(cli_tuple_list, timeout, console_host_login,ctrl_index_list)
    else:
        print 'Console login failed'
        return None
    ###logout
    console_host_logout=console.logout(console_host_execute)
    return console_host_logout

parse = argparse.ArgumentParser(description='Console host to execute CLI')
parse.add_argument('-d', '--destination', required=False, default='localhost', dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-e', '--serialname', required=True, default=None, dest='serialname',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')

parse.add_argument('-m', '--prompt', required=False, default='AH.*#', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=5, type=int, dest='timeout',
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

parse.add_argument('-i', '--interface', required=False, default='', dest='serial',
                    help='Serial number')

parse.add_argument('-n', '--nowaite', required=False, default=False, action='store_true', dest='is_waite',
                    help='enable waite mode')

parse.add_argument('-f', '--file', required=False, default=False, dest='configfilepath',
                    help='The path of configurefile')

parse.add_argument('-k', '--retry', required=False, default=18, type= int, dest='retry_times',
                    help='How many times you want to retry when the login step is failed')

def main():
    args = parse.parse_args() 
    ip=args.desip
    user=args.user
    passwd=args.passwd
    prompt=args.prompt
    ###v4 add \ for $
    prompt=re.sub('\$','\\$',prompt)
    timeout=args.timeout
    logdir=args.logdir
    logfile=args.logfile
    cli_list=args.cli_list
    is_debug=args.is_debug
    shellpasswd=args.shellpasswd
    is_shell=args.is_shell
    serialname=args.serialname
    config_file_path=args.configfilepath
    retry_times=args.retry_times
    ###check is config_file_path is null, if yes, use cli_list,if no, use config_file_path
    ### v5 add support both exist -v and -f
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
        ###v9 add a flag to check if v_index is the first time more than f_index
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
    else:
        execute_cli_list=cli_list
    debug('Execute cli list is as below...', is_debug) 
    debug(execute_cli_list,is_debug)
    try:
        console_result=console_execute_cli(ip,serialname,user,passwd,execute_cli_list,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd,retry_times)
    except Exception, e:
        print str(e)
    else:
        return console_result
            
if __name__=='__main__':
    console_result=main()
    if console_result:
        console_result.close()
        print 'Console successfully, exit 0'
        sys.exit(0)
    else:
        print 'Console failed, exit 1'
        sys.exit(1)
