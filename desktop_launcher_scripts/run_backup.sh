#python3 /home/mouse/dev/autoscripts/shrimp_nightly_rsync/shrimp_nightly_rsync.py
echo Starting backup. If this window closes immediately, something went wrong!
sleep 2
/bin/bash -l -c 'cd /home/mouse/dev/autoscripts/shrimp_nightly_rsync; python3 shrimp_nightly_rsync.py |& tee -a logfile'
echo Backup complete. Press enter to close window. DO NOT LEAVE OPEN!
read
