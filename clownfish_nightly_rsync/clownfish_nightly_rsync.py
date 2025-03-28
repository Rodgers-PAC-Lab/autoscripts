# rsync the behavior data from clownfish to cuttlefish
#
# Run like this: (note use of python3)
# /bin/bash -l -c 'cd /home/mouse/dev/autoscripts/clownfish_nightly_rsync; python3 clownfish_nightly_rsync.py >> logfile 2>&1'
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
import subprocess

# rsync will be called with this logfile
logfile = 'nightly_rsync.log'


## Check that cuttlefish is actually mounted before running
check_cuttlefish_mount_dir = '/home/mouse/mnt/cuttlefish2'
if not os.path.ismount(check_cuttlefish_mount_dir):
    raise IOError("This must be mounted: %s" % check_cuttlefish_mount_dir)

# Check this exists
cuttlefish_behavior_home = os.path.join(check_cuttlefish_mount_dir, 'behavior')
if not os.path.exists(cuttlefish_behavior_home):
    raise IOError("This must exist: %s" % cuttlefish_behavior_home)


## Run the rsync for octopilot
# rsync -va 
#   --backup-dir=/home/mouse/mnt/cuttlefish/from_clownfish/octopilot/terminal_backup_`date +%F_%H-%M-%S` 
#   /home/mouse/autopilot 
#   /home/mouse/mnt/cuttlefish/from_clownfish/autopilot/terminal

# This is where the input comes from
input_dir = '/home/mouse/octopilot'

# This is where output goes
output_dir = os.path.join(
    cuttlefish_behavior_home, 'from_clownfish')

# Generate the full rsync cmd
# Use --no-p because there is something weird about the permissions
# and if we don't ignore them, it lists every directory every time
# It sill picks up certain hdf5 files as having changed, not sure why
cmd = 'rsync -va --no-p --log-file=%s %s %s' % (
    logfile, input_dir, output_dir)
print("rsync : %s" % str(datetime.datetime.now()))
print(cmd)
sys.stdout.flush() # to maintain the order of print and os.system in the logfile

# Run the rsync
os.system(cmd)


## This is the way we used to back up autopilot, using backup_dir to catch changes
#~ ## Run the rsync for the terminal_backup
#~ # rsync -va 
#~ #   --backup-dir=/home/mouse/mnt/cuttlefish/from_clownfish/autopilot/terminal_backup_`date +%F_%H-%M-%S` 
#~ #   /home/mouse/autopilot 
#~ #   /home/mouse/mnt/cuttlefish/from_clownfish/autopilot/terminal

#~ # Generate the --backup-dir argument
#~ # The backticks will be expanded by os.system
#~ backup_dir_argument = os.path.join(
    #~ check_cuttlefish_mount_dir, 'from_clownfish', 'autopilot',
    #~ 'terminal_backup_`date +%F_%H-%M-%S`')

#~ # This is where the input comes from
#~ input_dir = '/home/mouse/autopilot'

#~ # This is where output goes
#~ output_dir = os.path.join(
    #~ check_cuttlefish_mount_dir, 'from_clownfish', 'autopilot', 'terminal')

#~ # Generate the full rsync cmd
#~ # Use --no-p because there is something weird about the permissions
#~ # and if we don't ignore them, it lists every directory every time
#~ # It sill picks up certain hdf5 files as having changed, not sure why
#~ cmd = 'rsync -va --no-p --log-file=%s --backup-dir=%s %s %s' % (
    #~ logfile, backup_dir_argument, input_dir, output_dir)
#~ print("rsync : %s" % str(datetime.datetime.now()))
#~ print(cmd)
#~ sys.stdout.flush() # to maintain the order of print and os.system in the logfile

#~ # Run the rsync
#~ os.system(cmd)


## Print stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_STOP__")
