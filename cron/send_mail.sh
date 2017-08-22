#!/bin/sh

PROAREA=/var/Production
WORKON_HOME=$PROAREA/socialmobility/pinax
PROJECT_ROOT=$PROAREA/socialmobility/knowledge/pylib/knowledge/knowledge_web

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py send_mail >> $PROJECT_ROOT/log/cron_mail.log 2>&1

