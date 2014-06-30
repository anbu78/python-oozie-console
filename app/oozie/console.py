import sys
from app.oozie.client import OozieClient
from app.oozie.config import OozieConfig

import os
import yaml
import urllib2
import requests
import socket

import simplejson as json
from xml.dom import minidom
from urllib import urlencode
from urlparse import urlparse

class OozieConsole(OozieClient, OozieConfig):
    """A wrapper module for Oozie Client, to fetch and format json output specific for OozieConsole"""
    CERTS = {}

    def __init__(self, cluster=None, useproxy=0, useycacert=0):
        self.cfg = yaml.load(self.CONFIG_YAML)
        if not self.cfg.get('clusters'):
            raise OozieConsoleException("no clusters defined in config")
        self.clusters = self.cfg.get('clusters')

        if not self.cfg.get('filters'):
            raise OozieConsoleException("no filters defined in config")
        self.filters = self.cfg.get('filters')
        
        if cluster not in self.clusters.keys():
            raise OozieConsoleException("cluster: %s not defined in config" % cluster)
        self.cluster = self.clusters.get(cluster)

        self.OOZIE_URL = self.cluster.get('OOZIE_URL')

        if useproxy:
            self.OOZIE_URL = self.YCA_PROXY
            OozieClient.__init__(self, self.OOZIE_URL)
            hosthdr = urlparse(self.OOZIE_URL).netloc
            self.setHeader('Host', hosthdr)
        else:
            OozieClient.__init__(self, self.OOZIE_URL)

        if useycacert:
            cert = self.get_cert_by_appid(self.APPID)
            self.setHeader('Cert-App-Auth', cert)


    def get_jobs(self, fkey=None):
        if fkey not in self.filters.keys():
            raise OozieConsoleException("no filters defined in config")
        filter = self.filters.get(fkey)
        jobnames = filter.get('name').keys() 
        status = filter.get('status')
        user = filter.get('user')
        farg = { 'name' : jobnames, 'status' : status, 'user' : user }
        data = self.query(farg, jobtype='coord')
        return data

    def jobinfo(self, jobid):

        data = self.info(jobid)

        columns = OozieConsole.DEFAULT_COLUMNS
        if jobid.endswith('-W'):
            columns = OozieConsole.WORKFLOW_COLUMNS
        for c in columns:
            c['caption'] = c.get('caption',c.get('field'))
        cols = columns

        records = data.pop('actions')
        for r in records:
            r['recid'] = r.get('actionNumber', r.get('id'))
        retval = {'records' : records, 'columns' : cols, 'data' : data }
        return retval

    def job_submit(self, cfg):
        data = self.start(cfg)
        return data

    def job_query(self):
        cert = self.get_cert_by_appid(self.APPID)
        self.setHeader('Cert-App-Auth', cert)
        data = self.query()
        cjobs = data.get('coordinatorjobs')
        for c in cjobs:
            cjobid = c.get('coordJobId')
            print cjobid
            jinfo = self.info(cjobid)
            print jinfo

    def get_cert_by_appid(self, appid):
        if len(self.CERTS) == 0:
           self.fetch_all_certs()
        return self.CERTS.get(appid)

    def fetch_all_certs(self):
        hostname = socket.gethostname()
        cert_url = '%s/%s' % (self.YCA_API_URL, hostname)
        obj = urllib2.urlopen(cert_url)
        data = obj.read()
        xmldoc = minidom.parseString(data)
        certs = xmldoc.getElementsByTagName('certificate')

        for c in certs:
           self.CERTS[c.attributes['appid'].value] = c.childNodes[0].nodeValue

class OozieConsoleException(Exception):
    """Oozie Console Exception class"""
    def __init__(self, *arg):
        self.args = arg

class WorkflowJob():
    pass


class CoordinatorJob():
   pass

class BundleJob():
   pass
