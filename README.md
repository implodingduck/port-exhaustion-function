# Port Exhaustion
KQL Query
'''
traces | where message has 'Number of ports used'
| extend numports = toint(split(message, ": ")[1])
| project numports, timestamp, cloud_RoleName
| render timechart 
'''
