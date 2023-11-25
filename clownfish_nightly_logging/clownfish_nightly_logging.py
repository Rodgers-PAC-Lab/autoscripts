## Scrape recent additions in autopilot logfiles and compile them
# Run this first
# bash ~/dev/autoscripts/clownfish_nightly_rsync/connect_to_all_pis.sh
#
# Whenever this script runs, it checks a bunch of logfiles for any new lines,
# filters those lines for things that sound like errors, and stores those
# error lines in a report.
#
# To do this, every time it runs, it keeps a copy of the version of that
# logfile at that time in ~/archived_log_files/lastversion. On subsequent runs,
# each logfile is compared against its archived version, to extract just
# the new lines. Whenever a new archived version is created, a dated backup
# is made.
#
# These summaries of error lines are written in markdown and can be read as:
#   pandoc -fmarkdown+hard_line_breaks filename.md | lynx -stdin
# hard_line_breaks makes it respect original line breaks
#
# Similarly, every time a line is reported as an error, this is stored in 
# ~/archived_log_files/reported. Dated backups are used here too.
#
# The dated backup mean that, in theory, we can roll back to the state at
# any previous time simply by making the current version in the archive
# match the dated backups at that time.
#
# Here are the files to check
# on the children: ~/mnt/rpi*/autopilot/logs/*.log
# on the terminal: ~/autopilot/logs/*.log
#
# Here is what to search for, always case-insensitive
# error (excluding "play_error_sound")
# exception
#
# grep -i error ~/autopilot/logs/*.log ~/mnt/rpi*/autopilot/logs/*.log | grep -v play_error_sound
# grep -i exception ~/autopilot/logs/*.log ~/mnt/rpi*/autopilot/logs/*.log

import glob
import os
import shutil
import subprocess
import datetime


## Set paths and create summary file
# NOTE: unlike every other computer, clownfish mounts cuttlefish at mnt/cuttlefish2
# the behavior account is mounted at mnt/cuttlefish, but this is depracated

# Everything is kept under archive_root
archive_root = os.path.expanduser(
    '~/mnt/cuttlefish2/behavior/archived_behavioral_log_parsing')
lastversion_root = os.path.join(archive_root, 'lastversion')
report_root = os.path.join(archive_root, 'reported')
summary_root = os.path.join(archive_root, 'summary')

# Create all these directories if they don't already exist
for dirname in [archive_root, lastversion_root, report_root, summary_root]:
    if not os.path.exists(dirname):
        os.mkdir(dirname)

# This is the summary file we'll write now
dt_string = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
summary_name = os.path.join(summary_root, '{}.md'.format(dt_string))

# Write the datetime to the top of the summary file
with open(summary_name, 'w') as summary_fi:
    summary_fi.write(dt_string + '\n\n')


## This is how we filter lines to report
def keep(line):
    cmp = line.lower()
    if 'error' in cmp or 'exception' in cmp:
        if 'play_error_sound' not in cmp:
            return True
    return False


## Get rpi locations
# List of all known rpis used for behavior: rpi01-rpi21 excluding rpi15
rpinames = ['rpi{:02d}'.format(n) for n in range(1, 22) if n != 15]


## Mount every pi
for rpiname in rpinames:
    # Extract rpi number from name
    rpinumber = int(rpiname.replace('rpi', ''))
    
    # This is the sshfs link
    # Always 200 greater than its number
    sshfs_link = 'pi@192.168.11.{}:'.format(200 + rpinumber)
    
    # This is where it will be mounted
    mountpoint = os.path.expanduser('~/mnt/{}'.format(rpiname))
    
    # The mountpoint should exist already
    assert os.path.exists(mountpoint)

    # If it's already mounted, continue
    if os.path.ismount(mountpoint):
        #print("{} is already mounted at {}".format(rpiname, mountpoint))
        continue
    
    # Otherwise try to mount it
    print("mounting {} at {}".format(rpiname, mountpoint))
    proc = subprocess.run(
        ['sshfs', sshfs_link, mountpoint], capture_output=True)
    
    # Report any error
    if proc.returncode != 0:
        print("error mounting {} at {}".format(rpiname, mountpoint))
        print('stdout:')
        print(proc.stdout.decode('utf-8'))
        print('stderr:')
        print(proc.stderr.decode('utf-8'))


## Generate list of all logfile directories to scan, along with a pretty name
logfile_dir_pretty_name_l = ['terminal']
logfile_dir_l = [os.path.expanduser('~/autopilot/logs')]
for rpiname in rpinames:
    logfile_dir_pretty_name_l.append(rpiname)
    logfile_dir_l.append(
        os.path.expanduser('~/mnt/{}/autopilot/logs'.format(rpiname)))


## Iterate over logfile_dirs
zobj = zip(logfile_dir_pretty_name_l, logfile_dir_l)
for logfile_dir_pretty_name, logfile_dir in zobj:
    
    ## Announce current logfile_dir in summary and to stdout
    print(logfile_dir_pretty_name)
    with open(summary_name, 'a') as summary_fi:
        summary_fi.write('# {}\n'.format(logfile_dir_pretty_name))


    ## Set up locations to keep stuff for this logfile_dir
    # This is where we keep the last read version of every file
    archive_dir = os.path.join(lastversion_root, logfile_dir_pretty_name)
    if not os.path.exists(archive_dir):
        os.mkdir(archive_dir)
    
    # This is where we keep all error lines reported from every file
    report_dir = os.path.join(report_root, logfile_dir_pretty_name)
    if not os.path.exists(report_dir):
        os.mkdir(report_dir)

    
    ## Find all logfiles in logfile_dir
    # This only includes current versions, not rotated versions
    logfiles = glob.glob(os.path.join(logfile_dir, '*.log'))


    ## Iterate over all found logfiles
    for logfile in logfiles:
        
        ## Set up filenames
        # Get short name of the logfile
        shortname = os.path.split(logfile)[1]
        
        # Get archived name and report name
        archived_name = os.path.join(archive_dir, shortname)
        report_name = os.path.join(report_dir, shortname)
        
        
        ## Load logfiles (previous and current)
        # Load current
        with open(logfile) as fi:
            current = fi.readlines()
        
        # Error check that the last line ends with a newline
        # Probably violated only after a crash or if it's in the middle
        # of updating
        if len(current) > 0:
            if current[-1][-1] != '\n':
                1/0
        
        # Load previous, or [] if it doesn't exist
        if os.path.exists(archived_name):
            # Load previous
            with open(archived_name) as fi:
                previous = fi.readlines()
        else:
            previous = []
        
        
        ## Identify if the log has been rotated
        # Want to make sure that "current" starts with the same lines as
        # "previous"
        if len(previous) > 0:
            # Only do anything if we actually have stuff in the archived version
            # If we don't have stuff in the archive, there's no concern
            # that it's missing from the current
            
            # Prepend up to 7 logs
            for n_logs in range(1, 32):
                # This tests all lines in previous and current (up to whichever
                # is shorter) for equality
                logs_match = True
                for pline, cline in zip(previous, current):
                    if pline != cline:
                        logs_match = False
                        break
                
                if logs_match:
                    # All lines match (except for new ones in the longer one)
                    # So break
                    break
                else:
                    # Some lines don't match
                    # Prepend the recently rotated log and try again
                    fn_to_prepend = logfile + '.{}'.format(n_logs)
                    
                    # Continue if this logfile doesen't exist
                    if not os.path.exists(fn_to_prepend):
                        continue
                    
                    print("prepending logfile {}".format(fn_to_prepend))
                    with open(fn_to_prepend) as fi:
                        to_prepend = fi.readlines()
                    
                    current = to_prepend + current
            
            # One last check
            # Error check that we have all the previous lines
            for pline, cline in zip(previous, current):
                if pline != cline:
                    # This can happen if too much time has passed
                    raise ValueError("cannot overlap previous and current logs")
        
        # I think this must be true now
        assert len(current) >= len(previous)
        
        # We only need to update the archive if there are new lines
        if len(previous) == len(current):
            update_archive = False
        else:
            update_archive = True

        
        ## Identify which lines are new since the last report
        current = current[len(previous):]
        
        
        ## Filter the lines for error or exception, but not play_error_sound
        keep_lines = [line for line in current if keep(line)]
        
        
        ## Report the keep_lines
        if len(keep_lines) > 0:
            # Print to summary
            with open(summary_name, 'a') as summary_fi:
                summary_fi.write('## {} / {}\n'.format(
                    logfile_dir_pretty_name, shortname))
                for line in keep_lines:
                    summary_fi.write(line)      
                summary_fi.write('\n')
            
            # Print to report archive
            # Backup the old copy
            if os.path.exists(report_name):
                shutil.copyfile(
                    report_name, 
                    report_name + '.backup.{}'.format(dt_string))                    
            with open(report_name, 'a') as report_fi:
                for line in keep_lines:
                    report_fi.write(line)

        
        ## Update the archive if necessary (ie, new lines)
        if update_archive:
            # Backup the old copy
            if os.path.exists(archived_name):
                shutil.copyfile(
                    archived_name, 
                    archived_name + '.backup.{}'.format(dt_string))
            
            # Copy current to previous (the new archive)
            shutil.copyfile(logfile, archived_name)
