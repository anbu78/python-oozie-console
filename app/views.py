from flask import render_template, jsonify, request, url_for
from app import app
from app.oozie.console import OozieConsole

USE_PROXY = 1
USE_YCA_CERT = 1

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/grid/<cluster>/<jobid>/')
def get_job_info(cluster, jobid):
    apiurl = url_for('api_job_info', cluster=cluster, jobid=jobid)

    columns = OozieConsole.DEFAULT_COLUMNS
    if jobid.endswith('-W'):
        columns = OozieConsole.WORKFLOW_COLUMNS
    cols = [ {'field': f } for f in columns ]

    tmpldata = {'jobid' : jobid,
                'apiurl' : apiurl}

    return render_template('grid.html', **tmpldata)

@app.route('/config/', methods = ['GET'])
def config():
    tmpldata = {}
    return render_template('config.html', **tmpldata)

@app.route('/config/update', methods = ['PUT'])
def update_config():
    pass
#
# Oozie Webservice Api calls
#

# TODO: add gridname to the route to access multiple grid
#       eg: /api/v1/<grid>/jobs/
#
@app.route('/api/v1/<cluster>/jobs/<fkey>/', methods = ['GET', 'POST'])
def api_get_jobs(cluster=None, fkey=None):
    console = OozieConsole(cluster, useproxy=USE_PROXY, useycacert=USE_YCA_CERT)
    jobs = console.get_jobs(fkey)
    return jsonify(jobs)

@app.route('/api/v1/<cluster>/job/<jobid>/', methods = ['GET', 'POST'])
@app.route('/api/v1/<cluster>/job/<jobid>/info', methods = ['GET', 'POST'])
def api_job_info(grid=None, jobid=None):
    console = OozieConsole(cluster, useproxy=USE_PROXY, useycacert=USE_YCA_CERT) 
    data = console.jobinfo(jobid)
    return jsonify(data)

