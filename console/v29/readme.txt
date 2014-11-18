1. fix the bug of "show log buffer" meet more more than 2 times cause "quit" timeout
2014-04-29 15:37:49 DEBUG Expect list is
2014-04-29 15:37:49 DEBUG [<class 'pexpect.TIMEOUT'>, '--More--', 'AH-[a-z0-9A-Z_-]*#|(root|logger)@.*~.*\\$']
2014-04-29 15:37:49 DEBUG Timeout is
2014-04-29 15:37:49 DEBUG 150
2014-04-29 15:37:49 DEBUG spawn child exist, sendline directly
2014-04-29 15:37:49 DEBUG Match expect index is 2, value is 'AH-ltwu#' 
2014-04-29 15:37:49 DEBUG Meet more 45 times
2014-04-29 15:37:49 DEBUG Sleep wait time 0.5 to execute next cli
2014-04-29 15:37:50 DEBUG ....................Quit login status....................
2014-04-29 15:37:52 DEBUG 1 time retry begin
2014-04-29 15:37:54 DEBUG 1 time retry over
2014-04-29 15:37:54 DEBUG 2 time retry begin
2014-04-29 15:37:56 DEBUG 2 time retry over
2014-04-29 15:37:56 DEBUG 3 time retry begin
2014-04-29 15:37:58 DEBUG 3 time retry over
2014-04-29 15:37:58 DEBUG 4 time retry begin
2014-04-29 15:38:00 DEBUG 4 time retry over
2014-04-29 15:38:00 DEBUG 5 time retry begin
2014-04-29 15:38:02 DEBUG 5 time retry over
Retry 5 times and logout still failed, return none
before is  
after is <class 'pexpect.TIMEOUT'>
SSH 192.168.101.121 process over.
SSH failed, exit 1

Root cause, the next command line is typed more than 45 " ", and send ctrl+d cannot take effort
Resovle solution, send enter at the end of the status more than 2 more

execute_command_via_cli_sendmode_expect_timeout_wait_list
execute_command_via_cli_sendmode_expect_timeout_wait_list_ssh


2.Add support reboot offset

3. ' --More-- \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08          \x08\x08\x08\x08\x08\x08\x08\x08\x08\x08' to ''

4.Add prompt to shell part for no shell passwd situation