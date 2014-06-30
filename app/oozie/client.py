import os
import logging
import requests
import simplejson as json
from urllib import urlencode
from app import app

class OozieClient:

    def __init__(self, url=None):
        """
        OozieClient: Oozie webservices api bindings
        """
        if url is None:
            self.baseUrl = os.environ.get('OOZIE_URL', self.OOZIE_URL)
        else:
            self.baseUrl = url
        logging.basicConfig(level=logging.INFO)
        self.headers = {}
        self.logger = logging.getLogger('oozie.client')
        self.logger.info('OozieClient object created successfully')

    def _call(self, endpoint='jobs', params=None):
        """
        Query Oozie Webservice API 
        @return json output
        """
        wsurl = self.buildUrl(endpoint, params)
        data = {}

        self.logger.info('Oozie WS Url: %s' % wsurl)
        r = requests.get(wsurl, headers=self.headers, verify=False)
        self.logger.debug("status=%d, url: %s" % (r.status_code, r.url))

        if r.status_code == requests.codes.ok:
            data = r.text

        return json.loads(data)

    def buildUrl(self, endpoint='jobs', params=None):
        """
        Return the Oozie URL constructed with available variables and parameters
        """
        urlparams = self.buildParams(params)
        urlparams = '?%s' % urlparams if urlparams != None else  ""
        url = '%s/%s%s' % (self.baseUrl, endpoint, urlparams)
        self.logger.info('Building Url: %s' % url)
        return url

    def buildParams(self, params=None):
        """
        Return query params built from given dictionary
        """
        urlparams = urlencode(params, doseq=True)
        return urlparams

    def getOozieUrl(self):
        """
        Return the Oozie URL of the workflow client instance
        """
        return self.baseUrl
    
    def setHeader(self, name, value):
        """
        Set a HTTP header to be used in the WS requests by the oozie instance
        """
        self.headers[name] = value
        self.logger.info('Adding Headers: (%s: %s)' % (name, value))

    def query(self, filter, jobtype='coord', user=None):
        """
        Return Bundle job id info
        """
        # jobs = ['btdac-slingshot_di_dac_cat_tool_gen-daily', 'btdac-slingshot_di_dac_eoo-daily']
        # filter = { 'status': ['RUNNING','RUNNINGWITHERROR','PREP'], 
        #            'name' : jobs,
        #          }
        l = []
        for k in filter.keys():
            v = filter[k]
            if isinstance(v, list) or isinstance(v, tuple):
                l.append(";".join([k + '=' + v1 for v1 in v]))
            else:
                l.append(k + '=' + v)
        params = { 'filter' : ";".join(l), 'jobtype' : jobtype }
        return self._call('jobs', params) 

    def info(self, jobid, offset=0, len=1000, order='desc'):
        """
        Return job id info irrespective of wf, coord or bundle
        """
        endpoint = 'job/%s' % jobid
        params = {'offset' : offset, 'len' : len, 'order' : order}
        return self._call(endpoint, params)

    def start(self, cfg):
        """
        Submit and start the job
        """
        endpoint = 'jobs'
        params = {}#{'action' : 'run'}
        wsurl = self.buildUrl(endpoint, params)
        data = {}
        self.headers['content-type'] = 'application/xml;charset=UTF-8'
        self.logger.info('Oozie WS Url: %s' % wsurl)
        r = requests.post(wsurl, headers=self.headers, allow_redirects=True, verify=False, files={'file':('job.xml',cfg,)})
        self.logger.info("status=%d, url: %s" % (r.status_code, r.url))

        if r.status_code == requests.codes.ok:
            data = r.text
        print data
        #return json.loads(data)

    def suspend(self, jobid):
        """
        Suspend the job id 
        """
        endpoint = 'job/%s' % jobid
        params = {'action' : 'suspend'}
        return self._call(endpoint, params)

    def resume(self, jobid):
        """
        Resume the job id 
        """
        endpoint = 'job/%s' % jobid
        params = {'action' : 'resume'}
        return self._call(endpoint, params)

    def kill(self, jobid):
        """
        Kill the job id 
        """
        endpoint = 'job/%s' % jobid
        params = {'action' : 'kill'}
        return self._call(endpoint, params)

    def wfJobInfo(self, jobid):
        """
        Return Workflow job id info
        """
        pass

    def coordJobInfo(self, jobid):
        """
        Return Coordinator job id info
        """
        pass

    def bundleJobInfo(self, jobid):
        """
        Return Bundle job id info
        """
        pass
