1. Modify format to unix
2. expect_list=[pexpect.TIMEOUT, 'Connection timed out', 'No route to host.*', 'Connected.*Escape character.*User Name:.*', 'Connected.*[Pp]assword:.*', 'Welcome to Aerohive Product.*login:.*']
modify index 1 from pass to 
        print 'The mpc connect to the remote target timeout, please confirm'
        print 'before is %s, after is %s' % (telnet_login_result.before, telnet_login_result.after)
        telnet_login_result.close(force=True)
        return None