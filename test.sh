#! /bin/bash

directory="$1"

vars="TOKEN GITHUB_ORG AWS_ACCESS_KEY_ID "
vars+="AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_SECURITY_TOKEN"

for i in ${vars}; do
    if [ -z "${!i}" ]; then
        echo "Unsetting empty variable: ${i}"
        unset "${i}"
    fi
done

black .

py.test \
    --capture=no \
    --verbose \
    -vv \
    --showlocals \
    -r a \
    --cov=. \
    --cov-report html \
    --cov-fail-under 20 \
    --flake8 \
    --random-order \
    ${directory}
