# This automatic script backs up paclab-krill to cuttlefish.
#
# It runs nightly on cephalopod. It should run after the heroku automatic 
# backup (pg:backup) has run, which currently starts at 11 PM ET and requires
# ~2-10 minutes to complete.
#
# Requirements:
#   /home/chris/mnt/cuttlefish should be mounted
#   /home/chris/mnt/cuttlefish/chris/backups should be a directory
#   /home/chris/mnt/cuttlefish/chris/backups/krill should be a directory
#   `heroku pg:backups public-url --app paclab-krill` should work
#   `curl` should be installed
#
# Outputs:
#   /home/chris/mnt/cuttlefish/chris/backups/krill/DATESTRING.dump
#
# Run like this:
# /bin/bash -i -l -c 'cd /home/chris/dev/autoscripts/cephalopod_backup_heroku; python3 backup_heroku.py >> logfile 2>&1'
# Use python3 because python may not exist outside of a conda environment
# These flags should ensure that heroku is are available on the PATH
# An alternative is to add PATH=/path/to/heroku in the single quoted command
# in the crontab.

import sys
import datetime
import os

# Announce the start and start time
print("AUTORUN_START backup_heroku")
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
sys.stdout.flush()

# Where to copy files to
mount_dir = '/home/chris/mnt/cuttlefish'
backups_dir = os.path.join(mount_dir, 'chris', 'backups')

# Check that it's mounted
if not os.path.ismount(mount_dir):
    raise IOError("Not a mount: %s" % mount_dir)

# Postgres backup of paclab-krill
# heroku is set to perform a pg:backup every day at 11PM
# Confirm this with: heroku pg:backups:schedules --app paclab-krill
# this script runs a few hours later so it should pull the latest version
backup_path = os.path.join(backups_dir, 'krill')
backup_file = datetime.date.today().strftime('%Y-%m-%d')
backup_full_file = os.path.join(backup_path, backup_file + '.dump')
cmd = 'curl -o %s `heroku pg:backups public-url --app paclab-krill`' % backup_full_file
print("\n# Dumping paclab-krill to pgdump")
print(cmd)
os.system(cmd)


# Announce the stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
