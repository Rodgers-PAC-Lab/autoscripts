# Run this every minute
# Checks disk usage and kills watchtower if it exceeds some value
#
# Run like this:
# /bin/bash -l -c 'cd /home/mouse/dev/autoscripts/jellyfish_df_monitor; python jellyfish_df_monitor.py >> logfile 2>&1'
# This ensures that the python installation and paths are correct

# Announce the start and start time
print("---------------")
print("AUTORUN_START__")
import datetime
import os
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_START_FILE {}".format(os.path.abspath(__file__)))

# More imports
import subprocess

threshold = 95

# Check disk space
df_bytes = subprocess.run(['df', '-h'], capture_output=True)

# Parse result
df_s = df_bytes.stdout.decode('utf-8').strip()

# Iterate over lines
pct_used_f = None
for line in df_s.split('\n')[1:]:
    # Get result from this line
    filesystem, total_sz, used_sz, remaining_sz, pct_used, mountpoint = (
        line.split())
    
    # Get pct used for root
    if mountpoint == '/':
        pct_used_f = float(pct_used.replace('%', ''))
        break

# Error if couldn't parse pct_used 
if pct_used_f is None:
    raise ValueError("cannot get df for root")

# Kill if over threshold
if pct_used_f >= threshold:
    print('killing')
    kill_proc = subprocess.run(['killall', 'xed'], capture_output=True)
    if kill_proc.returncode == 0:
        print('successful kill')
    else:
        print('kill failed: {}'.format(
            kill_proc.stderr.decode('utf-8').strip()))
else:
    print('no need to kill')

# Print stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
print("AUTORUN_STOP__")