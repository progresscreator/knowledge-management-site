#!/bin/sh

PROAREA=/var/Production
WORKON_HOME=$PROAREA/socialmobility/pinax
PROJECT_ROOT=/home/www/iknow.mit.edu/knowledge/pylib/knowledge/knowledge_web

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py emit_notices >> $PROJECT_ROOT/log/cron_notices.log 2>&1

