1. Modify special check for win laptop begin(BR vpc), from root@hztb.* to root@.*
2. add retry times for logout and modify the timeout fro 10 to 5
3. delete the logout timeout vlaue in ssh_execute_cli(), set it to default value of the logout() = 5s

