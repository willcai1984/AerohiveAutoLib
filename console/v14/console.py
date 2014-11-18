#!/usr/bin/python
# Filename: console.py
# Function: login target execute cli via console server
# coding:utf-8
# Author: Well
# Example command: console.py -i 782 -e tb1-ap350-3 -v "show run" -d localhost -u admin -p aerohive -m "AH.*#"
# Transmit command: console -M localhost tb1-ap350-3 -f -l root
import pexpect, sys, argparse, re, time

def sleep (mytime=1):
    time.sleep(mytime)


def debug(mesage, is_debug=True):
    if mesage and is_debug:
        print '%s DEBUG' % time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        print mesage

### cli mode: send/sendline/sendcontrol/sendnone, for example: [('','sendline'),('d','sendcontrol'),('','sendnone')]
###### if you want to send ctrl-e+co cli_mode_tuple_list=[[('e','sendcontrol'),('co','send')]]
### retry_cli_mode: send/sendline/sendcontrol/sendnone
def spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout=5 , retry_cli_mode_tuple_list=[], retry_times=5, spawn_child='', is_debug=True):
    debug('............Timeout_retry func Init sendline parameters............',is_debug)
    retry_num = 0
    retry_times=int(retry_times)
    debug('CLI is',is_debug)
    debug(cli_mode_tuple_list,is_debug)
    debug('Expect list is',is_debug)
    debug(expect_list,is_debug)
    debug('Timeout is',is_debug)
    debug(timeout,is_debug)
    ###process retry_cli_list
    if len(retry_cli_mode_tuple_list) < retry_times:
        ###if retry_cli num is less than retry times, extend with sendnone type
        extend_num = retry_times-len(retry_cli_mode_tuple_list)
        retry_execute_tuple_list=retry_cli_mode_tuple_list+[[('','sendnone')]]*extend_num
    elif len(retry_cli_mode_tuple_list) == retry_times:
        retry_execute_tuple_list=retry_cli_mode_tuple_list
    else:
        print '''retry_cli_list's length is more than retry_times, cannot process'''
        return None, None
    debug('............Timeout_retry func Execute command send process............',is_debug)
    ###Judge if spawn exist, yes--sendline directly, no--create spawn_child
    if spawn_child:
        debug('spawn child exist, sendline directly',is_debug)
        for cli,cli_mode in cli_mode_tuple_list:
            if cli_mode == 'send':
                spawn_child.send(cli)
            elif cli_mode == 'sendline':
                spawn_child.sendline(cli)
            elif cli_mode == 'sendcontrol':
                spawn_child.sendcontrol(cli)
            elif cli_mode == 'sendnone':
                pass
            else:
                print '''Error cli mode error, please check your cli's mode is send/sendline/sendcontrol/sendnone'''
                return None, None 
    else:
        debug('spawn child not exist, create spawn firstly',is_debug)
        for cli,cli_mode in cli_mode_tuple_list:
            spawn_child = pexpect.spawn(cli)
    retry_index=spawn_child.expect(list(expect_list), timeout=timeout)
    ###check whether enter to retry mode
    if retry_index == 0:
        debug('Meet time out status, enable retry mode')
        debug('retry_execute_tuple_list is',is_debug)
        debug(retry_execute_tuple_list,is_debug)
        while retry_index == 0:
            ### the first retry, the num is 1
            retry_num += 1
            ### if more than retry total num, return None
            if retry_num > retry_times:
                print 'Retry %s times and still failed, close the expect child and return none' % retry_times
                print 'before is %s, after is %s' % (spawn_child.before, spawn_child.after)
                spawn_child.close(force=True)
                return None, retry_index  
            debug('Retry %s time begin' % retry_num, is_debug)
            ###retry_execute_tuple_list increased via index     
            for cli,cli_mode in retry_execute_tuple_list[retry_num-1]:
                if cli_mode == 'send':
                    spawn_child.send(cli)
                elif cli_mode == 'sendline':
                    spawn_child.sendline(cli)
                elif cli_mode == 'sendcontrol':
                    spawn_child.sendcontrol(cli)
                elif cli_mode == 'sendnone':
                    pass
                else:
                    print '''Error cli mode error, please check your cli's mode is send/sendline/sendcontrol/sendnone'''
                    return None, None 
            retry_index = spawn_child.expect(expect_list, timeout=timeout)
            debug('Retry %s time over' % retry_num, is_debug)
    return spawn_child, retry_index
        

def general_login(spawn_chlid,user,passwd,prompt,login_timeout=2,login_retry_times=10,is_debug=False,is_user=False,is_passwd=False,is_no=False,is_prompt=False):
    general_login_result=spawn_chlid
    if is_user:
        debug('Meet login successfully, send user to confirm login',is_debug)
        debug('............Step3 send user to confirm login............',is_debug)            
        cli_mode_tuple_list=[(user,'sendline')]
        expect_list=[pexpect.TIMEOUT, '[Pp]assword.*']
        timeout=login_timeout
        ###only need expect func, sendnone
        retry_cli_mode_tuple_list=[[('','sendnone')]]*login_retry_times
        general_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, is_debug)
        general_login_result=general_login_info[0]
        general_login_index=general_login_info[1]
        if general_login_index==0:
            print 'Send user to confirm login timeout, please confirm the host is alive'
            return None
        elif general_login_index==1:                  
            is_passwd=True
            debug('''From is_user jump to is_passwd process ''',is_debug)
    if is_passwd:
        debug('Meet password successfully, send passwd to confirm login',is_debug)
        debug('............Step4 send password to confirm login............',is_debug)
        cli_mode_tuple_list=[(passwd,'sendline')]
        expect_list=[pexpect.TIMEOUT, 'login.*', '[Pp]assword.*', 'yes\|no>:.*', prompt]
        timeout=login_timeout
        ###only need expect func, sendnone
        retry_cli_mode_tuple_list=[[('','sendnone')]]*login_retry_times
        general_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, is_debug)
        general_login_result=general_login_info[0]
        general_login_index=general_login_info[1]
        if general_login_index==0:
            print 'Send password to confirm login timeout, please confirm the host is alive'
            return None
        elif general_login_index==1:
            print 'Meet login again, user or password maybe incorrect, please check'
            general_login_result.close(force=True)
            return None
        elif general_login_index==2:
            print 'Meet password again, password maybe incorrect, please check'
            general_login_result.close(force=True)
            return None                              
        elif general_login_index==3:
            is_no=True
            debug('''From is_passwd jump to is_no process ''',is_debug)
        elif general_login_index==4:
            is_prompt=True
            debug('''From is_passwd jump to is_prompt process ''',is_debug)
    if is_no:
        debug('Meet is_default yes or no successfully, send no to not use default config',is_debug)
        debug('............Step5 send no to not use default config............',is_debug)
        cli_mode_tuple_list=[('no','sendline')]
        expect_list=[pexpect.TIMEOUT, prompt]
        timeout=login_timeout
        ###only need expect func, sendnone
        retry_cli_mode_tuple_list=[[('','sendnone')]]*login_retry_times
        general_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, general_login_result, is_debug)
        general_login_result=general_login_info[0]
        general_login_index=general_login_info[1]            
        if general_login_index == 0:
            print 'Send no to confirm login timeout, please confirm the host is alive'
            return None
        elif general_login_index== 1:
            is_prompt=True
            debug('''From is_no jump to is_prompt process ''',is_debug)
    if is_prompt:
        debug('Meet prompt successfully, can cli now',is_debug)
    return general_login_result



def generate_cli_list(cli_list, config_file_path, input_para_list, is_debug=True):
    if config_file_path:
        debug('config file flag is set, special process the cli_list', is_debug)
        v_argv_list = []
        f_argv_list = []
        para_index = 0
        # get -v and -f indexes for redesign all cli's order
        for para in input_para_list:
            if para == '-v':
                v_argv_list.append(para_index)
            if para == '-f':
                f_argv_list.append(para_index)
            para_index += 1
        debug('input_para_list is as below', is_debug)
        debug(input_para_list, is_debug)
        debug('v_command_index_list is as below', is_debug)
        debug(v_argv_list, is_debug)
        debug('f_command_index_list is as below', is_debug)
        debug(f_argv_list, is_debug)
        try:
            with open(config_file_path, mode='r') as config_file_open:
                read_cli_list = config_file_open.readlines()
            ###remove \r\n for windows file
            file_cli_list = []
            for cli in read_cli_list:
                file_cli_list.append(re.sub('[\r\n]', '', cli))   
        except IOError:
            print 'Your file path %s is wrong or the file is not exist' % config_file_path
        else:
            debug('Open configure file successfully', is_debug)
        execute_cli_list = []
        f_num=len(f_argv_list)
        f_index=0
        if v_argv_list:
            debug('Both -v -f flag exist', is_debug)
            is_v_less_than_f = 1
            for v_index in v_argv_list:
                ### if -v's index is less than -f's, add the para to cli_list directly
                if v_index < f_argv_list[f_index]:
                    execute_cli_list.append(input_para_list[v_index + 1])
                else:
                    ### if -v's index is the first time more than -f's, should add the f's para firstly and then add v's(only support one file), set the flag to 0
                    if is_v_less_than_f:
                        execute_cli_list.extend(file_cli_list)
                        execute_cli_list.append(input_para_list[v_index + 1])
                        ###if has more than 2 f para, set the f_index to next(-v still less than -f), else ,set the is_v_less_than_f flag to 0(-v more than -f)
                        if f_index < f_num-1:
                            f_index += 1
                        else:
                            is_v_less_than_f = 0
                    else:
                        ### if -v's index is not the first time more than -f's, add the para to cli_list directly
                        execute_cli_list.append(input_para_list[v_index + 1])
        else:
            debug('Only -f flag exist', is_debug)
            execute_cli_list.extend(file_cli_list)
    else:
        execute_cli_list = cli_list
    return execute_cli_list



def generate_cli_expect_timeout_list(cli_list, prompt, timeout, passwd='', shellpasswd='', bootpasswd=''):
    cli_expect_timeout_list = [] 
    ctrl_index_list = []
    ctrl_index = 0
    reboot_timeout = 300
    save_img_timeout = 1200
    boot_timeout = 30
    for cli in cli_list:
        log_regex = re.compile('^show log.*')
        reset_config_regex = re.compile('^reset config$')
        reset_boot_regex = re.compile('^reset config bootstrap$')
        reboot_regex = re.compile('^reboot$')
        save_config_regex = re.compile('^save config tftp:.* (current|bootstrap)')
        # ##v9 add img for accurate match
        save_image_regex = re.compile('^save image tftp:.*img$')
        # ##v9 add support save image reboot cases
        save_image_reboot_regex = re.compile('^save image tftp:.*now$')
        shell_regex = re.compile('^_shell$')
        exit_regex = re.compile('^exit$')
        enble_regex = re.compile('^enable$')
        country_regex = re.compile('^boot-param country-code.*')
        ctrl_regex = re.compile('ctrl-.*')
        # ##v12 add ^reset$ for logout bootload
        reset_regex = re.compile('^reset$')
        # ##v12 add quit for quit login status
        quit_regex = re.compile('^quit$')
        if log_regex.search(cli):
            cli_expect_timeout_list.append((cli, '\w+.*', timeout))
            cli_expect_timeout_list.append(('', prompt, timeout))
            ctrl_index = ctrl_index + 2
        elif reset_boot_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'bootstrap configuration.*', timeout))
            cli_expect_timeout_list.append(('y', prompt, reboot_timeout))
            ctrl_index = ctrl_index + 2
        elif reset_config_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'bootstrap configuration.*', timeout))
            cli_expect_timeout_list.append(('y', prompt, timeout))
            cli_expect_timeout_list.append(('', 'login:', reboot_timeout))
            ctrl_index = ctrl_index + 3
        elif reboot_regex.search(cli):
            # ##v14 add support bootload
            if bootpasswd:
                cli_expect_timeout_list.append((cli, 'Do you really want to reboot.*', timeout))
                cli_expect_timeout_list.append(('y', prompt, timeout))
                cli_expect_timeout_list.append(('', 'Hit.*to stop.*autoboot.*2.*', boot_timeout))
                cli_expect_timeout_list.append(('', '[Pp]assword:', timeout))
                cli_expect_timeout_list.append((bootpasswd, '.*>.*', timeout))
                ctrl_index = ctrl_index + 5
            else:
                cli_expect_timeout_list.append((cli, 'Do you really want to reboot.*', timeout))
                cli_expect_timeout_list.append(('y', prompt, timeout))
                cli_expect_timeout_list.append(('', 'login:.*', reboot_timeout))
                ctrl_index = ctrl_index + 3               
        elif save_config_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'configuration.*', timeout))
            cli_expect_timeout_list.append(('y', prompt, timeout))
            ctrl_index = ctrl_index + 2
        elif save_image_regex.search(cli):
            cli_expect_timeout_list.append((cli, r'update image.*', timeout))
            cli_expect_timeout_list.append(('y', prompt, save_img_timeout))
            ctrl_index = ctrl_index + 2
        # ##v9 add support save image and reboot
        elif save_image_reboot_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'update image.*', timeout))
            cli_expect_timeout_list.append(('y', prompt, save_img_timeout))
            cli_expect_timeout_list.append(('', 'login:.*', reboot_timeout))
            ctrl_index = ctrl_index + 3
        elif shell_regex.search(cli):
            cli_expect_timeout_list.append((cli, '[Pp]assword.*', timeout))
            cli_expect_timeout_list.append((shellpasswd, prompt, timeout))
            ctrl_index = ctrl_index + 2
        elif exit_regex.search(cli):
            cli_expect_timeout_list.append((cli, prompt, timeout))                
            ctrl_index = ctrl_index + 1          
        elif enble_regex.search(cli):
            cli_expect_timeout_list.append((cli, '[Pp]assword.*', timeout))
            cli_expect_timeout_list.append((passwd, prompt, timeout))
            ctrl_index = ctrl_index + 1               
        elif country_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'To apply radio setting.*it now\?.*', timeout))
            cli_expect_timeout_list.append(('y', prompt, timeout))
            cli_expect_timeout_list.append(('', 'login:.*', reboot_timeout))
            ctrl_index = ctrl_index + 3    
        elif ctrl_regex.search(cli):
            cli_expect_timeout_list.append((cli, prompt, timeout))
            ctrl_index_list.append(ctrl_index)
            ctrl_index = ctrl_index + 1
        elif reset_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'login:.*', reboot_timeout))
            ctrl_index = ctrl_index + 1  
        elif quit_regex.search(cli):
            cli_expect_timeout_list.append((cli, 'login:.*', timeout))
            ctrl_index = ctrl_index + 1  
        else:
            cli_expect_timeout_list.append((cli, prompt, timeout))
            ctrl_index = ctrl_index + 1
    return cli_expect_timeout_list, ctrl_index_list
    

def console_login(ip,user,passwd,serialname,prompt,login_timeout=2,login_retry_times=20,log_file_path=[],log_file_open=[],is_debug=True):
    ###init parameters process
    login_retry_times=int(login_retry_times)
    ###v13 login_retry_times should be more than 3 due to the retry format of 'Reboot after bootload status or normal(no reboot) status' 
    if login_retry_times < 3:
        print 'Error, Retry times should be more than 3'
        return None
    login_timeout=int(login_timeout)
    ###init flag process
    is_user=False
    is_passwd=False
    is_no=False
    is_prompt=False
    ###Execute login process
    console_login_command = 'console -M %s %s -f -l root' % (ip, serialname)
    debug('''console login command is "%s"''' % console_login_command, is_debug)
    debug('............Step1 send command to login target via console............',is_debug)
    cli_mode_tuple_list=[(console_login_command,'sendline')]
    ###0 timeout
    ###1 no this console name in the localhost
    ###2 normal login, cannot add.* after enter ... help due to bumped and warning check in the next step 
    expect_list=[pexpect.TIMEOUT, 'localhost: console .* not found.*', 'Enter .* for help']
    timeout=login_timeout
    ### if not meet the expect list, will send 5 enter
    ######retry_cli_mode_tuple_list should have more [] with cli_mode_tuple_list
    retry_cli_mode_tuple_list=[[('','sendline')]]*login_retry_times
#    spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout=5 , retry_cli_mode_tuple_list=[], login_retry_times=5, spawn_child='', is_debug=True)
    console_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, '', is_debug)
    console_login_result=console_login_info[0]
    console_login_index=console_login_info[1]
    if log_file_path == './stdout':
        console_login_result.logfile_read = sys.stdout
    else:
        console_login_result.logfile_read = log_file_open
    if console_login_index == 0:
        print 'console host timeout, please confirm you can reach the host'
        return None
    elif console_login_index == 1:
        print 'The hostname %s is not aliveable in the localhost, please confirm' % serialname
        print 'before is %s, after is %s' % (console_login_result.before, console_login_result.after)
        console_login_result.close(force=True)
        return None
    elif console_login_index == 2:
        debug('''............Step2 send 'enter' to confirm login target via console............''',is_debug)
        ###check if is the reboot status(reboot status no need to type 'enter' will show something on the screen)(before boot load, for the reset status not wait 30s)
        is_reboot_before_bootload = console_login_result.expect([pexpect.TIMEOUT, '[\w]+'], timeout=1)                   
        if is_reboot_before_bootload:
            debug('Reboot before bootload status', is_debug)
            debug('Before is ...', is_debug)
            debug(console_login_result.before, is_debug)
            debug('After is ...', is_debug)
            debug(console_login_result.after, is_debug)
            if console_login_result.after == 'bumped' or console_login_result.after == 'WARNING':
                if console_login_result.after == 'bumped':
                    debug('Meet Bumped mode, send enter to confirm')
                elif console_login_result.after == 'WARNING':
                    debug('Meet WARNING mode, send enter to confirm')
                cli_mode_tuple_list=[('','sendline')]
                expect_list=[pexpect.TIMEOUT, 'login.*', '[Pp]assword.*','yes\|no>:.*', prompt]
                timeout=login_timeout
                retry_cli_mode_tuple_list=[[('','sendline')]]*login_retry_times
                console_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, console_login_result, is_debug)
                console_login_result=console_login_info[0]
                console_login_index=console_login_info[1]
                if console_login_index == 0:
                    print 'Send enter to confirm login bumped/waning mode timeout'
                    return None
                elif console_login_index == 1:
                    is_user=True
                    debug('''From 'Bumped/Warning' mode jump to is_user process ''',is_debug)
                elif console_login_index == 2:
                    is_passwd=True
                    debug('''From 'Bumped/Warning' mode jump to is_passwd process ''',is_debug)
                elif console_login_index == 3:
                    is_no=True
                    debug('''From 'Bumped/Warning' mode jump to is_no process ''',is_debug)
                elif console_login_index == 4:
                    is_prompt=True
                    debug('''From 'Bumped/Warning' mode jump to is_prompt process ''',is_debug)
            else:
                debug('Meet Reboot before bootload mode, wait for power on successfully')
                ###before bootload mode cannot send anything , use sendnone 
                cli_mode_tuple_list=[('','sendnone')]
                expect_list=[pexpect.TIMEOUT, 'login.*', '[Pp]assword.*','yes\|no>:.*', prompt]
                timeout=login_timeout
                retry_cli_mode_tuple_list=[[('','sendnone')]]*login_retry_times
                console_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, console_login_result, is_debug)
                console_login_result=console_login_info[0]
                console_login_index=console_login_info[1]
                if console_login_index == 0:
                    print 'Send enter to confirm login bumped/waning mode timeout'
                    return None
                elif console_login_index == 1:
                    is_user=True
                    debug('''From 'Reboot/Reset' mode jump to is_user process ''',is_debug)
                elif console_login_index == 2:
                    is_passwd=True
                    debug('''From 'Reboot/Reset' mode jump to is_passwd process ''',is_debug)
                elif console_login_index == 3:
                    is_no=True
                    debug('''From 'Reboot/Reset' mode jump to is_no process ''',is_debug)
                elif console_login_index == 4:
                    is_prompt=True
                    debug('''From 'Reboot/Reset' mode jump to is_prompt process ''',is_debug)  
        else:
            debug('Reboot after bootload status or normal(no reboot) status', is_debug)
            cli_mode_tuple_list=[('','sendline')]
            ###0 May meet aerohive pruduct powerdown on vmwarw ---EOF, console command is EOF already
            ###1 If the cisco console server's port connect nothing, would stay'Escape character is '^]'.' when you send 'enter', cannot diff it from the normal way ,use timeout to mark it
            ###2 Aerohive product already login---#
            ###3 Aerohive product already login, but is the first time to login after reset---'Use the Aerohive.*<yes|no>:'
            ###4 Aerohive product login normally
            ###5 login switch via console(meet password) 
            expect_list=[pexpect.TIMEOUT, pexpect.EOF,'login.*', '[Pp]assword.*','yes\|no>:.*', prompt]
            timeout=login_timeout
            ###the first time send ctrl-e+co, the others send enter
            ###v13 first and second times send enter only, if timeout: send ctrl-e+co
            retry_cli_mode_tuple_list=[[('e','sendcontrol'),('co','send')],[('','sendline')]]+[[('','sendline')]]*(login_retry_times-2)
            console_login_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, timeout, retry_cli_mode_tuple_list , login_retry_times, console_login_result, is_debug)
            console_login_result=console_login_info[0]
            console_login_index=console_login_info[1] 
            if console_login_index == 0:
                print 'Send enter to confirm login timeout, please confirm the host is alive'
                return None                
            elif console_login_index == 1:
                print 'The hostname %s not exist or in using, please check' % serialname
                print 'before is %s, after is %s' % (console_login_result.before, console_login_result.after)
                console_login_result.close(force=True)
                return None
            elif console_login_index == 2:
                is_user=True
                debug('''From 'Normal_login' mode jump to is_user process ''',is_debug)
            elif console_login_index == 3:
                is_passwd=True
                debug('''From 'Normal_login' mode jump to is_passwd process ''',is_debug)
            elif console_login_index == 4:
                is_no=True
                debug('''From 'Normal_login' mode jump to is_no process ''',is_debug)
            elif console_login_index == 5:
                is_prompt=True
                debug('''From 'Normal_login' mode jump to is_prompt process ''',is_debug)
        ###Process the login via flag
        ### the four flags' logic are if/if/if/if not if/elif/elif/elif due to is_user may use is_passwd's func
        console_login_result=general_login(console_login_result,user,passwd,prompt,login_timeout,login_retry_times,is_debug,is_user,is_passwd,is_no,is_prompt)       
    return console_login_result



###Add spy mode for long time running
def execute_command_via_cli_expect_timeout_list(spawn_child, cli_expect_timeout_list, cli_retry_times=2,wait_time=0.5, ctrl_index_list=[], is_debug=True):
    execute_cli_result = spawn_child
    cli_num = 1
    for cli, cli_expect, cli_timeout in cli_expect_timeout_list:
        if cli_expect_timeout_list.index((cli, cli_expect, cli_timeout)) in ctrl_index_list:
            debug(cli_expect_timeout_list.index((cli, cli_expect, cli_timeout)), is_debug)
            debug(ctrl_index_list, is_debug)
            debug('%s send ctrl command' % cli_num, is_debug)
            ctrl_cli = re.sub(r'ctrl-', '', cli)
            execute_cli_result.sendcontrol(ctrl_cli)
        else:
            debug('%s send normal command' % cli_num, is_debug)
            execute_cli_result.sendline(cli)
        index = execute_cli_result.expect([pexpect.TIMEOUT, cli_expect, '--More--', 'More:', '-- More --'], timeout=cli_timeout)
        ###v13 set private var for meet more status
        more_num = 0
        more_index = 1
        ###
        if index == 0:
            print '''TimeOut when execute the %s CLI, fail in Execute CLI parter''' % cli_num
            print 'CLI is %s, Expect is %s, Timeout is %s' % (cli, cli_expect, cli_timeout)
            print 'before is %s' % (execute_cli_result.before)
            print 'after is %s' % (execute_cli_result.after)
            execute_cli_result.close(force=True)
            return None
        elif index == 1:
            debug('%s successfully executed' % cli, is_debug)
        elif index == 2:
            debug('''Meet 'more', should send 'blank' to continue, Aerohive products''', is_debug)
            while more_index == 1:
                more_num += 1
                ###v13 add retry for status 'more'
                cli_mode_tuple_list=[(' ','send')]
                expect_list=[pexpect.TIMEOUT,'--More--',cli_expect]
                retry_cli_mode_tuple_list=[[('','sendline')]]*cli_retry_times
                more_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list, cli_timeout, retry_cli_mode_tuple_list , cli_retry_times, execute_cli_result, is_debug)
                more_result=more_info[0]
                more_index=more_info[1]
                if more_index == 0:
                    print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                    return None
                ###continue while
                elif more_index == 1:
                    pass
                ###continue next for entry
                elif more_index == 2:
                    pass
            execute_cli_result=more_result           
            debug('Meet more %s times' % more_num, is_debug)
        elif index == 3:
            debug('''Meet 'more', should send 'blank' to continue, Dell products''', is_debug)
            while more_index == 1:
                execute_cli_result.send(' ')
                more_index = execute_cli_result.expect([pexpect.TIMEOUT,'More:',cli_expect], timeout=cli_timeout)
                if more_index == 0:
                    print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                    execute_cli_result.close(force=True)
                    return None                
        elif index == 4:
            debug('''Meet 'more', should send 'blank' to continue, H3C products''', is_debug)
            while more_index == 1:
                execute_cli_result.send(' ')
                more_index = execute_cli_result.expect([pexpect.TIMEOUT,'-- More --',cli_expect], timeout=cli_timeout)
                if more_index == 0:
                    print 'Send blank to confirm show the left log timeout, please confirm the host is alive'
                    execute_cli_result.close(force=True)
                    return None
        else:
            print '''Not match any expect in 'step cli execute' expect_list, please check'''
            print 'before is %s, after is %s' % (execute_cli_result.before, execute_cli_result.after)
            execute_cli_result.close(force=True)
            return None     
        debug('Sleep wait time %s to execute next cli' % wait_time, is_debug)
        sleep(wait_time)
        cli_num += 1   
    return execute_cli_result



def console_logout(spawn_child, logout_timeout=2, logout_retry_times=20, is_debug=True):
    console_logout_result = spawn_child
    debug('....................Free console port....................', is_debug)
    cli_mode_tuple_list=[('e','sendcontrol'),('c.','send')]
    expect_list=[pexpect.TIMEOUT, 'disconnect']
    retry_cli_mode_tuple_list=[[('','sendline')]]+[[('e','sendcontrol'),('c.','send')]]+[[('','sendline')]]*(logout_retry_times-2)
    console_logout_info=spawn_timeout_retry(cli_mode_tuple_list, expect_list,logout_timeout, retry_cli_mode_tuple_list , logout_retry_times, console_logout_result, is_debug)
    console_logout_result=console_logout_info[0]
    console_logout_index=console_logout_info[1]
    if console_logout_index == 0:
        print '''TimeOut when send ctrl+ec. to to logout console prompt status'''
        print 'before is %s, after is %s' % (console_logout_result.before, console_logout_result.after)
        return None
    elif console_logout_index == 1:
        debug('Free console successfully', is_debug)
    else:
        print '''Not match any expect in 'logout' expect_list, please check'''
        print 'before is %s, after is %s' % (console_logout_result.before, console_logout_result.after)
        console_logout_result.close(force=True)
        return None                
    return console_logout_result





###define class, for logfile can be opened and closed automatic
class console_host:
    # ##v10 add wait time
    def __init__(self, ip, serialname, user, passwd, is_debug=False, absolute_logfile='', prompt='[$#>]', wait_time=0):
        self.ip = ip
        self.serialname = serialname
        self.user = user
        self.passwd = passwd
        self.is_debug = is_debug
        self.prompt = prompt
        self.absolute_logfile = absolute_logfile
        # ##v10 add wait time
        self.wait_time = wait_time
        if absolute_logfile == './stdout':
            pass
        else:
            self.absolute_logfile_open = open(absolute_logfile, mode='w')
        print 'console %s process start, init parameters............' % serialname
    def __del__(self):
        if self.absolute_logfile == './stdout':
            pass
        else:
            # ##close the mode a file firstly
            self.absolute_logfile_open.close()
            absolute_logfile = self.absolute_logfile
            # ##sub 28 blanks and \r
            with open(absolute_logfile, mode='r') as absolute_logfile_open:
                originate_logfile = absolute_logfile_open.read()
            correct_logfile = re.sub(' {28}|\r', '', originate_logfile)
            with open(absolute_logfile, mode='w') as absolute_logfile_open:
                absolute_logfile_open.write(correct_logfile)            
        print 'console %s process over.' % self.ip
        
    def login(self, login_timeout=2,login_retry_times=5):
        ip = self.ip
        serialname = self.serialname
        user = self.user
        passwd = self.passwd
        is_debug = self.is_debug
        prompt = self.prompt
        log_file_path = self.absolute_logfile
        if log_file_path == './stdout':
            log_file_open=[]
        else:
            log_file_open = self.absolute_logfile_open
        console_login_result=console_login(ip,user,passwd,serialname,prompt,login_timeout,login_retry_times,log_file_path,log_file_open,is_debug)            
        return console_login_result

    def execute_command_via_cli_expect_timeout_list(self, spawn_child, cli_expect_timeout_list, ctrl_index_list=[], cli_retry_times=2):
        is_debug = self.is_debug
        wait_time = self.wait_time
        console_cli_result=execute_command_via_cli_expect_timeout_list(spawn_child,cli_expect_timeout_list, cli_retry_times, wait_time, ctrl_index_list, is_debug)
        return console_cli_result

    # ##v11 modify timeout from 5 to 10 for low performance devices
    def logout(self, spawn_child, logout_timeout=10, logout_retry_times=5):
        is_debug = self.is_debug
        console_logout_result=console_logout(spawn_child, logout_timeout, logout_retry_times, is_debug)
        return console_logout_result







###def login-execute-logout func
def console_execute_cli(ip, user, passwd, serialname, cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd, wait_time, bootpasswd):
    timeout = int(timeout)
    retry_times = int(retry_times)
    wait_time = float(wait_time)
    retry_times = int(retry_times)
    ###set private var
    login_timeout=2
    login_retry_times=retry_times
    cli_timeout=timeout
    cli_retry_times=2
    logout_timeout=2
    logout_retry_times=10   
    ###start login process
    absolute_logfile = logdir + '/' + logfile
    debug('logfile path is %s' % absolute_logfile, is_debug)
    console = console_host(ip, serialname, user, passwd, is_debug, absolute_logfile, prompt, wait_time)
    console_host_login = console.login(login_timeout,login_retry_times)
    if console_host_login:
        execute_cli_list = generate_cli_expect_timeout_list(cli_list, prompt, cli_timeout, passwd, shellpasswd, bootpasswd)
        print 'execute_cli_list is as below'
        print execute_cli_list
        cli_expect_timeout_list = execute_cli_list[0]
        ctrl_index_list = execute_cli_list[1]
        debug('cli_exepct_timeout_list is as below', is_debug)
        debug(cli_expect_timeout_list, is_debug)
        debug('ctrl_index_list is as below', is_debug)
        debug(ctrl_index_list, is_debug)                                       
        console_host_execute = console.execute_command_via_cli_expect_timeout_list(console_host_login, cli_expect_timeout_list, ctrl_index_list, cli_retry_times)
    else:
        print 'Console login failed'
        return None
    if console_host_execute:
        console_host_logout = console.logout(console_host_execute,logout_timeout, logout_retry_times)
    else:
        print 'Console execute cli failed'
        return None        
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

parse.add_argument('-m', '--prompt', required=False, default='AH-\w+#.*', dest='prompt',
                    help='The login prompt you want to meet')

parse.add_argument('-o', '--timeout', required=False, default=5, type=int, dest='timeout',
                    help='Time out value for every execute cli step')

parse.add_argument('-l', '--logdir', required=False, default='.', dest='logdir',
                    help='The log file dir')

parse.add_argument('-z', '--logfile', required=False, default='stdout', dest='logfile',
                    help='The log file name')

parse.add_argument('-v', '--command', required=False, action='append', default=[], dest='cli_list',
                    help='The command you want to execute')

parse.add_argument('-sp', '--shellpasswd', required=False, default='', dest='shellpasswd',
                    help='Shell password for enter to shell mode')

parse.add_argument('-debug', '--debug', required=False, default=False, action='store_true', dest='is_debug',
                    help='enable debug mode')

parse.add_argument('-b', '--shell', required=False, default=False, action='store_true', dest='is_shell',
                    help='enable shell mode')

parse.add_argument('-i', '--interface', required=False, default='', dest='serial',
                    help='Serial number')

parse.add_argument('-n', '--nowait', required=False, default=False, action='store_true', dest='is_wait',
                    help='enable wait mode')

parse.add_argument('-f', '--file', required=False, default='', dest='configfilepath',
                    help='The path of configurefile')
###v13 modify to 90 and timeout modify to 2
parse.add_argument('-k', '--retry', required=False, default=90, type=int, dest='retry_times',
                    help='How many times you want to retry when the login step is failed')

parse.add_argument('-w', '--wait', required=False, default=0, type=float , dest='wait_time',
                    help='wait time between the current cli and next cli')

parse.add_argument('-bp', '--bootpassword', required=False, default='', dest='bootpasswd',
                    help='boot password')

def main():
    args = parse.parse_args() 
    is_debug = args.is_debug
    ip = args.desip
    user = args.user
    passwd = args.passwd
    ###process prompt: add \\ for $ and .* for the end, special process for '|'
    prompt = args.prompt
    prompt = re.sub('\$', '\\$', prompt)
    prompt_para_list = prompt.split('|')
    debug('prompt_para_list is as below', is_debug)
    debug(prompt_para_list, is_debug)
    prompt_len = len(prompt_para_list)
    prompt = ''
    for prompt_num in range(prompt_len):
        if prompt_num == prompt_len - 1:
            prompt = prompt + '%s.*' % prompt_para_list[prompt_num]
        else:
            prompt = prompt + '%s.*|' % prompt_para_list[prompt_num]
    debug('Real prompt is as below', is_debug)
    debug(prompt, is_debug)    
    timeout = args.timeout
    logdir = args.logdir
    logfile = args.logfile
    cli_list = args.cli_list
    shellpasswd = args.shellpasswd
    is_shell = args.is_shell
    serialname = args.serialname
    config_file_path = args.configfilepath
    retry_times = args.retry_times
    wait_time = args.wait_time
    bootpasswd = args.bootpasswd
    input_para_list=sys.argv
    debug('''Type command is "python %s"''' % (' '.join(input_para_list)),is_debug)
    execute_cli_list=generate_cli_list(cli_list, config_file_path, input_para_list, is_debug)
    debug('execute_cli_list is as below',is_debug)
    debug(execute_cli_list,is_debug)
    try:
        console_result = console_execute_cli(ip, user, passwd, serialname, execute_cli_list, prompt, timeout, retry_times, logdir, logfile, is_debug, is_shell, shellpasswd,wait_time, bootpasswd)
    except Exception, e:
        print str(e)
    else:
        return console_result
            
if __name__ == '__main__':
    console_result = main()
    if console_result:
        console_result.close(force=True)
        print 'Console successfully, exit 0'
        sys.exit(0)
    else:
        print 'Console failed, exit 1'
        sys.exit(1)
