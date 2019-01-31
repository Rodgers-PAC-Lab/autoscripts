# Sequence of scripts to run after behavior each day
# Must be run with /bin/bash -l -c 'cd THIS_DIR; bash post_behavior.sh EXPERIMENTER'
# EXPERIMENTER can be "chris", "jung", "all", or left out
# This determines who, if anybody, gets the email
#
# Three steps:
# 1. rsync and daily update
#    writes to 'logfile' in this directory
#    rsync also has its own rsync.log
# 2. put_new
#    writes to 'logfile' in this directory
# 3. nightly_email
#    writes to 'logfile' in this directory

# chdir if it wasn't already
cd /home/autoscript/dev/autoscripts/marvin_post_behavior

# rsync and daily update
echo rsync and daily update
python rsync_and_daily_update.py >> logfile 2>&1

# put_new
echo put_new
python /home/autoscript/dev/mouse-cloud/manage.py put_new >> logfile 2>&1

# daily_email
# Pass the parameter, if any, and let nightly_email deal with it
python nightly_email.py $* >> logfile 2>&1
