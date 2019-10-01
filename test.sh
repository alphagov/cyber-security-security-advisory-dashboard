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
    tests
