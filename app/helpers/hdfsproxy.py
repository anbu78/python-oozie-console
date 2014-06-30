import errno
import logging
import requests
import posixpath as ppath
from xml.dom import minidom
import stat
import time

DEFAULT_READ_SIZE = 1024*1024 # 1MB

class HdfsProxy():
  """
  HdfsProxy implements the filesystem interface via the HdfsProxy rest protocol.
  """
  DEFAULT_USER = 'aga_se'
  DEFAULT_FS = '/fs'

  def __init__(self, proxyurl, headers=None, cert=None, sslverify=False):
    self._url = proxyurl.rstrip('/') + self.DEFAULT_FS 
    self._headers = headers if headers else {}
    self._sslverify = sslverify
    self._cert = cert
    logging.basicConfig(level=logging.DEBUG)
    self.logging = logging.getLogger('hdfsproxy')

  @property
  def url(self):
    return self._cert

  @property
  def sslverify(self):
    return self._sslverify

  @property
  def headers(self):
    return self._headers

  @property
  def cert(self):
    return self._cert

  @property
  def defaultfs(self):
    return self.DEFAULT_FS

  @property
  def user(self):
    return self.DEFAULT_USER

  def _call(self, method='GET', path=None, **kwargs):
    hdfs_url = self.get_hdfs_path(path)
    params = kwargs['params']
    r = requests.request(method, hdfs_url, headers=self._headers, verify=self._sslverify, **kwargs)
    self.logging.info(r.url)
    if r.status_code == requests.codes.ok:
        return r.text
    return None

  def get_hdfs_path(self, path=None):
    normpath = ppath.normpath(path) if path else ''
    return '%s%s' % (self._url, normpath)

  def content_summary(self, path):
    """
    content_summary(path): get content summary of a directory or a file
    This is the equivalent of hadoop fs -count command.
    """
    params['op'] = 'contentSummary'
    return self._call('GET', path, params=params)

  def check_sum(self, path):
    """
    check_sum(path): get checksum of the file
    """
    params = {'op' : 'fileChecksum'}
    return self._call('GET', path, params=params)

  def status(self, path, recursive=False):
    """
    status(path, recursive=False):
           recursive - Optional. Requires a boolean value. Default is false. 
    return: Provides a recursive listing of the directory. 
    """
    params = {'op' : 'status'}
    if recursive: params['recursive'] = 'true'
    return self._call('GET', path, params=params)

  def exists(self, path):
    return self.status(path) is not None

  def delete(self, path, recursive=False, skipTrash=True):
    """
    delete(path, recursive=False, skipTrash=True) Delete a file or directory.
    """
    params = {'op' : 'delete'}
    if recursive: params['recursive'] = 'true'
    if skipTrash: params['skipTrash'] = 'true'
    return self._call('PUT', path, params=params)

  def mkdir(self, path, permission='755'):
    """
    mkdir(path, mode=None, permission=755) Creates a directory and any parent directory if necessary.
    """
    params = {'op' : 'mkdir', 'permission' : permission}
    return self._call('PUT', path, params=params)

  def rmdir(self, path, skipTrash=False):
    """
    rmdir(path, skipTrash=False): Delete a directory.
    """
    return self.delete(path, skipTrash=skipTrash)

  def chmod(self, path, permission='750', recursive=False):
    """
    chmod(path, permission, recursive=False): change permission for the hdfs directory
    """
    params = {'op' : 'chmod', 'permission' : permission}
    if recursive: params['recursive'] = 'true'
    return self._call('PUT', path, params=params)

  def chgrp(self, path, group='users', recursive=False):
    """
    chgrp(path, group='users', recursive=False): change group for the hdfs directory
    """
    params = {'op' : 'chgrp', 'group' : group}
    if recursive: params['recursive'] = 'true'
    return self._call('PUT', path, params=params)

  def chown(self, path, owner, group='users', recursive=False):
    """
    chown(path, owner, group='users', recursive=False): change ownership for the hdfs directory
    """
    params = {'op' : 'chmod', 'permission' : permission}
    if recursive: params['recursive'] = 'true'
    return self._call('PUT', path, params=params)

  def put(self, **kwargs):
    """
    put(path, overwrite=False, blocksize=None, replication=None, permission='750')
    An alias to create function
    """
    return self.create(**kwargs)

  def create(self, path, overwrite=False, blocksize=None,
             replication=None, permission='750', data=None):
    """
    create(path, overwrite=False, blocksize=None, replication=None, permission='750', data=None)
    Creates a file with the specified parameters.
    """
    params = {'op' : 'create', 'permission' : permission}
    if overwrite: params['overwrite'] = 'true'
    if blocksize: params['blocksize'] = long(blocksize)
    if replication: params['replication'] = int(replication)
    self._headers['Content-Type'] = 'application/octet-stream'
    return self._call('PUT', path, params=params, data=data)

  def close(self):
    """
    close(path): to close the filesystem handle created for that user
    """
    params = {'op' : 'close'}
    return self._call('PUT', path=None, params=params)
    pass

  def stream(self, path):
    """
    stream(path): to download a file from HDFS
    """
    #TODO: yet to implement
    pass

  def append(self, path):
    """
    append(path): append content to a file in HDFS
    """
    #TODO: yet to implement
    pass

  def move(self, path, dest):
    """
    move(path, dest): move directory to new destination 
    """
    params = {'op' : 'move'}
    return self._call('PUT', path, params=params)

  def xml2dict(self, xmlstr):
    """
    xml2dict(xmlstr): convert xml string to dict object
    """
    dom = minidom.parseString(xmlstr)
    dictobj = dict()
    if dom.nodeType == dom.TEXT_NODE:
        dictobj['data'] = dom.data
    if dom.nodeType not in [dom.TEXT_NODE, dom.DOCUMENT_NODE,
                                dom.DOCUMENT_TYPE_NODE]:
        for item in dom.attributes.items():
            dictobj[item[0]] = item[1]
    if dom.nodeType not in [dom.TEXT_NODE, dom.DOCUMENT_TYPE_NODE]:
        for child in dom.childNodes:
            child_name, child_dict = self.xml2dict(child)
            if child_name in dictobj:
                try:
                    dictobj[child_name].append(child_dict)
                except AttributeError:
                    dictobj[child_name] = [dictobj[child_name], child_dict]
            else:
                dictobj[child_name] = child_dict
    return dictobj
 
