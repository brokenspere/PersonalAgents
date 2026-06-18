#!/bin/bash
rm -rf test_package test_deployment.zip
mkdir -p test_package
pip3 install -r requirements.txt -t test_package/ --no-cache-dir --quiet
rm -rf test_package/boto3* test_package/botocore* test_package/s3transfer*
find test_package/ -type d -name "__pycache__" -exec rm -rf {} +
find test_package/ -type d -name "*.dist-info" -exec rm -rf {} +
find test_package/ -type d -name "tests" -exec rm -rf {} +
rm -rf test_package/pandas/tests
rm -rf test_package/numpy/tests
rm -rf test_package/numpy/core/tests
du -sh test_package
cd test_package
zip -q -r ../test_deployment.zip .
cd ..
ls -lh test_deployment.zip
