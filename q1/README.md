"q1.py" is the python script for processing combined web server logs to produce instructions for ban and unban suspicious IP addresses.  

To execute the script, you should ensure the environment is installed with python 3.6 or above. Also should grant exec permission to the script.  
```
Usage: ./q1.py <ApacheLogFile>
```

Output should be in CSV format:  
```
timestamp,BAN/UNBAN,ip  
```

To get debug output, you can set DEBUG=1 as environment variable.  

You can find the rules defined in the script configuration section in JSON format:  
```
BAN_RULES=[
    {"hitCount": 40, "timeRange": 60, "banInterval": 600},
    {"hitCount": 100, "timeRange": 600, "banInterval": 3600},
    {"hitCount": 20, "timeRange": 600, "banInterval": 7200, "reqestFilter": r' /login '}
]
```

"hitCount" means the hit count of the rule within defined time range per IP.
"timeRange" refers to the time period for counting hits, should be an integer of seconds.
"reqestFilter" is optional and should be a regular expression string. If provided, it should be used as the pettern for filtering the request string in the log. 

You may change the rules to check out the results.

Important:  
This script is designed to run against static log files. To make it applicable for live stream, should adopt multi-threading for timer to trigger UNBAN instaed of the single thread loop which get time from the logs and back print UNBAN command by sequence.  

Design:
1. The script read the log file line-by-line, and keep a dict of all found IPs. Once a new IP is found, it will be added to the dict and creates hit-queues according to rules count. For the log entry hit in any rule, the relavent hit-queue will be appended with the "request" and "time". Then, it will check and discard all "expired" hits, and verify if the IP should be banned.  
2. If the IP should be banned, it will then try to push the IP into an ordered banned-list, with an expiry (current time + ban interval). While the IP exists in the list, it will check and requeue the item on expiry update. Else, insert the entry to the ordered banned-list.  
3. In parallel, the script will scan the banned list to dispatch those expired IPs and trigger unban action.  


