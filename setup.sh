#!/usr/bin/bash

rm -rf env
python3 -m venv env
source env/bin/activate
pip install --upgrade setuptools pip -r requirements.txt
