# Generate an email with results of behavior
# Accepts an "experimenter" parameter which can be chris, jung, or all

# Announce the start and start time
print("AUTORUN_START nightly_email")
import datetime
print("AUTORUN_START_TIME : %s" % str(datetime.datetime.now()))
import sys
sys.stdout.flush()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import MCwatch
import pandas
import numpy as np
import matplotlib.pyplot as plt
import weasyprint
import subprocess
import smtplib
import email
from email.mime.application import MIMEApplication
import email.mime.multipart
import email.mime.text
import os.path
import runner.models

import socks
#socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "bcp3.cumc.columbia.edu", 8080)
#socks.wrapmodule(smtplib)
#~ server = smtplib.SMTP('smtp.gmail.com:587')
#~ print "server acquired"
#~ 1/0

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("experimenter", nargs='?', default='')

args = parser.parse_args()

DRY_RUN = False

def date_from_YMDHMS(s):
    """Given a string like 201501011159, return datetime"""
    return datetime.datetime.strptime(s, '%Y%m%d%H%M%S')
def drop_runmice_dir(s):
    token = '/home/mouse/mnt/nas2_home/behavior/sandbox_root'
    if not s.startswith(token):
        raise ValueError("string does not begin with runmice path")
    return s[len(token):]

# Choose the toaddrs
if args.experimenter == 'chris':
    experimenters = ['chris']
elif args.experimenter == 'jung':
    experimenters = ['jung']
elif args.experimenter == 'all':
    experimenters = ['chris', 'jung']
elif args.experimenter == '':
    print("No experimenter provided, exiting.")
    print("Specify chris, jung, or all, if you want to send an email")
    experimenters = []
else:
    print("Experimenter must be chris, jung, or all, not %r" % args.experimenter)
    experimenters = []


# Iterate over experimenters and send one email to each   
for experimenter in experimenters:
    # Get the toaddrs and experimenter_id
    if experimenter == 'chris':
        toaddrs = [
            "xrodgers_cat_gmail_dog_com",
            "eg3026_cat_columbia_dog_edu",
        ]
        experimenter_id = 0
    elif experimenter == 'jung':
        toaddrs = [
            "jp3641_cat_columbia_dog_edu",
            "jbd2144_cat_columbia_dog_edu",
            "ers2204_cat_columbia_dog_edu",
        ]
        experimenter_id = 1        
    else:
        raise ValueError("unknown experimenter: %s" % experimenter)
    
    for n in range(len(toaddrs)):
        toaddrs[n] = toaddrs[n].replace('_cat_', '@').replace('_dog_', '.')

    # Put the text results here
    text_results = []
    text_results.append('Behavior report: ' + str(datetime.datetime.now()))

    # figs to concatenate
    figs = []

    # The day to analyze
    target_date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    text_results.append("Target date: %s" % str(target_date))

    # Get the db
    db = MCwatch.behavior.db.get_behavior_df()
    pdf = MCwatch.behavior.db.get_perf_metrics()
    active_mice = list(runner.models.Mouse.objects.filter(
        in_training=True, experimenter=experimenter_id
        ).values_list('name', flat=True))

    # Print out data from today's session
    formatters = {
        'dt_start': lambda dt: pandas.to_datetime(dt).strftime('%H:%M:%S'),
        'dt_end': lambda dt: pandas.to_datetime(dt).strftime('%H:%M:%S'),
        'duration': lambda dt: str(dt / np.timedelta64(1, 's')),
        'filename': drop_runmice_dir,
        }

    # Get the sessions from the target date
    todays_db = db[
        (db.dt_end.apply(lambda dt: dt.date()) == target_date) &
        (db['mouse'].isin(active_mice))
    ]
    todays_db = todays_db.set_index('session')
    todays_db = todays_db[['mouse', 'rig', 'dt_start', 'duration', 'filename', 
        'protocol', 'stimulus_set']].sort_values('mouse')

    # Print parsed sessions
    text_results.append("PARSED SESSIONS FROM TODAY: (%d)" % len(todays_db))
    text_results.append(
        todays_db.drop('filename', 1).to_string(formatters=formatters))

    # Check for any mice that weren't run
    unrun_mice = [mouse for mouse in active_mice
        if mouse not in todays_db.mouse.values]
    text_results.append("\n\nMICE THAT WERE NOT RUN: (%d)" % len(unrun_mice))
    text_results.append(' '.join(unrun_mice))

    # Print perf metrics from today
    todays_pdf = pdf.drop_duplicates(
        subset=['session']).set_index('session').reindex(todays_db.index)
    todays_pdf = todays_pdf.join(todays_db[['rig']])
    #~ todays_pdf = todays_pdf.sort_values(by='perf_unforced', ascending=False)
    text_results.append("\n\nPERFORMANCE METRICS:")
    text_results.append(todays_pdf[
        ['rig', 'n_trials', 'spoil_frac', 'perf_all', 'perf_unforced']
        ].to_string(float_format=lambda f: "%0.2f" % f))

    # Text results to pdf
    html_text = '<pre><span class="inner-pre" style="font-size: 11px">' + \
        "\n".join(text_results).replace("\n", "\r\n") + "</pre>"
    html = weasyprint.HTML(string=html_text)
    html.write_pdf('text.pdf')

    # Performance plots by training stage
    pbts_fig_l = MCwatch.behavior.db_plot.plot_by_training_stage(
        mouse_names=active_mice)
    for nfig, fig in enumerate(pbts_fig_l):
        figname = 'perf_by_training_stage%d.pdf' % nfig
        fig.savefig(figname)
        figs.append(figname)

    # Plot by box
    if experimenter == 'chris':
        f = MCwatch.behavior.db_plot.display_perf_by_rig()
        figname = 'perf_by_box.pdf'
        f.savefig(figname)
        figs.append(figname)
        plt.close(f)

    # Session plots
    for nsession, session in enumerate(todays_db.index):
        if todays_db.loc[session, 'protocol'] != 'TwoChoice':
            continue
        try:
            f = MCwatch.behavior.db_plot.display_session_plot(session)
        except:
            # This happens with empty trial matrix
            print("cannot generate session plot")
            continue
        figname = 'session%d.pdf' % nsession
        figs.append(figname)
        f.savefig(figname)
        plt.close(f)

    # Concatenate pdfs
    pipe = subprocess.Popen(['pdftk', 'text.pdf'] + figs +
        ['cat', 'output', 'report.pdf'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = pipe.communicate()

    # Remove the pdfs from disk
    for fig in figs:
        os.remove(fig)
    os.remove('text.pdf')

    # Email params
    fromaddr = "labautoemail@gmail.com"
    username = "labautoemail@gmail.com"
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

# Print stop time
print("AUTORUN_STOP_TIME : %s" % str(datetime.datetime.now()))
