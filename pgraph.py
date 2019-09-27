import os
import logging as log
from string import Template

from addict import Dict
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from jinja2 import Template


import config


url = "https://api.github.com/graphql"


api_token = config.get_value("token")

transport = RequestsHTTPTransport(
    url=url,
    use_json=True,
    headers={
        "Authorization": "Bearer %s" % api_token,
        "Accept": "application/vnd.github.vixen-preview+json",
    },
)


def query(name, **kwargs):
    log.error(f"Calling query {name}.graphql with token starting {api_token[0:4]}")
    client = Client(transport=transport, fetch_schema_from_transport=True)
    queries = {}
    for filename in os.listdir("query"):
        with open(f"query/{filename}") as query_file:
            queries[filename.split(".")[0]] = query_file.read()
    query_template = Template(queries[name])
    full_query = query_template.render(**kwargs)
    query = gql(full_query)
    return Dict(client.execute(query))
