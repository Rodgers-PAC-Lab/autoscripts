# rsync data from shrimp to cuttlefish
# * ~/open-ephys
# * ~/octopilot
# * ~/Videos
#
# Run like this:
# /bin/bash -l -c 'cd /home/mouse/dev/autoscripts/shrimp_nightly_rsync; python3 shrimp_nightly_rsync.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct


## Announce the start and start time
print("---------------")
print("AUTORUN_START__")
import datetime
import os
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_START_FILE {}".format(os.path.abspath(__file__)))

# Rest of imports
import sys


## Logfile
# rsync will be called with this logfile
logfile = 'nightly_rsync.log'


## Check that output diretories are actually mounted before running
check_cuttlefish_mount_dir = '/home/mouse/mnt/shrimpX'
if not os.path.ismount(check_cuttlefish_mount_dir):
    raise IOError("This must be mounted: %s" % check_cuttlefish_mount_dir)

check_cuttlefish_mount_dir = '/home/mouse/mnt/cuttlefish'
if not os.path.ismount(check_cuttlefish_mount_dir):
    raise IOError("This must be mounted: %s" % check_cuttlefish_mount_dir)


## The reusable copy function
def run_rsync(input_dir, output_dir):
    # Form the command
    cmd = 'rsync -va --no-p --log-file=%s %s %s' % (
        logfile, input_dir, output_dir)
    
    # Log the command
    print("rsync : %s" % str(datetime.datetime.now()))
    print(cmd)
    
    # This maintains the order of print and os.system in the logfile
    sys.stdout.flush() 
    
    # Run the command
    os.system(cmd)    


## Copy ~/open-ephys to ~/mnt/cuttlefish/shrimp
input_dir = '/home/mouse/open-ephys'
output_dir = '/home/mouse/mnt/cuttlefish/shrimp'
run_rsync(input_dir, output_dir)


## Copy ~/Videos to shrimpX
input_dir = '/home/mouse/Videos'
output_dir = '/home/mouse/mnt/shrimpX'
run_rsync(input_dir, output_dir)


## Copy ~/octopilot to ~/mnt/cuttlefish/shrimp
input_dir = '/home/mouse/octopilot'
output_dir = '/home/mouse/mnt/cuttlefish/shrimp'
run_rsync(input_dir, output_dir)


## Print stop time
print()
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_STOP__")
