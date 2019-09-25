#!/bin/bash

# clean up previous run
rm -rf build/.package build/*.zip build/.package build/node_modules build/package-lock.json static

# make package folders
mkdir -p build/.package/static
mkdir -p build/.package/templates
mkdir -p build/.package/query

# install node_modules and rebuild assets
cd build
npm install
gulp
cd ..

# copy python source and assets
cp *.py build/.package
cp -R static/* build/.package/static/
cp -R templates/* build/.package/templates/
cp -R query/* build/.package/query/

# install requirements
# bash -c "echo -e '[install]\nprefix=\n' > setup.cfg"
pip3 install -r requirements.txt -t build/.package

# zip output
cd build/.package
zip -9 ../github_audit_lambda_package.zip -r .

# tidy up
cd ../..
rm -rf build/.package build/node_modules build/package-lock.json