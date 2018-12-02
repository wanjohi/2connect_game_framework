#!/usr/bin/env bash

rm game_framework.zip
mkdir dist
cp framework.py dist/
cp lambda_function.py dist/
cp -R venv/lib/python3.7/site-packages/* dist/
cd dist
zip -r game_framework.zip *
cd ../
mv dist/game_framework.zip .
rm -rf dist