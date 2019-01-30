# Sequence of scripts to run after behavior each day
# Must be run with /bin/bash -l -c 'cd THIS_DIR; THIS_SCRIPT'
# Three steps:
# 1. rsync and daily update
#    writes to 'logfile' in auto/post_behavior
#    rsync also has its own rsync.log
# 2. put_new
#    writes to 'put_new.log' in auto/post_behavior
#    Should be 'logfile' but haven't made this consistent yet
# 3. nightly_email
#    writes to 'logfile'

# everything is in post_behavior
cd /home/autoscript/scripts/auto/post_behavior

# rsync and daily update
echo rsync and daily update
python rsync_and_daily_update.py >> logfile 2>&1

# put_new
echo put_new
python /home/mouse/dev/mouse-cloud/manage.py put_new >> put_new.log 2>&1

# daily_email
if [[ $* == *--email* ]]
  then
    echo nightly_email
    python nightly_email.py >> logfile 2>&1
fi
