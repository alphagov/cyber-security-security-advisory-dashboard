[![Total alerts](https://img.shields.io/lgtm/alerts/g/alphagov/cyber-security-security-advisory-dashboard.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/alphagov/cyber-security-security-advisory-dashboard/alerts/) [![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/alphagov/cyber-security-security-advisory-dashboard.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/alphagov/cyber-security-security-advisory-dashboard/context:javascript) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/alphagov/cyber-security-security-advisory-dashboard.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/alphagov/cyber-security-security-advisory-dashboard/context:python)

# Security Advisory Dashboard 

## Prerequisites 

Check you have docker and docker-compose installed 

```
docker --version 
docker-compose --version
```

A GITHUB_ORG env var containing the organisation login short name 
from the GitHub URL.

A TOKEN env var containing a read-only personal access token for a GitHub org 
admin user. 

Alternatively the token can be retrieved from SSM if the make command 
is run via aws-vault or similar to set AWS credentials.  

Create or change the `settings.[env].json` file 

## Setup 

Run the make task to build the container image. 

This extends the python3 base image and installs the pip requirements 
as well as installing node, npm and gulp. 
```container
make rebuild
```

## Run the cli tasks to build the data 

### audit

Gets the paged repository data with vulnerability alerts  
```audit
make audit
```

The audit process runs the api calls to collect vulnerability and 
activity data from github as well as the dependabot config API to 
determine which repositories have dependabot enabled. 

### alert_status 

For each repository call the v3 REST API to determine whether vulnerability
alerts are enabled. 
```alert_status
make alert_status
```

This task has been kept separate because currently it takes too long 
to run. 

## Run a local dev server 

The run task currently runs the npm install and then runs the gulp tasks 
to build the static assets, js and css. 

    TODO move the npm install into the docker build. 
    
```run
make run
```
