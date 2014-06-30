

class OozieConfig():
    APPID = 'app.griduser.aga_se'
    YCA_PROXY = 'https://proxy.example.com/oozie/v2'
    YCA_API_URL = 'http://ca.example.com:4080/wsca/v1/certificates'
    DEFAULT_COLUMNS = [ {'field': 'actionNumber',
                         'size' : '5%', 
                         'caption' : 'Id' },
                        {'field': 'externalId', 
                         'size' : '25%' }, 
                        {'field': 'createdTime', 
                         'size' : '18%' }, 
                        {'field': 'lastModifiedTime', 
                         'size' : '18%' }, 
                        {'field': 'nominalTime', 
                         'size' : '18%'},
                        {'field': 'status', 
                         'size' : '10%'},
                        {'field': 'errorMessage', 
                         'size' : '20%' }
                       ]
    WORKFLOW_COLUMNS = DEFAULT_COLUMNS
    CONFIG_YAML = '''
---
clusters:
   DR:
     desc: Dilithium Red
     OOZIE_URL: https://dilithiumred-oozie.red.cluster.example.com:4443/oozie/v2/
   DB:
     desc: Dilithium Blue
     OOZIE_URL: https://dilithiumblue-oozie.blue.cluster.example.com:4443/oozie/v2/
   PT:
     desc: Phazon Tan
     OOZIE_URL: https://phazontan-oozie.tan.cluster.example.com:4443/oozie/v2/

status: &STATUS [ SUCCEEDED, RUNNING, RUNNINGWITHERROR ]

filters:
   dapper:
      jobtype: coord
      user:
        - p_dapr
      name: &dapper
        zest-cobchecker-5mins : { failchk : 1, failchkmax : 20 }
        dapper-groupImp-hourly :
        dapper-campaignMetrics-daily :
      status: *STATUS
   dapper1:
      name: *dapper
      status: *STATUS
'''
