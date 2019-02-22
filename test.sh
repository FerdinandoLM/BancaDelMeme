#!/bin/bash

TEST_ENV=.testenv

if [ ! -d $TEST_ENV ]; then
  # set up virtual environment
  python -m venv $TEST_ENV
  if [ -f $TEST_ENV/bin/activate ]; then
    source $TEST_ENV/bin/activate
  else
    source $TEST_ENV/Scripts/activate
  fi

  # install deps
  pip install -r requirements.txt
  pip install coverage
else
  # just activate virtual environment
  if [ -f $TEST_ENV/bin/activate ]; then
    source $TEST_ENV/bin/activate
  else
    source $TEST_ENV/Scripts/activate
  fi
fi

# load envvars
export CONFIG=cfg_test.json

# run tests
coverage run --branch --source=src -m unittest discover --start=test --pattern=*.py && \
  coverage report && \
  coverage html
