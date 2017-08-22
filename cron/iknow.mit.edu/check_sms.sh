#!/bin/sh

PROAREA=/var/Production
WORKON_HOME=$PROAREA/socialmobility/pinax
PROJECT_ROOT=/home/www/barter.mit.edu/knowledge/pylib/knowledge/knowledge_web

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py check_sms >> $PROJECT_ROOT/log/check_sms.log 2>&1

