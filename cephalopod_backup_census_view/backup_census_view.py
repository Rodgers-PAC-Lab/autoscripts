# This automatic script backs up a copy of the census view to cuttlefish.
#
# It runs nightly on cephalopod. 
#
# Requirements:
#   /home/chris/mnt/cuttlefish should be mounted
#   /home/chris/mnt/cuttlefish/chris/backups should be a directory
#   /home/chris/mnt/cuttlefish/chris/backups/krill-html should be a directory
#   './credentials' must exist and be valid in the current directory
#   The user specified by 'credentials' must exist and have staff privileges
#
# Outputs:
#   /home/chris/mnt/cuttlefish/chris/backups/krill-html/YEAR/MONTH/DAY/index.DATESTRING.html
#   /home/chris/mnt/cuttlefish/chris/backups/krill-html/YEAR/MONTH/DAY/index.html
#
# Run like this:
# /bin/bash -i -l -c 'cd /home/chris/dev/autoscripts/cephalopod_backup_census_view; python3 backup_census_view.py >> logfile 2>&1'
# Use python3 because python may not exist outside of a conda environment
# The bash flags are probably not necessary here because no special modules
# are required

# Minimal imports
import sys
import datetime
import os

# Announce the start and start time
print("AUTORUN_START backup_census_view")
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
sys.stdout.flush()

# Rest of imports
import requests
import json

# Where to copy files to
mount_dir = '/home/chris/mnt/cuttlefish'
backups_dir = os.path.join(mount_dir, 'chris', 'backups')

# Check that it's mounted
if not os.path.ismount(mount_dir):
    raise IOError("Not a mount: %s" % mount_dir)

# This is the root of the backup
backup_path = os.path.join(backups_dir, 'krill-html')

# Store the output in a dated directory nested within backup_path
now = datetime.datetime.now()
dt_string = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

# Nested directory for today
output_directory = backup_path
for number in now.year, now.month, now.day:
    output_directory = os.path.join(output_directory, str(number))
    if not os.path.exists(output_directory):
        print("creating directory", output_directory)
        os.mkdir(output_directory)

# Filename, one with date string, one without
output_filename1 = os.path.join(output_directory,
    'index.%s.html' % dt_string)
output_filename2 = os.path.join(output_directory,
    'index.html')

# load credentials
with open('credentials') as fi:
    credentials = json.load(fi)
username = credentials['username']
password = credentials['password']

# Connect to login url and get the cookies
URL = "https://paclab-krill.herokuapp.com/admin/login/"
client = requests.session()
client.get(URL)
csrftoken = client.cookies['csrftoken']
cookies = dict(client.cookies)

# Now post the login information and continue to /colony/
# token has to be in the header, and also in the cookies
headers = {
    'Referer': 'https://paclab-krill.herokuapp.com', # required
    'X-CSRFToken': csrftoken # required
}
login_data = {
    'username': username, 
    'password': password, 
    'next': '/colony/'}
response = requests.post(URL, 
    data=login_data, headers=headers, cookies=cookies)

if len(response.text) < 100000:
    print("WARNING: did not get very much text")

with open(output_filename1, 'w') as fi:
    fi.write(response.text)
with open(output_filename2, 'w') as fi:
    fi.write(response.text)
