1. bumped mode already login optimzed
2. Add support reset config bootstrap
3. Add waite for login for the cli
'reset config
reboot
boot-param country-code'
4. modify country code to 'To apply radio setting.*it now\?' to match 
''AH-50a640#boot-param region World

Region code is set, please reboot AP later.
AH-50a640#boot-param country-code 784
Note: To apply radio setting for the new countryWARNING!!! 10 minute CAC period as channel
is a weather radar channel

code, you must reboot the HiveAP. Do you want to reboot it now? WARNING!!! 10 minute
CAC period as channel is a weather radar channel

WARNING!!! 10 minute CAC period as channel is a weather radar channel
End of DFS wait period for 5680MHZ''

5. Modift 'exit' to match more general status(not only shell)