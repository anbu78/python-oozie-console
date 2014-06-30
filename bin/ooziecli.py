#!/bin/env python2.7
import os
import sys
import fnmatch
import requests
import socket
import argparse
from xml.dom import minidom
from urlparse import urlparse
sys.path.append('.')
from app.helpers.hdfsproxy import HdfsProxy
from app.oozie.console import OozieConsole

CERTS = {}
APPID = 'app.griduser.aga_se'
YCA_PROXY = 'https://proxy.example.com/'
YCA_API_URL = 'http://ca.example.com:4080/wsca/v1/certificates'

def main():
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # create the parser for the "copy" command
    cmd_copy = subparsers.add_parser('copy')
    cmd_copy.add_argument('--proxy', dest="proxy", help='Hdfs Proxy Url', action="store")
    cmd_copy.add_argument('--src', dest="src", help='NFS source path', action="store")
    cmd_copy.add_argument('--dest', dest="dest", help='HDFS destination path', action="store")

    args = parser.parse_args()

    buildtime = args.src.split('/')[-1].split('-')[-1]
    copyToHdfs(args.proxy, args.src, args.dest)
    for file in find_files(args.src, 'job.properties'):
        if os.path.isfile(file):
            jobSubmit(file, buildtime)

def copyToHdfs(proxy, src, dest):
    cert = get_cert_by_appid(APPID)
    basedir = os.path.basename(src)
    dirname = os.path.dirname(src)
    hostgrid = urlparse(proxy).netloc
    headers = {'Cert-App-Auth' : cert, 'Host' : hostgrid}
    hpxy = HdfsProxy(YCA_PROXY, headers=headers)
    for file in find_files(src):
        print "-" * 100
        remotedir = dest + file.replace(dirname, '')
        if os.path.isdir(file):
            url = proxy + dest + remotedir + '?op=mkdir&permission=750'
            #if not hpxy.exists(remotedir):
            hpxy.mkdir(remotedir)
        elif os.path.isfile(file):
            url = proxy + dest + remotedir + '?op=create&overwrite=true'
            #if not hpxy.exists(remotedir):
            hpxy.create(remotedir, data=open(file,'rb').read())
        else:
            print 'file=%s : unknown format' % file

    hpxy.close()

def jobSubmit(cfg, buildtime):
    tmpl = '''<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <property>
        <name>user.name</name>
        <value>aga_se</value>
    </property>
'''
    content = [tmpl]
    print "cfg: %s" % cfg
    for line in open(cfg, 'r').readlines():
        line = line.rstrip('\n').strip(" ")
        if not len(line): continue
        k, v = line.split('=')
        v = v.replace('{__build_timestamp__}', buildtime)
        content.append('''
    <property>
        <name>%s</name>
        <value>%s</value>
    </property>
''' % (k.strip(),v.strip()))
    content.append('</configuration>')
    data = "".join(content)
    oc = OozieConsole(useproxy=0, useycacert=1)
    print data
    print oc.job_submit(data)
    
    
def find_files(directory, pattern='*'):
    for root, dirs, files in os.walk(directory):
        yield root
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def get_cert_by_appid(appid):
    if len(CERTS) == 0:
       fetch_all_certs()

    return CERTS.get(appid)

def fetch_all_certs():
    hostname = socket.gethostname()
    cert_url = '%s/%s' % (YCA_API_URL, hostname)
    obj = requests.get(cert_url)
    data = obj.text
    xmldoc = minidom.parseString(data)
    certs = xmldoc.getElementsByTagName('certificate')

    for c in certs:
       CERTS[c.attributes['appid'].value] = c.childNodes[0].nodeValue

if __name__ == '__main__':
    main()
