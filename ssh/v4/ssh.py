#!/usr/bin/python
# Filename: ssh.py
# Function: ssh target execute cli
# coding:utf-8
# Author: Well
# Example command:ssh.py -d ip -u user -p password -m prompt -o timeout -l logdir -z logfile -v "show run" -v "show version"
import pexpect, sys, argparse,re

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage
        
class ssh_host:
    def __init__(self, ip, user, passwd, port=22, is_debug=False, absolute_logfile='', prompt='[$#>]'):
        self.ip=ip
        self.user=user
        self.passwd=passwd
        self.port=port
        self.is_debug=is_debug
        self.absolute_logfile=absolute_logfile
        self.prompt=prompt
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open=open(absolute_logfile, mode = 'w')
        print 'SSH %s process start, init parameters............' % ip
    
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
        print 'SSH %s process over.' % self.ip

    def login(self,login_timeout=10):
        ip=self.ip
        user=self.user
        passwd=self.passwd
        port=self.port
        prompt=self.prompt
        is_debug=self.is_debug
        ssh_login_command='ssh %s@%s -p %s' % (user, ip, port)
        debug('''SSH host via IP''', is_debug)
        debug('''SSH login command is "%s"''' % ssh_login_command, is_debug)
        debug('Step1 send ssh command to login host', is_debug)
        ssh_login_result=pexpect.spawn(ssh_login_command)
        ###Judge if the log file has been set, if yes, redirect the log to file
        ###else to stdout
        if self.absolute_logfile == './stdout':
            #ssh_login_result.logfile=sys.stdout
            #ssh_login_result.logfile_send=sys.stdout
            ssh_login_result.logfile_read=sys.stdout
        else:
            #ssh_login_result.logfile=self.absolute_logfile_open
            #ssh_login_result.logfile_send=self.absolute_logfile_open
            ssh_login_result.logfile_read=self.absolute_logfile_open
        ###0 timeout
        ###1 PC nerwork is abnormal
        ###2 Aerohive produce normally login
        ###3 General network product normally login
        index = ssh_login_result.expect([pexpect.TIMEOUT, 'Are you sure you want to continue connecting .*\?', '[Pp]assword'], timeout=login_timeout)
        if index == 0:
            print 'SSH host timeout, please confirm you can reach the host'
            ssh_login_result.close(force=True)
            return None
        elif index == 1:
            debug('The host is not in known host list, need send yes to confirm login',is_debug)
            ssh_login_result.sendline('yes')
            index=ssh_login_result.expect([pexpect.TIMEOUT, '[Pp]assword:'], timeout=login_timeout)
            if index == 0:
                print '''TimeOut when send 'yes' confirm authenticity to login'''
                ssh_login_result.close(force=True)
                return None
            elif index == 1:
                debug('Add host to known host list successfully, and meet password part')
        elif index == 2:
            debug('Add host to known host list successfully, and meet password part')
        else:
            print '''Unknown error'''
            ssh_login_result.close(force=True)
            return None 
        ###unknow host ---yes---password
        ###know host---password
        ssh_login_result.sendline(passwd)
        ###Use global variable need add class name  'ssh_host.login_prompt'
        ###version 2 modify prompt to 'Last.*root@hztb1.*'(win) for forbin login prompt influence(#$>~^ and so on)
        ### version 3 modify prompt to 'Last.*root@.*' for br vpc(root@br2-vpc) 
        index=ssh_login_result.expect([pexpect.TIMEOUT,'[Pp]assword','Last.*root@.*','Aerohive Networks .*#'], timeout=20)
        if index==0:
            print '''TimeOut when send password to login Host'''
            ssh_login_result.close(force=True)
            return None
        elif index==1:
            print '''Incorrect username or password, please confirm'''
            ssh_login_result.close(force=True)
            return None
        
        
        elif index==2:
            debug('Login windows/linux clients successfully, can execute cli now')
        elif index==3:
            debug('Login Aerohive products successfully, can execute cli now')
        return ssh_login_result
    
    def execute_command(self,cli,cli_expect,timeout,spawn_child):
        is_debug=self.is_debug
        ssh_login_result=spawn_child
        ssh_login_result.sendline(cli)
        ###2 may meet some display command cannot show all the parameters,need send '' to continue
        index=ssh_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:','-- More --'], timeout=timeout)
        if index == 0:
            print '''TimeOut when execute CLI, fail in Execute CLI parter'''
            ssh_login_result.close(force=True)
            return None
        elif index == 1:
            debug('%s' % cli,is_debug)
        elif index == 2:
            debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
            ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
            while index:
                ###only need send ' ' only, no need 'enter'
                ssh_login_result.send(' ')
                index=ssh_login_result.expect([cli_expect,'--More--'], timeout=timeout)
        elif index == 3:
            debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
            while index:
                ###only need send ' ' only, no need 'enter'
                ssh_login_result.send(' ')
                index=ssh_login_result.expect([cli_expect,'More:'], timeout=timeout)
        elif index == 4:
            debug('H3C product, cannot show all in a page, send blank to continue',is_debug)
            while index:
                ###only need send ' ' only, no need 'enter'
                ssh_login_result.send(' ')
                index=ssh_login_result.expect([cli_expect,'-- More --'], timeout=timeout)                    
        return ssh_login_result
    
    def execute_command_via_tuple_list(self,cli_tuple_list,timeout,spawn_child,ctrl_index_list=[]):
        is_debug=self.is_debug
        ssh_login_result=spawn_child
        if ctrl_index_list:
            for cli,cli_expect in cli_tuple_list:
                if cli_tuple_list.index((cli,cli_expect)) in ctrl_index_list:
                    debug('Send ctrl command',is_debug)
                    cli=re.sub(r'ctrl-','',cli)
                    debug('Send command is ctrl-%s' % cli, is_debug)
                    ssh_login_result.sendcontrol(cli)
                else:
                    debug('Send normal command',is_debug)
                    ssh_login_result.sendline(cli)
                ###2 may meet some display command cannot show all the parameters,need send '' to continue
                index=ssh_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:'], timeout=timeout)
                if index == 0:
                    print '''TimeOut when execute CLI, fail in Execute CLI parter'''
                    ssh_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli,is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
                    ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
                    while index:
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        ssh_login_result.send(' ')
                        index=ssh_login_result.expect([cli_expect,'--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        ssh_login_result.send(' ')
                        index=ssh_login_result.expect([cli_expect,'More:'], timeout=timeout)   
        else:
            for cli,cli_expect in cli_tuple_list:
                ssh_login_result.sendline(cli)
                ###2 may meet some display command cannot show all the parameters,need send '' to continue
                index=ssh_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--','More:'], timeout=timeout)
                if index == 0:
                    print '''TimeOut when execute CLI, fail in Execute CLI parter'''
                    ssh_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli,is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue',is_debug)
                    ###while '--more--' continue, until meet 'cil_expect' break the loop, Aerohive product
                    while index:
                        ###only need send ' ' only, no need 'enter', so use send instead of sendline
                        ssh_login_result.send(' ')
                        index=ssh_login_result.expect([cli_expect,'--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue',is_debug)
                    while index:
                        ###only need send ' ' only, no need 'enter'
                        ssh_login_result.send(' ')
                        index=ssh_login_result.expect([cli_expect,'More:'], timeout=timeout)            
        return ssh_login_result
    
    ###add retry for logout
    def logout(self,spawn_child,logout_timeout=5):
        is_debug=self.is_debug
        ssh_logout_result=spawn_child
        debug('....................Quit login status....................',self.is_debug)
        ssh_logout_result.sendcontrol('d')
        index=ssh_logout_result.expect([pexpect.TIMEOUT,'Connection to .* closed'],timeout=logout_timeout)
        if index== 0:
            logout_retry_index = 0
            logout_retry_times = 2
            logout_retry_num =0
            while logout_retry_index == 0:
                logout_retry_num += 1
                ### only use expect func for forbin enter bottload mode
                debug('%s time retry begin' % logout_retry_num, is_debug)
                ssh_logout_result.sendcontrol('d')
                logout_retry_index = ssh_logout_result.expect([pexpect.TIMEOUT,'Connection to .* closed'],timeout=logout_timeout)
                debug('%s time retry over' % logout_retry_num, is_debug)
                ###add retry_num check here, when retry_num = retry_times, return none
                if logout_retry_num == logout_retry_times:
                    print 'Retry %s times and logout still failed, return none' % logout_retry_times
                    ssh_logout_result.close(force=True)
                    return None
        elif index == 1:
            pass
        debug('Free %s successfully' % self.ip, self.is_debug)
        return ssh_logout_result

def ssh_execute_cli(ip,user,passwd,cli_list,port,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd):
    ###Is_shell is not used in this func
    timeout=int(timeout)
    ###In linux, no matter how many '/' between father folder and child folder
    absolute_logfile=logdir+'/'+logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    ###set class
    ssh=ssh_host(ip, user, passwd, port, is_debug, absolute_logfile,prompt)
    ###login
    ###add timeout parameters to login function
    ssh_host_login=ssh.login(timeout)
    ###execute cli
    if ssh_host_login:
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
            ### add ~ for win clients default
            elif ctrl_regex.search(cli):
                cli_tuple_list.append((cli,'%s|~' % prompt))
                ctrl_index_list.append(ctrl_index)
            else:
                cli_tuple_list.append((cli,'%s|~' % prompt))
                ctrl_index=ctrl_index + 1
        debug('cli_tuple_list is as below',is_debug)
        debug(cli_tuple_list,is_debug)
        debug('ctrl_index_list is as below',is_debug)
        debug(ctrl_index_list,is_debug)                                       
        ssh_host_execute=ssh.execute_command_via_tuple_list(cli_tuple_list, timeout, ssh_host_login,ctrl_index_list)
    else:
        print 'SSH login failed'
        return None
    
    ###logout
    ###check the if has port port, if yes, use ssh.logout_via_port(), else, use ssh.logout_via_ip()
#    ssh_host_logout=ssh.logout(ssh_host_execute,timeout)
    ### timeout from input may too long for logout retry, so use the deafult value 5s
    ### modify based linux laptop modify wpa cli and logout(may match win prompt ~ firstly and send control+d too early)
    ssh_host_logout=ssh.logout(ssh_host_execute)
    return ssh_host_logout

parse = argparse.ArgumentParser(description='SSH host to execute CLI')
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')

parse.add_argument('-m', '--prompt', required=False, default='AH.*#', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=10, type=int, dest='timeout',
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

parse.add_argument('-i', '--interface', required=False, default=22, type=int, dest='port',
                    help='ssh port')

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
    port=args.port
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
        ssh_result=ssh_execute_cli(ip,user,passwd,execute_cli_list,port,timeout,prompt,logdir,logfile,is_debug,is_shell,shellpasswd)
    except Exception, e:
        print str(e)
    else:
        return ssh_result
            
if __name__=='__main__':
    ssh_result=main()
    if ssh_result:
        ssh_result.close()
        print 'SSH successfully, exit 0'
        sys.exit(0)
    else:
        print 'SSH failed, exit 1'
        sys.exit(1)