[![Total alerts](https://img.shields.io/lgtm/alerts/g/alphagov/cyber-security-security-advisory-dashboard.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/alphagov/cyber-security-security-advisory-dashboard/alerts/) [![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/alphagov/cyber-security-security-advisory-dashboard.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/alphagov/cyber-security-security-advisory-dashboard/context:javascript) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/alphagov/cyber-security-security-advisory-dashboard.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/alphagov/cyber-security-security-advisory-dashboard/context:python)

# Security Advisory Dashboard 

## Prerequisites 

Check you have docker and docker-compose installed 

```
docker --version 
docker-compose --version
```

A TOKEN env var containing a read-only personal access token for a GitHub org 
admin user. 

    TODO implement secrets management for this before go live  

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

### alert_status 

For each repository call the v3 REST API to determine whether vulnerability
alerts are enabled. 
```alert_status
make alert_status
```

### dependabot_status 

Call the dependabot config API to determine which alphagov repositories
have dependabot automated PRs enabled  
```dependabot_status
make dependabot_status
```

### build_routes

Currently this just builds the /alert-status route template data file. 

The idea is that this takes the raw api response data from GitHub and 
Dependabot and builds the route json files to populate the route templates. 

```build_routes
make build_routes
```

### repo_owners

Uses the `repositoryTopics` data to allocate repositories to teams. 
```repo_owners
make repo_owners
```




## Run a local dev server 

The run task currently runs the npm install and then runs the gulp tasks 
to build the static assets, js and css. 

    TODO move the npm install into the docker build. 
    
```run
make run
```
