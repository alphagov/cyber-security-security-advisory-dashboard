#!/bin/bash

# install node_modules and rebuild assets
cd build
npm install
gulp
rm -rf node_modules package-lock.json
cd ..

