1. Add special check for win laptop begin

root@10.155.40.11's password: DEBUG Add host to known host list successfully, and meet password part

Last login: Thu Mar 14 11:21:29 2013 from 10.155.40.10
      ____________________,             ______________________________________
   .QQQQQQQQQQQQQQQQQQQQQQQQL_         |                                      |
 .gQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ__   |                                      |
 gQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ==   |                    _.---.)           |
 QQQQQQQQQQQQQQQQQQQQQQQQQQQF=         |          (^--^)_.-"      `;          |
 QQQQQQQQQ================!            |          ) ee (           |          |
 QQQQQQQQ                              |         (_.__._)         /           |
 QQQQQQQQ                              |           `--',        ,'            |
 QQQQQQQQ     ~"jjj__,                 |            jgs )_|--')_|             |
 QQQQQQQQ       "jjjjjjjjjj___         |                ""'   ""'             |
 QQQQQQQQ        ~jjjjjjjjjjjjjjjjj__  |                                      |
 QQQQQQQQ        _jjjjjjjjjjjjjj/~~~~  |      The Hippo says: Welcome to      |
 QQQQQQQQ      .{jjjjjjj/~~~~~         |                             _        |
 QQQQQQQQ     .{/~~~~`                 |  ____  _   _   ____  _ _ _ (_) ____  |
 QQQQQQQQ                              | / ___)| | | | / _  || | | || ||  _ \ |
 QQQQQQQQ                              |( (___ | |_| |( (_| || | | || || | | ||
 QQQQQQQQQL_______________,            | \____) \__  | \___ | \___/ |_||_| |_||
 QQQQQQQQQQQQQQQQQQQQQQQQQQQL___       |        (___/  (____|                 |
 4QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ___  |                                      |
 (=QQQQQQQQQQQQQQQQQQQQQQQQQQQQQ====   |       -.-. -.-- --. .-- .. -.        |
   (QQQQQQQQQQQQQQQQQQQQQQQQF=         |______________________________________|


root@hztb1-pc1 ~


>>> import pexpect
>>> cli= 'ssh root@10.155.40.11 -p 22'
>>> a=pexpect.spawn(cli)
>>> a.expect('ssword')
0
>>> a.sendline('aerohive')
9
>>> a.expect('Last.*root@hztb1.*')
0
>>> a.after
'Last login: Thu Mar 14 11:27:21 2013 from 10.155.40.10\r\r\n      ____________________,             ______________________________________\r\n   .QQQQQQQQQQQQQQQQQQQQQQQQL_         |                                      |\r\n .gQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ__   |                                      |\r\n gQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ==   |                    _.---.)           |\r\n QQQQQQQQQQQQQQQQQQQQQQQQQQQF=         |          (^--^)_.-"      `;          |\r\n QQQQQQQQQ================!            |          ) ee (           |          |\r\n QQQQQQQQ                              |         (_.__._)         /           |\r\n QQQQQQQQ                              |           `--\',        ,\'            |\r\n QQQQQQQQ     ~"jjj__,                 |            jgs )_|--\')_|             |\r\n QQQQQQQQ       "jjjjjjjjjj___         |                ""\'   ""\'             |\r\n QQQQQQQQ        ~jjjjjjjjjjjjjjjjj__  |                                      |\r\n QQQQQQQQ        _jjjjjjjjjjjjjj/~~~~  |      The Hippo says: Welcome to      |\r\n QQQQQQQQ      .{jjjjjjj/~~~~~         |                             _        |\r\n QQQQQQQQ     .{/~~~~`                 |  ____  _   _   ____  _ _ _ (_) ____  |\r\n QQQQQQQQ                              | / ___)| | | | / _  || | | || ||  _ \\ |\r\n QQQQQQQQ                              |( (___ | |_| |( (_| || | | || || | | ||\r\n QQQQQQQQQL_______________,            | \\____) \\__  | \\___ | \\___/ |_||_| |_||\r\n QQQQQQQQQQQQQQQQQQQQQQQQQQQL___       |        (___/  (____|                 |\r\n 4QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ___  |                                      |\r\n (=QQQQQQQQQQQQQQQQQQQQQQQQQQQQQ====   |       -.-. -.-- --. .-- .. -.        |\r\n   (QQQQQQQQQQQQQQQQQQQQQQQQF=         |______________________________________|\r\n\r\n\x1b]0;~\x07\r\r\n\x1b[32mroot@hztb1-pc1 \x1b[33m~\x1b[0m\r\r\n$ '
>>> 


2. add default ~ for win clients
cli_tuple_list.append((cli,'%s|~' % prompt))