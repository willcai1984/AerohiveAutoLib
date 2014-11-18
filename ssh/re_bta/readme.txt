Modify based on v2
1. add check for reboot and reset, if exist, wait 30s for next step
2. modify root@hz.* to root@.*(for br vpc)
3. add retry times for logout and modify the timeout fro 10 to 3
4. delete the logout timeout vlaue in ssh_execute_cli(), set it to default value of the logout() = 3s
