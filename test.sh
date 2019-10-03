#! /bin/bash

vars="TOKEN GITHUB_ORG AWS_ACCESS_KEY_ID "
vars+="AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN"

for i in ${vars}; do
    if [ -z "${!i}" ]; then
        echo "Unsetting empty variable: ${i}"
        unset "${i}"
    fi
done

py.test \
    --capture=no \
    --verbose \
    --showlocals \
    -r a \
    --cov=. \
    --cov-report html \
    --cov-fail-under 70 \
    --flake8 \
    --black \
    --random-order \
    tests
