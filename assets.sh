#!/bin/bash

# install node_modules and rebuild assets
cd build
npm install
gulp
cd ..
