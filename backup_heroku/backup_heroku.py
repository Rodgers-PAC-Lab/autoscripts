# This automatic script backs up mouse-cloud and rmb-colony to NAS.
#
# It runs nightly on gamma. It should run after the heroku automatic 
# backup (pg:backup) has run, which currently starts at 2 AM and requires
# almost an hour to complete.
#
# Requirements:
#   /home/jack/mnt/nas2_home should be mounted
#   /home/jack/mnt/nas2_home/backups/django_mouse_cloud should be a directory
#   /home/jack/mnt/nas2_home/backups/django_rmb_colony should be a directory
#   `heroku pg:backups public-url --app mouse-cloud` should work
#   `heroku pg:backups public-url --app rmb-colony` should work
#   `curl` should be installed
#
# Outputs:
#   /home/jack/mnt/nas2_home/django_mouse_cloud/DATESTRING.dump
#   /home/jack/mnt/nas2_home/django_rmb_colony/DATESTRING.dump
#
# Run like this:
# /bin/bash -l -c 'cd dev/autoscripts/backup_heroku; python backup_heroku.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct
#

import sys
import datetime
import os

# Announce the start and start time
print "AUTORUN_START backup_heroku"
print "AUTORUN_START_TIME : %s" % str(datetime.datetime.now())
sys.stdout.flush()

# Where to copy files to
mount_dir = '/home/jack/mnt/nas2_home'
backups_dir = os.path.join(mount_dir, 'backups')

# Check that it's mounted
if not os.path.ismount(mount_dir):
    raise IOError("Not a mount: %s" % mount_dir)

# Postgres backup of mouse-cloud
backup_path = os.path.join(backups_dir, 'django_mouse_cloud')
backup_file = datetime.date.today().strftime('%Y-%m-%d')
backup_full_file = os.path.join(backup_path, backup_file + '.dump')
cmd = 'curl -o %s `heroku pg:backups public-url --app mouse-cloud`' % backup_full_file
print "\n# Dumping mouse-cloud to pgdump"
print cmd
os.system(cmd)

# Postgres backup of rmb-colony
# heroku is set to perform a pg:backup every day at 2AM
# this script runs a few hours later so it should pull the latest version
backup_path = os.path.join(backups_dir, 'django_rmb_colony')
backup_file = datetime.date.today().strftime('%Y-%m-%d')
backup_full_file = os.path.join(backup_path, backup_file + '.dump')
cmd = 'curl -o %s `heroku pg:backups public-url --app rmb-colony`' % backup_full_file
print "\n# Dumping rmb-colony to pgdump"
print cmd
os.system(cmd)


# Announce the stop time
print "AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now())
