"awssh" is the bash script for ssh to an AWS EC2 server.

To execute the script, you should ensure the environment is installed with aws cli with proper configuration.
```
Usage: ./awssh <tag>
```

Output (host found):
```
Public IP: 18.167.51.113
(execute 'ssh ec2-user@18.167.51.113')
```

Output (host not found):
```
Host not found.
```

Design:
1. The script use aws cli to lookup the public property
2. The script then execute ssh command 

