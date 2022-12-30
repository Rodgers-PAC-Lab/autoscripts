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


## Mount the parent rpis so we can get their logfiles too
# Presently we are only doing this for rpi13
proc = subprocess.Popen(
    ['sshfs', 'pi@192.168.11.213:', '/home/mouse/mnt/rpi13'], 
    stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
proc.wait()

# Parse the result of the Popen
if proc.returncode == 0:
    # This means it mounted successfully
    pass
elif proc.returncode == 1:
    # An error occurred
    error_message = proc.stderr.read()
    if 'mountpoint is not empty' in error_message:
        # This is the expected error if it's already mounted, which is ok
        pass
    else:
        # An unexpected error occurred
        # Log the error
        # But continue, because we still want to do the other backups
        print("unexpected error occurred when mounting rpi13: {}".format(
            error_message))

# Check that cuttlefish is actually mounted before running
check_cuttlefish_mount_dir = '/home/mouse/mnt/cuttlefish'
if not os.path.ismount(check_cuttlefish_mount_dir):
    raise IOError("This must be mounted: %s" % check_cuttlefish_mount_dir)


## Run the rsync for rpi13
# rsync -va 
#   --backup-dir=/home/mouse/mnt/cuttlefish/from_clownfish/autopilot/logfiles/rpi13_backup_`date +%F_%H-%M-%S` 
#   /home/mouse/mnt/rpi13/autopilot/logs/ 
#   /home/mouse/mnt/cuttlefish/from_clownfish/autopilot/logfiles/rpi13

# Generate the --backup-dir argument
# The backticks will be expanded by os.system
backup_dir_argument = os.path.join(
    check_cuttlefish_mount_dir, 'from_clownfish', 'autopilot', 'logfiles', 
    'rpi13_backup_`date +%F_%H-%M-%S`')

# This is where the input comes from
# Note the trailing slash
input_dir = '/home/mouse/mnt/rpi13/autopilot/logs/'

# This is where output goes
output_dir = os.path.join(
    check_cuttlefish_mount_dir, 'from_clownfish', 'autopilot', 'logfiles', 
    'rpi13')

# Generate the full rsync cmd
cmd = 'rsync -va --log-file=%s --backup-dir=%s %s %s' % (
    logfile, backup_dir_argument, input_dir, output_dir)
print("rsync : %s" % str(datetime.datetime.now()))
print(cmd)
sys.stdout.flush() # to maintain the order of print and os.system in the logfile

# Run the rsync
os.system(cmd)


## Run the rsync for the terminal_backup
# rsync -va 
#   --backup-dir=/home/mouse/mnt/cuttlefish/from_clownfish/autopilot/terminal_backup_`date +%F_%H-%M-%S` 
#   /home/mouse/autopilot 
#   /home/mouse/mnt/cuttlefish/from_clownfish/autopilot/terminal

# Generate the --backup-dir argument
# The backticks will be expanded by os.system
backup_dir_argument = os.path.join(
    check_cuttlefish_mount_dir, 'from_clownfish', 'autopilot',
    'terminal_backup_`date +%F_%H-%M-%S`')

# This is where the input comes from
input_dir = '/home/mouse/autopilot'

# This is where output goes
output_dir = os.path.join(
    check_cuttlefish_mount_dir, 'from_clownfish', 'autopilot', 'terminal')

# Generate the full rsync cmd
# Don't use verbose here, because it prints every directory, I think maybe
# because the GUI is running and touching something?
cmd = 'rsync -a --log-file=%s --backup-dir=%s %s %s' % (
    logfile, backup_dir_argument, input_dir, output_dir)
print("rsync : %s" % str(datetime.datetime.now()))
print(cmd)
sys.stdout.flush() # to maintain the order of print and os.system in the logfile

# Run the rsync
os.system(cmd)


## Print stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_STOP__")
