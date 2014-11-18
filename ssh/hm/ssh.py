#!/usr/bin/python
# Filename: ssh.py
# Function: ssh target execute cli
# coding:utf-8
# Author: Will
# Example command:ssh.py -d 10.155.30.65 -w 5 -c 2 -v '_test presence send-packet 200'
import pexpect, sys, argparse, re, time

def sleep (mytime=1):
    time.sleep(mytime)

def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print 'DEBUG',
        print mesage
        
class ssh_host:

    def __init__(self, ip, user, passwd, port=22, is_debug=False, absolute_logfile='', prompt='[$#>]', wait_time=0):
        self.ip = ip
        self.user = user
        self.passwd = passwd
        self.port = port
        self.is_debug = is_debug
        self.absolute_logfile = absolute_logfile
        self.prompt = prompt
        self.wait_time = wait_time
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open = open(absolute_logfile, mode='w')
        print 'SSH %s process start, init parameters............' % ip
    
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open.close()
            absolute_logfile = self.absolute_logfile
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile = absolute_logfile_open.read()
            correct_logfile = re.sub(' {28}|\r', '', originate_logfile)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.write(correct_logfile)            
        print 'SSH %s process over.' % self.ip
    def login(self, login_timeout=10):
        ip = self.ip
        user = self.user
        passwd = self.passwd
        port = self.port
        prompt = self.prompt
        is_debug = self.is_debug
        ssh_login_command = 'ssh %s@%s -p %s' % (user, ip, port)
        debug('''SSH host via IP''', is_debug)
        debug('''SSH login command is "%s"''' % ssh_login_command, is_debug)
        debug('Step1 send ssh command to login host', is_debug)
        ssh_login_result = pexpect.spawn(ssh_login_command)
        if self.absolute_logfile == './stdout':
            ssh_login_result.logfile_read = sys.stdout
        else:
            ssh_login_result.logfile_read = self.absolute_logfile_open
        index = ssh_login_result.expect([pexpect.TIMEOUT, 'Are you sure you want to continue connecting .*\?', '[Pp]assword', prompt], timeout=login_timeout)
        if index == 0:
            print 'SSH host timeout, please confirm you can reach the host'
            print 'before is %s' % ssh_login_result.before
            print 'after is %s' % ssh_login_result.after
            ssh_login_result.close(force=True)
            return None
        elif index == 1:
            debug('The host is not in known host list, need send yes to confirm login', is_debug)
            ssh_login_result.sendline('yes')
            index = ssh_login_result.expect([pexpect.TIMEOUT, '[Pp]assword:'], timeout=login_timeout)
            if index == 0:
                print '''TimeOut when send 'yes' confirm authenticity to login'''
                print 'before is %s' % ssh_login_result.before
                print 'after is %s' % ssh_login_result.after
                ssh_login_result.close(force=True)
                return None
            elif index == 1:
                debug('Add host to known host list successfully, and meet password part', is_debug)
        elif index == 2:
            debug('Add host to known host list successfully, and meet password part', is_debug)
        elif index == 3:
            debug('Already login, can execute CLI now', is_debug)
            return ssh_login_result
        else:
            print '''Unknown error'''
            print 'before is %s' % ssh_login_result.before
            print 'after is %s' % ssh_login_result.after
            ssh_login_result.close(force=True)
            return None 
        ssh_login_result.sendline(passwd)
        ###Use global variable need add class name  'ssh_host.login_prompt'
        ###version 2 modify prompt to 'Last.*root@hztb1.*'(win) for forbin login prompt influence(#$>~^ and so on)
        ### version 3 modify prompt to 'Last.*root@.*' for br vpc(root@br2-vpc) 
        ### v5 add support login via user name logger modify root to (root|logger)
        ### v9 remove last login .* for login self
        ### v9 add prompt for general product
        index = ssh_login_result.expect([pexpect.TIMEOUT, '[Pp]assword', '(root|logger)@.*', 'Aerohive Networks .*#', prompt], timeout=login_timeout)
        if index == 0:
            print '''TimeOut when send password to login Host'''
            print 'before is %s' % ssh_login_result.before
            print 'after is %s' % ssh_login_result.after
            ssh_login_result.close(force=True)
            return None
        elif index == 1:
            print '''Incorrect username or password, please confirm'''
            print 'before is %s' % ssh_login_result.before
            print 'after is %s' % ssh_login_result.after
            ssh_login_result.close(force=True)
            return None
        elif index == 2:
            debug('Login windows/linux clients successfully, can execute cli now')
        elif index == 3:
            debug('Login Aerohive products successfully, can execute cli now')
        elif index == 4:
            debug('Login general products successfully, can execute cli now')
        return ssh_login_result
    
    def execute_command_via_tuple_list(self, cli_tuple_list, timeout, spawn_child, ctrl_index_list=[]):
        is_debug = self.is_debug
        ###v10 add wait time
        wait_time = self.wait_time
        ssh_login_result = spawn_child
        if ctrl_index_list:
            for cli, cli_expect in cli_tuple_list:
                if cli_tuple_list.index((cli, cli_expect)) in ctrl_index_list:
                    debug('Send ctrl command', is_debug)
                    cli = re.sub(r'ctrl-', '', cli)
                    debug('Send command is ctrl-%s' % cli, is_debug)
                    ssh_login_result.sendcontrol(cli)
                else:
                    debug('Send normal command', is_debug)
                    ssh_login_result.sendline(cli)
                index = ssh_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--', 'More:'], timeout=timeout)
                if index == 0:
                    print '''TimeOut when execute CLI, fail in Execute CLI parter'''
                    print 'before is %s' % ssh_login_result.before
                    print 'after is %s' % ssh_login_result.after
                    ssh_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli, is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue', is_debug)
                    more_index = 0                    
                    while index:
                        more_index += 1
                        ssh_login_result.sendline('')
                        index = ssh_login_result.expect([cli_expect, '--More--'], timeout=timeout)
                    debug('Meet more %s times' % more_index, is_debug)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue', is_debug)
                    while index:
                        ssh_login_result.send(' ')
                        index = ssh_login_result.expect([cli_expect, 'More:'], timeout=timeout)
                debug('Sleep wait time %s to execute next cli' % wait_time, is_debug)
                sleep(wait_time)     
        else:
            for cli, cli_expect in cli_tuple_list:
                ssh_login_result.sendline(cli)
                index = ssh_login_result.expect([pexpect.TIMEOUT, cli_expect, '--More--', 'More:'], timeout=timeout)
                if index == 0:
                    print '''TimeOut when execute CLI, fail in Execute CLI parter'''
                    print 'before is %s' % ssh_login_result.before
                    print 'after is %s' % ssh_login_result.after
                    ssh_login_result.close(force=True)
                    return None
                elif index == 1:
                    debug('%s' % cli, is_debug)
                elif index == 2:
                    debug('Aerohive product, cannot show all in a page, send blank to continue', is_debug)
                    while index:
                        ssh_login_result.send(' ')
                        index = ssh_login_result.expect([cli_expect, '--More--'], timeout=timeout)
                elif index == 3:
                    debug('Dell product, cannot show all in a page, send blank to continue', is_debug)
                    while index:
                        ssh_login_result.send(' ')
                        index = ssh_login_result.expect([cli_expect, 'More:'], timeout=timeout)
                debug('Sleep wait time %s to execute next cli' % wait_time, is_debug)
                sleep(wait_time)              
        return ssh_login_result
    
    def logout(self, spawn_child, logout_timeout=2):
        is_debug = self.is_debug
        ssh_logout_result = spawn_child
        debug('....................Quit login status....................', self.is_debug)
        ssh_logout_result.sendcontrol('d')
        index = ssh_logout_result.expect([pexpect.TIMEOUT, 'Connection to .* closed'], timeout=logout_timeout)
        if index == 0:
            logout_retry_index = 0
            logout_retry_times = 2
            logout_retry_num = 0
            while logout_retry_index == 0:
                logout_retry_num += 1
                debug('%s time retry begin' % logout_retry_num, is_debug)
                ssh_logout_result.sendcontrol('d')
                logout_retry_index = ssh_logout_result.expect([pexpect.TIMEOUT, 'Connection to .* closed'], timeout=logout_timeout)
                debug('%s time retry over' % logout_retry_num, is_debug)
                if logout_retry_num == logout_retry_times:
                    print 'Retry %s times and logout still failed, return none' % logout_retry_times
                    print 'before is %s' % ssh_logout_result.before
                    print 'after is %s' % ssh_logout_result.after
                    ssh_logout_result.close(force=True)
                    return None
        elif index == 1:
            pass
        debug('Free %s successfully' % self.ip, self.is_debug)
        return ssh_logout_result
def ssh_execute_cli(ip, user, passwd, cli_list, port, timeout, prompt, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, count):
    timeout = int(timeout)
    wait_time = float(wait_time)
    count=int(count)
    absolute_logfile = logdir + '/' + logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    ssh = ssh_host(ip, user, passwd, port, is_debug, absolute_logfile, prompt, wait_time)
    ssh_host_login = ssh.login(timeout)
    if ssh_host_login:
        cli_tuple_list = []
        reset_regex = re.compile('^reset config$')
        reboot_regex = re.compile('^reboot$')
        save_config_regex = re.compile('^save config tftp:.* (current|bootstrap)')
        save_image_regex = re.compile('^save image tftp:.*')
        shell_regex = re.compile('^_shell$')
        exit_regex = re.compile('^exit$')
        enble_regex = re.compile('^enable$')
        country_regex = re.compile('^boot-param country-code.*')
        ctrl_regex = re.compile('ctrl-.*')
        ctrl_index_list = []
        ctrl_index = 0
        for cli in cli_list:
            if reset_regex.search(cli):
                cli_tuple_list.append((cli, r'bootstrap configuration.*'))
                cli_tuple_list.append(('y', 'rebooting'))
                ctrl_index = ctrl_index + 2
            #pass
            elif reboot_regex.search(cli):
                cli_tuple_list.append((cli, r'Do you really want to reboot.*'))
                cli_tuple_list.append(('y', r'rebooting'))
                ctrl_index = ctrl_index + 2               
            #pass , select prompt can goto next is this step is failed
            elif save_config_regex.search(cli):
                cli_tuple_list.append((cli, r'configuration.*'))
                cli_tuple_list.append(('y', prompt))
                ctrl_index = ctrl_index + 2
            #pass , select prompt can goto next is this step is failed
            elif save_image_regex.search(cli):
                cli_tuple_list.append((cli, r'update image.*'))
                cli_tuple_list.append(('y', prompt))
                ctrl_index = ctrl_index + 2
            #pass...may consider the incorrect password status
            elif shell_regex.search(cli):
                cli_tuple_list.append((cli, '[Pp]assword:'))
                cli_tuple_list.append((shellpasswd, prompt))
                ctrl_index = ctrl_index + 2
            #V6 add support general status
            elif exit_regex.search(cli):
                cli_tuple_list.append((cli, prompt))
                ctrl_index = ctrl_index + 1          
            elif enble_regex.search(cli):
                cli_tuple_list.append((cli, '[Pp]assword'))
                cli_tuple_list.append((passwd, prompt))
                ctrl_index = ctrl_index + 1               
            elif country_regex.search(cli):
                cli_tuple_list.append((cli, 'To apply radio setting for the new country code.*'))
                cli_tuple_list.append(('y', prompt))
                ctrl_index = ctrl_index + 2
            elif ctrl_regex.search(cli):
                cli_tuple_list.append((cli, '%s|root@.*~.*\$' % prompt))
                ctrl_index_list.append(ctrl_index)
            else:
                cli_tuple_list.append((cli, '%s|root@.*~.*\$' % prompt))
                ctrl_index = ctrl_index + 1
        debug('cli_tuple_list is as below', is_debug)
        debug(cli_tuple_list, is_debug)
        debug('ctrl_index_list is as below', is_debug)
        debug(ctrl_index_list, is_debug)
        ###hm
        if count > 0:
            for i in range(count):
                ssh_host_execute = ssh.execute_command_via_tuple_list(cli_tuple_list, timeout, ssh_host_login, ctrl_index_list)
                print '%s times over' % (i+1)
        elif count == 0:
            i=1
            while 1:
                ssh_host_execute = ssh.execute_command_via_tuple_list(cli_tuple_list, timeout, ssh_host_login, ctrl_index_list)
                print '%s times over' % (i+1)
                i+=1
        else:                                        
            print 'count should not be negative num,pls check'
            ssh_host_login.close(force=True)
    else:
        print 'SSH login failed'
        return None
    ssh_host_logout = ssh.logout(ssh_host_execute)
    return ssh_host_logout

parse = argparse.ArgumentParser(description='SSH host to execute CLI')
parse.add_argument('-d', '--destination', required=True, default=None, dest='desip',
                    help='Destination Host Blade Server IP')

parse.add_argument('-u', '--user', required=False, default='admin', dest='user',
                    help='Login Name')

parse.add_argument('-p', '--password', required=False, default='aerohive', dest='passwd',
                    help='Login Password')
###v8 modify the prompt to AH-\w+#.*
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

parse.add_argument('-debug', '--debug', required=False, default=False, action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False, action='store_true', dest='is_shell',
                    help='enable shell mode')

parse.add_argument('-i', '--interface', required=False, default=22, type=int, dest='port',
                    help='ssh port')

parse.add_argument('-n', '--nowaite', required=False, default=False, action='store_true', dest='is_waite',
                    help='enable waite mode')

parse.add_argument('-f', '--file', required=False, default=False, dest='configfilepath',
                    help='The path of configurefile')

parse.add_argument('-w', '--wait', required=False, default=0, type=float , dest='wait_time',
                    help='wait time between the current cli and next cli')
#hm
parse.add_argument('-c', '--count', required=False, default=1, type=int, dest='count',
                    help='the count you want to repeat the command, only support one -v only')

def main():
    args = parse.parse_args() 
    ip = args.desip
    user = args.user
    passwd = args.passwd
    prompt = args.prompt
    timeout = args.timeout
    logdir = args.logdir
    logfile = args.logfile.strip()
    cli_list = args.cli_list
    is_debug = args.is_debug
    shellpasswd = args.shellpasswd
    is_shell = args.is_shell
    port = args.port
    config_file_path = args.configfilepath
    wait_time = args.wait_time
###hm
    count = args.count
    if config_file_path:
        debug('config file flag is set, special process the cli_list')
        para_list = sys.argv
        v_argv_list = []
        f_argv_list = []
        para_index = 0
        for para in para_list:
            if para == '-v':
                v_argv_list.append(para_index)
            if para == '-f':
                f_argv_list.append(para_index)
            para_index += 1
        debug('para_list is as below', is_debug)
        debug(para_list, is_debug)
        debug('v_command_index_list is as below', is_debug)
        debug(v_argv_list, is_debug)
        debug('f_command_index_list is as below', is_debug)
        debug(f_argv_list, is_debug)
        try:
            with open(config_file_path, mode='r') as config_file_open:
                read_cli_list = config_file_open.readlines()
            file_cli_list = []
            for cli in read_cli_list:
                file_cli_list.append(re.sub('[\r\n]', '', cli))   
        except IOError:
            print 'Your file path %s is wrong or the file is not exist' % config_file_path
        else:
            debug('Open configure file successfully', is_debug)
        execute_cli_list = []
        if v_argv_list:
            debug('Both -v -f flag exist', is_debug)
            is_first_more = 1
            for v_index in v_argv_list:
                if v_index < f_argv_list[0]:
                    execute_cli_list.append(para_list[v_index + 1])
                else:
                    if is_first_more:
                        execute_cli_list.extend(file_cli_list)
                        execute_cli_list.append(para_list[v_index + 1])
                        is_first_more = 0
                    else:
                        execute_cli_list.append(para_list[v_index + 1])
        else:
            debug('Only -f flag exist', is_debug)
            execute_cli_list.extend(file_cli_list)
    else:
        ###hm
        if count==1:
            execute_cli_list = cli_list
        else: 
            if len(cli_list)==1:
                execute_cli_list = cli_list
            else:
                print '-c only support one -v parameter, pls check'
                return None
    debug('Execute cli list is as below...', is_debug) 
    debug(execute_cli_list, is_debug)
    try:
        ssh_result = ssh_execute_cli(ip, user, passwd, execute_cli_list, port, timeout, prompt, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, count)
    except Exception, e:
        print str(e)
    else:
        return ssh_result
            
if __name__ == '__main__':
    ssh_result = main()
    if ssh_result:
        ssh_result.close()
        print 'SSH successfully, exit 0'
        sys.exit(0)
    else:
        print 'SSH failed, exit 1'
        sys.exit(1)
