# rsync the video data from shrimp to cuttlefish
#
# Run like this:
# /bin/bash -l -c 'cd /home/mouse/dev/autoscripts/shrimp_nightly_rsync; python3 shrimp_nightly_rsync.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct

# Announce the start and start time
print("---------------")
print("AUTORUN_START__")
import datetime
import os
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_START_FILE {}".format(os.path.abspath(__file__)))

# Rest of imports
import sys

# rsync will be called with this logfile
logfile = 'nightly_rsync.log'

# rsync -va /media/mouse/windows/Users/mouse/Videos /home/mouse/mnt/cuttlefish/behavior/videos/e3vision
# Check that it's actually mounted before running
check_cuttlefish_mount_dir = '/home/mouse/mnt/cuttlefish'
if not os.path.ismount(check_cuttlefish_mount_dir):
    raise IOError("This must be mounted: %s" % check_cuttlefish_mount_dir)

# This is where output goes
output_dir = os.path.join(
    check_cuttlefish_mount_dir, 'shrimp')

# Copy behavior
input_dir = '/home/mouse/Videos'
cmd = 'rsync -va --log-file=%s %s %s' % (
    logfile, input_dir, output_dir)
print("rsync : %s" % str(datetime.datetime.now()))
print(cmd)
sys.stdout.flush() # to maintain the order of print and os.system in the logfile
os.system(cmd)

# Print stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_STOP__")
