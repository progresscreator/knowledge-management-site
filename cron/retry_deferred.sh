#!/bin/sh

PROAREA=/var/Production
WORKON_HOME=$PROAREA/socialmobility/pinax
PROJECT_ROOT=$PROAREA/socialmobility/knowledge/pylib/knowledge/knowledge_web

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py retry_deferred >> $PROJECT_ROOT/log/cron_retry.log 2>&1

