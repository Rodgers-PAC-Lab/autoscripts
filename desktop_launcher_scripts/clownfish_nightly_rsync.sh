# This is the same command in crontab -e that is run inside
# a "bash -i -l -c"
# This version is meant to be used from a desktop launcher

echo Starting octopilot backup...
cd /home/mouse/dev/autoscripts/clownfish_nightly_rsync
python3 clownfish_nightly_rsync.py >> logfile 2>&1
echo Octopilot backup complete. Press any key to close this window
read

