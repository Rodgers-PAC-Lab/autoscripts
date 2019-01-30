# Analyzes behavioral data for the day
#
# Run like this:
# /bin/bash -l -c 'cd /home/mouse/scripts/auto/post_behavior; python rsync_and_daily_update.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct

# Announce the start and start time
print "AUTORUN_START rsync_and_daily_update"
import datetime
print "AUTORUN_START_TIME : %s" % str(datetime.datetime.now())

# Rest of imports
import os
import sys
import MCwatch.behavior

# Should check that it's actually mounted before running
#output_dir = '/home/mouse/mnt/nas2_home'
output_dir = '/mnt/behavior'
if not os.path.ismount(output_dir):
    raise IOError("Not a mount: %s" % output_dir)

# run rsync and log results
logfile = '/home/autoscript/scripts/auto/post_behavior/rsync.log'
input_dir = '/home/mouse/sandbox_root'
#output_dir = '/home/mouse/mnt/nas2_home/behavior'
output_dir = '/mnt/behavior'
cmd = 'rsync -rt --exclude="TO_DEV" --log-file=%s %s %s' % (logfile, input_dir, output_dir)
print "rsync : %s" % str(datetime.datetime.now())
print cmd
sys.stdout.flush() # to maintain the order of print and os.system in the logfile
os.system(cmd)

# Run the updates etc
print "daily update : %s" % str(datetime.datetime.now())
MCwatch.behavior.daily_update.daily_update()

# Print stop time
print "AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now())
