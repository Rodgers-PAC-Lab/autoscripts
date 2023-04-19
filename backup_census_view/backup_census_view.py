# This automatic script backs up a copy of the census view to the NAS.
#
# It runs nightly on gamma.
#
# Requirements:
#   /home/jack/mnt/nas2_home should be mounted
#   /home/jack/mnt/nas2_home/backups/rmb-colony-html should be a directory
#   './credentials' must exist and be valid in the current directory
#   The user specified by 'credentials' must exist and have staff privileges
#
# Outputs:
#   /home/jack/mnt/nas2_home/rmb-colony-html/YEAR/MONTH/DAY/index.DATESTRING.html
#   /home/jack/mnt/nas2_home/rmb-colony-html/YEAR/MONTH/DAY/index.html
#
# Run like this:
# /bin/bash -l -c 'cd dev/autoscripts/backup_census_view; python backup_census_view.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct

import os
import datetime
import requests
import json

# Store the output in a dated directory on the nas
# Would be better to get the root backups directory from the command line
# somehow
now = datetime.datetime.now()
dt_string = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

# Root directory on NAS
#root_output_directory = '/home/jack/mnt/nas2_home/backups/rmb-colony-html'
root_output_directory = '/home/jack/data/krill-html'

# Nested directory for today
output_directory = root_output_directory
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
