# rsync the behavior, ps3 videos, and neural data from nivram to NAS
#
# Run like this:
# /bin/bash -l -c 'cd /home/mouse/scripts/auto/post_behavior; python nightly_rsync.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct

# Announce the start and start time
print "AUTORUN_START nightly_rsync"
import datetime
print "AUTORUN_START_TIME : %s" % str(datetime.datetime.now())

# Rest of imports
import os
import sys

# rsync will be called with this logfile
logfile = 'nightly_rsync.log'

# Check that it's actually mounted before running
nas2_home_output_dir = '/mnt/nas2_home'
nas2_behavior_output_dir = '/mnt/behavior'
if not os.path.ismount(nas2_home_output_dir):
    raise IOError("Not a mount: %s" % nas2_home_output_dir)
if not os.path.ismount(nas2_behavior_output_dir):
    raise IOError("Not a mount: %s" % nas2_behavior_output_dir)

# Copy behavior
input_dir = '/home/chris/sandbox_root'
cmd = 'rsync -rtv --exclude="TO_DEV" --log-file=%s %s %s' % (logfile, input_dir, 
    nas2_behavior_output_dir)
print "rsync : %s" % str(datetime.datetime.now())
print cmd
sys.stdout.flush() # to maintain the order of print and os.system in the logfile
os.system(cmd)

# Copy ps3 video
input_dir = '/home/chris/Videos'
cmd = 'rsync -rtvl --log-file=%s %s %s' % (logfile, input_dir, 
    os.path.join(nas2_home_output_dir, 'ps3eye', 'nivram'))
print "rsync : %s" % str(datetime.datetime.now())
print cmd
sys.stdout.flush() # to maintain the order of print and os.system in the logfile
os.system(cmd)

#~ # Copy whisker_video
#~ input_dir = '/home/chris/whisker_video/'
#~ cmd = 'rsync -rtv --log-file=%s %s %s' % (logfile, input_dir, 
    #~ os.path.join(output_dir, 'whisker', 'processed/'))
#~ print cmd
#~ with file(logfile, 'a') as fi:
    #~ fi.write("running: %s\n" % cmd)
#~ os.system(cmd)

# Copy data
input_dir = '/home/chris/data/'
cmd = 'rsync -rtv --log-file=%s %s %s' % (logfile, input_dir, 
    os.path.join(nas2_home_output_dir, 'neural/'))
print "rsync : %s" % str(datetime.datetime.now())
print cmd
sys.stdout.flush() # to maintain the order of print and os.system in the logfile
os.system(cmd)

# Print stop time
print "AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now())
