1. add bumped check for the first login, add support the already login status
2. add support both -v -f in one step
3. reset config or reboot cannot match login( the first time is send ctrl+eco, the other is enter directly)(console)
nor_index = console_login_result.expect([pexpect.EOF, pexpect.TIMEOUT, prompt, 'Use the Aerohive.*no>:','Welcome to Aerohive Product.*login','[Pp]assword'], timeout=login_timeout)
nor_index == 1
4. modify the retry time from 12 to 18


1. Support the already login status when meet bumped status
2. Support both ¨Cv ¨Cf in one step
3. Optimize the retry way, the first time is send ctrl+eco, the other is enter directly
