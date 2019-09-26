#!/usr/bin/env python3
import os
import serverless_wsgi
import logging as log

from app import app
log.error("frontend_lambda called")

def lambda_handler(event, context):
    sk = os.getenv("SECRET_KEY", "FALSE")
    if sk is not "FALSE":
        log.error(f"Key starts with: {sk[0:2]}")
        app.server_key = sk
        app.config["SECRET_KEY"] = sk


    log.error("Invoking flask via serverless_wsgi")
    return serverless_wsgi.handle_request(app, event, context)


# if __name__ == "__main__":
#     app.secret_key = "notrandomkey"
#     app.config["ENV"] = "development"
#     app.config["TESTING"] = True
#     app.config["DEBUG"] = True
#     app.config["verify_oidc"] = True
#     app.run(port=5000)
