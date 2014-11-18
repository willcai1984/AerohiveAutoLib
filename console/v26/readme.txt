1. Add support parameters -loop
2. Modify sp default from false to '', for no shell passwd
3.
        elif shell_regex.search(cli):
            #v26 start
            ### add prompt to expect
            if shellpasswd:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, '[Pp]assword', timeout, wait))
                cli_sendmode_expect_timeout_wait_list.append((shellpasswd, sendmode, prompt, timeout, wait))
            else:
                cli_sendmode_expect_timeout_wait_list.append((cli, sendmode, prompt, timeout, wait))
            #v26 end
4. Modify command send mode