1. support -bp to enter bootload and execute command
for 
bootload login
<console target ="ap1" prompt="[=\w+]>">
       -bp ${bootload_passwd}
       -v "reboot"
</console>

booload execute
<console target ="ap1" prompt="[=\w+]>">
       -v "version"
</console>

booload exit
<console target ="ap1" >
       -v "reset"
</console>

or for all cli in a line
<console target ="ap1" prompt="[=\w+]>|AH_\w+*#">
       -bp ${bootload_passwd}
       -v "reboot"
       -v "version"
       -v "reset"
</console>

2. support use 'quit' to quit login status

3. Add execute CLI num if print

4. Add time print for the log