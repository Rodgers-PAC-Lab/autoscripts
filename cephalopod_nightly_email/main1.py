## Run a behavioral report
# For whatever reason, cannot import weasyprint in pylab mode
#
# Make plots of each cohort of mice, and capture errors/warnings
# Check for missing sessions
# Grab the pandoc error messages from clownfish
# Run a df on jellyfish
# Based on autoscripts/marving_post_behavior/nightly_email.py
#
# Order
# * [clownfish] 21:00 /home/mouse/dev/scripts/chris/20230216_behavior_logfiles; python3 main1.py
# * [clownfish] 21:10 /home/mouse/dev/autoscripts/clownfish_nightly_rsync/clownfish_nightly_rsync.py
# * [jellyfish] 22:00 /home/mouse/dev/autoscripts/jellyfish_nightly_rsync/jellyfish_nightly_rsync.py
# * [cuttlefish] This script makes a bunch of plots in 'plots'
# * [cuttlefish] 00:30 /home/chris/dev/autoscripts/cephalopod_weekly_aws/rclone_s3.sh
#    Generates text output in text.pdf
#    Summarizes everything in report.pdf

# Announce the start and start time
print("AUTORUN_START nightly_email")
import datetime
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
import sys
sys.stdout.flush()

import os
import traceback
import glob
import numpy as np
import pandas
import spur
import paclab
import shared
import matplotlib.pyplot as plt
import weasyprint
import subprocess
import smtplib
import email
from email.mime.application import MIMEApplication
import email.mime.multipart
import email.mime.text
import socks


## Set up for email
DRY_RUN = False

toaddrs = [
    "xrodgers_cat_gmail_dog_com",
    #"eliana.pollay_cat_emory_dog_edu",
    #"valentina.esho_cat_emory_dog_edu",
    "cabowe_cat_emory_dog_edu",
    #"rowan.gargiullo_cat_emory_dog_edu",
    'abigail.mcelroy_cat_emory_dog_edu',
    'kai.park_cat_emory_dog_edu',
    'hansu.chung_cat_emory_dog_edu',
    #'karinne.cobb_cat_emory_dog_edu',
    ]
for n in range(len(toaddrs)):
    toaddrs[n] = toaddrs[n].replace('_cat_', '@').replace('_dog_', '.')


## Put the text results here
text_results = []
text_results.append('Behavior report: ' + str(datetime.datetime.now()))

# The day to analyze (today)
# For debugging, sometimes we set this to yesterday to grab yesterday's results
target_date = datetime.datetime.now().date()
text_results.append("Target date: %s" % str(target_date))


## All plots will go here
plot_dir = 'plots'
if not os.path.exists(plot_dir):
    os.mkdir(plot_dir)

# Remove anything in there
for filename in os.listdir(plot_dir):
    os.remove(os.path.join(plot_dir, filename))


## Define cohorts of mice
# Each cohort will be separately plotted
cohorts = {
    'cedric1': [
    'Tiger_142',
    'Tiger_143',
    'TeacupDog_140',
    'TeacupDog_139',
    'TeacupDog_141',
    ],
    'cedric2': [
    'Koala_145',
    'Koala_144',
    'SmoothieDog_138',
    'SmoothieDog_136',
    'SmoothieDog_137',
    'SmoothieDog_135',
    ],
    'abigail': [
        'Hot_Dog_148',
        'Hot_Dog_149',
        'Seal_150',
        'Seal_151',
        'Tractor_146',
        'Tractor_147',
        'Goat_152',
        'Goat_153',
    ],
    'joe': [
        'Llama_156',
        'Llama_157',
        'Parrot_164',
        'Parrot_165',
        'Chameleon_162',
        'Chameleon_163',
        'Lemon_154',
        'Lemon_155',
    ],    
    'kai': [
        'Lion_158',
        'Lion_159',
        'Sun_160',
        'Sun_161',
    ],
}


## Analyze behavior
# This makes all plots and returns a logfile
try:
    output_log_text = shared.analyze_behavior(plot_dir, cohorts)
except Exception as e:
    # Uncomment this raise for debugging
    # And also do a similar uncomment in make_all_plots
    #raise
    
    output_log_text = (
        "error running shared.analyze_behavior" + 
        ''.join(traceback.format_exception(None, e, e.__traceback__))
        + '\n'
        )
    print(output_log_text)
    
plt.close('all')

text_results.append(output_log_text)

## Get df
# This is for the video computer
shell = spur.SshShell(hostname='dolphin', username='mouse', port=60000)
cannot_connect = False
try:
    ssh_result = shell.run(['df', '-h', '/'])
except spur.ssh.ConnectionError:
    cannot_connect = True
shell.close()

if cannot_connect:
    text_results.append('cannot connect to jellyfish!')
else:
    df_s = ssh_result.output.decode('utf-8')
    filesystem, total_sz, used_sz, remaining_sz, pct_used, mountpoint = (
        df_s.split('\n')[1].split())
    text_results.append(df_s)


## Find a markdown summary of today's behavior
# Get a list of all summary files
ablp_dir = os.path.expanduser(
    '~/mnt/cuttlefish/behavior/archived_behavioral_log_parsing/summary')
log_parsing_filenames = os.listdir(ablp_dir)

# Find the one(s) that start with today's date (the target date)
todays_log_parsing_results_l = [
    s for s in log_parsing_filenames if s.startswith(str(target_date))]

# Write out the results from each log
if len(todays_log_parsing_results_l) == 0:
    # No logs available
    text_results.append('warning: no log parsing results for today\n')

else:
    # One or more logs available, iterate over them
    for lpr in todays_log_parsing_results_l:
        # Read it
        full_filename = os.path.join(ablp_dir, lpr)
        text_results.append('logfile {} follows\n'.format(lpr))
        text_results.append('---\n')

        # TODO: use pandoc to render this markdown more nicely
        # For now, just print the markdown
        with open(full_filename) as fi:
            todays_markdown = fi.readlines()
        todays_markdown_s = ''.join(todays_markdown)

        # Append to text results
        text_results.append(todays_markdown_s)


## Text results to pdf
# TODO: Instead of forcing this through html, which looks ugly, use pandoc
# to convert markdown directly to pdf
# Text results to pdf
html_text = (
    '<pre><span class="inner-pre" style="font-size: 7px">' + 
    "\n".join(text_results).replace("\n", "\r\n") + "</pre>"
    )
html = weasyprint.HTML(string=html_text)
html.write_pdf('text.pdf')

# Concatenate pdfs
fig_pdfs = sorted(glob.glob(os.path.join(plot_dir, '*.pdf')))
pipe = subprocess.Popen(['pdftk', 'text.pdf'] + fig_pdfs +
    ['cat', 'output', 'report.pdf'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = pipe.communicate()

# Remove the pdfs from disk
for fig in fig_pdfs:
    os.remove(fig)
os.remove('text.pdf')


## Email
# Email params
fromaddr = "rodgers.paclab.autoemail@gmail.com"
username = "rodgers.paclab.autoemail@gmail.com"

# This is NOT the gmail password, it's an "app password" generated under
# 2-step verification settings
with open('credentials') as fi:
    password = fi.readlines()[0].strip()

# Construct msg
msg = email.mime.multipart.MIMEMultipart(
    From=fromaddr,
    To=email.utils.COMMASPACE.join(toaddrs),
    Date=email.utils.formatdate(localtime=True),
    Subject="Behavior auto report %s" % str(target_date),
    )
msg.attach(email.mime.text.MIMEText(html_text, "html"))

# Attach file
filename = 'report.pdf'
with open(filename, "rb") as fi:
    msg.attach(MIMEApplication(
        fi.read(),
        Content_Disposition='attachment; filename="%s"' % os.path.basename(filename),
        Name=os.path.basename(filename),
        ))

# Send message
if not DRY_RUN:
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    server.close()

    # Delete the pdf
    os.remove(filename)


## Print stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
