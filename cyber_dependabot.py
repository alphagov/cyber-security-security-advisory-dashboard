import requests
import os
import json
from pprint import pprint
from addict import Dict


ROOT_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f'token {os.environ.get("SP_TOKEN", "")}',
    # "Accept": "application/vnd.github.baptiste-preview+json",
    "Accept": "application/vnd.github.dorian-preview+json",
}


def get(path):
    return requests.get(f"{ROOT_URL}{path}", headers=HEADERS)


def put(path, data=None):
    return requests.put(f"{ROOT_URL}{path}", headers=HEADERS)


def enable_vulnerability_alerts():
    today = datetime.date.today().isoformat()
    with open(f"output/{today}/repositories.json", "r") as f:
        repos = json.load(f)

    repos = [Dict(r) for v in repos.values() for r in v]

    langs = set([lang.name for repo in repos for lang in repo.languages.nodes])
    print(langs)
    raise
    for repo in repos:
        # pprint(repo.name)
        if "cyber" in repo.name or "cst" in repo.name or "csw" in repo.name:
            # if not repo.vulnerabilityAlerts.edges:
            #    continue
            # package_manager = repo.vulnerabilityAlerts.edges[0].node.vulnerableManifestPath
            # print(f'name: {repo.name}, manifest: {package_manager}')
            # language = repo.languages.nodes[0]
            # print(language)
            update_confid(repo)
            # if "cyber-security-splunk-onboarding" in repo.name:
            # pprint(repo.name)
            # r = get(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
            # print(r.status_code, r.text)
            # r = put(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
            # print(r.status_code, r.text)
            # r = get(f"/repos/{repo.owner.login}/{repo.name}/vulnerability-alerts")
            # print(r.status_code, r.text)


def get(path):
    root_url = "https://api.dependabot.com"
    headers = {"Authorization": "Personal %s" % config.get_value("token")}

    url = root_url + path
    response = requests.get(url, headers=headers)
    return response


def update_confid(repo):
    if not repo.languages.nodes:
        print(repo)
        return

    language = repo.languages.nodes[0].name
    print(language)

    # One of bundler, composer, docker, maven, npm_and_yarn,
    # elm, submodules, hex, cargo, gradle, nuget, dep, go_modules,
    # pip, terraform, github_actions
    # ['Vim script', 'C#', 'Go', 'Ruby', 'C', 'Pascal', 'Scheme', 'Protocol Buffer', 'CoffeeScript',', 'Assembly', 'ApacheConf', 'Dockerfile', 'Batchfile', 'Ragel', 'TypeScript', 'Perl', 'HCL', 'C++', 'Inno Setup', 'Liquid', 'Elixir', 'R', 'PowerShell', 'Java', 'sed', 'Cycript', 'PLpgSQL, 'Scala', 'Clojure', 'FreeMarker', 'Awk', 'Mako']
{
    "Vim script": "",
    "C#": "",
    "Go": "",
    "Ruby": "",
    "C": "",
    "Pascal": "",
    "Scheme": "",
    "Protocol Buffer": "",
    "CoffeeScript": "",
    "Yacc": "",
    "JavaScript": "",
    "Lua": "",
    "TSQL": "",
    "Visual Basic": "",
    "PLSQL": "",
    "JSONiq": "",
    "API Blueprint": "",
    "Python": "",
    "Makefile": "",
    "Assembly": "",
    "ApacheConf": "",
    "Dockerfile": "",
    "Batchfile": "",
    "Ragel": "",
    "TypeScript": "",
    "Perl": "",
    "HCL": "",
    "Nix": "",
    "Jsonnet": "",
    "ASP": "",
    "Shell": "",
    "PHP": "",
    "Puppet": "",
    "Emacs Lisp": "",
    "Gherkin": "",
    "Handlebars": "",
    "Smarty": "",
    "Logos": "",
    "C++": "",
    "Inno Setup": "",
    "Liquid": "",
    "Elixir": "",
    "R": "",
    "PowerShell": "",
    "Java": "",
    "sed": "",
    "Cycript": "",
    "PLpgSQL": "",
    "XSLT": "",
    "Haskell": "",
    "Nginx": "",
    "Lex": "",
    "Roff": "",
    "Groovy": "",
    "Tcl": "",
    "Jupyter Notebook": "",
    "CSS": "",
    "HTML": "",
    "VCL": "",
    "M4": "",
    "Scala": "",
    "Clojure": "",
    "FreeMarker": "",
    "Awk": "",
    "Mako": "",
}



    package_managers = {
        "Ruby": "bundler",
        "Python": "pip",
        "JavaScript": "npm_and_yarn",
        "Dockerfile": "docker",
        "Terraform": "terraform",
        "HCL": "terraform",
        "Makefile": None,
        "Java": "maven",
    }

    # https://github.com/dependabot/api-docs
    # https://api.github.com/repositories/1599151
    config = {
        "repo-id": repo.databaseId,
        "update-schedule": "daily",
        "directory": "/",
        "account-id": "596977",
        "account-type": "org",
        "package-manager": package_managers.get(language),
    }
    #print(config)
    # requests.post(root_url + "/update_configs", headers=headers, json=config)


enable_vulnerability_alerts()
# https://github.com/alphagov/cst-aws-pocs
# https://github.com/alphagov/cyber-security-splunk-onboarding/settings
# https://github.com/alphagov/cyber_security_terraform_red_weed/network/dependencies/vulnerabilities/enable_updates
