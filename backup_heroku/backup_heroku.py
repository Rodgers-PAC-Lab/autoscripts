# This automatic script backs up mouse-cloud and rmb-colony to NAS.
#
# It runs nightly on gamma. It should run after the heroku automatic 
# backup (pg:backup) has run, which currently starts at 2 AM and requires
# almost an hour to complete.
#
# Requirements:
#   /home/jack/mnt/nas2_home should be mounted
#   /home/jack/mnt/nas2_home/backups should be adirectory
#   /home/jack/mnt/nas2_home/backups/krill should be a directory
#   `heroku pg:backups public-url --app paclab-krill` should work
#   `curl` should be installed
#
# Outputs:
#   /home/jack/mnt/nas2_home/backups/krill/DATESTRING.dump
#
# Run like this:
# /bin/bash -l -c 'cd dev/autoscripts/backup_heroku; python backup_heroku.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct
#
# For whatever reason I had to add PATH=/path/to/heroku in the single quoted
# command in the crontab. Probably because it doesn't run in interactive mode
# and thus doesn't source bashrc.

import sys
import datetime
import os

# Announce the start and start time
print "AUTORUN_START backup_heroku"
print "AUTORUN_START_TIME : %s" % str(datetime.datetime.now())
sys.stdout.flush()

# Where to copy files to
mount_dir = '/home/jack/data' #'/home/jack/mnt/nas2_home'
backups_dir = os.path.join(mount_dir, 'backups')

#~ # Check that it's mounted
#~ if not os.path.ismount(mount_dir):
    #~ raise IOError("Not a mount: %s" % mount_dir)

# Postgres backup of paclab-krill
# heroku is set to perform a pg:backup every day at 11PM
# Confirm this with: heroku pg:backups:schedules --app paclab-krill
# this script runs a few hours later so it should pull the latest version
backup_path = os.path.join(backups_dir, 'krill')
backup_file = datetime.date.today().strftime('%Y-%m-%d')
backup_full_file = os.path.join(backup_path, backup_file + '.dump')
cmd = 'curl -o %s `heroku pg:backups public-url --app paclab-krill`' % backup_full_file
print "\n# Dumping paclab-krill to pgdump"
print cmd
os.system(cmd)


# Announce the stop time
print "AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now())
