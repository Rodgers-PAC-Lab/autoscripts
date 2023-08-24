import os
import traceback
import datetime
import numpy as np
import pandas
import paclab
import matplotlib.pyplot as plt
import my.plot
import matplotlib.dates as mdates


## Plots
PLOT_RCP_AND_FC = True
PLOT_TRIALS_AND_POKES_BY_SESSION = False
PLOT_POKES_BY_PORT_EVERY_SESSION = False
PLOT_TRIALS_BY_PORT_EVERY_SESSION = False
PLOT_SWEEP_TASK_BY_PARAM = False
IMSHOW_FIRST_POKED_PORT_BY_PRP = False

# Helpers
myFmt = mdates.DateFormatter('%m-%d')




def analyze_behavior(plot_dir, cohorts):
    ## Keep track of all errors and warnings
    output_log_text = ''


    ## Load munged metadata
    # Define munged sessions
    munged_sessions_df = pandas.read_excel(os.path.expanduser(
        '~/mnt/cuttlefish/shared/munged_sessions.xlsx'))
    munged_sessions = munged_sessions_df['Session Name'].values

    # TODO: define renamed sessions in a similar way
    rename_sessions_l = []


    ## Get data for parse
    # Get path to terminal data
    path_to_terminal_data = paclab.paths.get_path_to_terminal_data()

    # Form mouse_names
    mouse_names = []
    for cohort_name, cohort_mice in cohorts.items():
        mouse_names += list(cohort_mice)
    mouse_names = sorted(np.unique(mouse_names))


    ## Parse data
    # Get parsed_results
    # TODO: Also get PokeTrain
    # TODO: capture errors and warnings as a string
    parsed_results = paclab.parse.parse_sandboxes(
        path_to_terminal_data, 
        mouse_names=mouse_names,
        rename_sessions_l=rename_sessions_l,
        munged_sessions=munged_sessions,
        protocol_name=None,#'PAFT',
        quiet=True,
        )

    # Extract the parsed_results into their own variables
    perf_metrics = parsed_results['perf_metrics']
    session_df = parsed_results['session_df']
    trial_data = parsed_results['trial_data']
    poke_data = parsed_results['poke_data']

    # Append text output, if any
    output_log_text += parsed_results['txt_output']


    ## Identify duplicated session and problem dates
    txt_output = paclab.parse.identify_duplicated_sessions(
        session_df, quiet=False)
    output_log_text += txt_output


    ## Get the task of each mouse
    task_mouse_df = session_df.groupby(
        ['mouse', 'protocol_filename']).size().rename('n_sessions').reset_index()
    task_mouse_df['task'] = task_mouse_df['protocol_filename'].apply(
        lambda s: os.path.split(s)[1].replace('.json', ''))
    mouse2task = task_mouse_df.set_index('mouse')['task'].sort_index()
    task2mouse = task_mouse_df.set_index(['task', 'mouse'])[
        'n_sessions'].sort_index()


    ## Calculate performance metrics
    # Calculate n_pokes by date
    n_pokes_by_session = trial_data['n_pokes'].groupby(['session_name']).sum()
    perf_metrics = perf_metrics.join(n_pokes_by_session, on='session_name')

    # Calculate n_trials and n_pokes by date
    perf_by_mouse_and_date = perf_metrics.reset_index().set_index(
        ['mouse', 'date'])[['n_trials', 'n_pokes', 'rcp', 'fc']]

    # Calculate pokes by port
    poked_by_port = poke_data.groupby('session_name')[
        'poked_port'].value_counts().unstack().T

    # Calculate trials by port
    trials_by_port = trial_data.groupby('session_name')[
        'rewarded_port'].value_counts().unstack().T


    ## Plots
    # Do these plots, one for each cohort
    for cohort_name, cohort_mouse_names in cohorts.items():      
        plot_error_text = make_all_plots(
            plot_dir,
            cohort_name,
            perf_by_mouse_and_date,
            task2mouse,
            cohort_mouse_names,
            poked_by_port,
            trials_by_port,
            session_df,
            trial_data,
            )
        
        if plot_error_text != '':
            output_log_text += plot_error_text + '\n'

    return output_log_text

def make_all_plots(
    plot_dir,
    cohort_name,
    perf_by_mouse_and_date,
    task2mouse,
    cohort_mouse_names,
    poked_by_port,
    trials_by_port,
    session_df,
    trial_data,
    ):

    output_log_txt = ''
    
    # TODO: encase each individual plot in try/except
    try:
        f = plot_rcp_and_fc(
            perf_by_mouse_and_date, task2mouse, cohort_mouse_names)
        if f is None:
            output_log_txt += (
                "no data available to make perf plots"
            )
            print(output_log_txt)
        else:
            f.savefig(os.path.join(plot_dir, 
                '{}_01_plot_rcp_and_fc.pdf'.format(cohort_name)))
            plt.close(f)
    
        f = plot_trials_and_pokes_by_session(
            perf_by_mouse_and_date, task2mouse, cohort_mouse_names)
        f.savefig(os.path.join(plot_dir, 
            '{}_02_plot_trials_and_pokes_by_session.pdf'.format(cohort_name)))
        plt.close(f)
        
        #~ f = plot_pokes_by_port_every_session(
            #~ poked_by_port)
        #~ f.savefig(os.path.join(plot_dir, 
            #~ '{}_03_plot_pokes_by_port_every_session.pdf'.format(cohort_name)))
        #~ plt.close(f)
        
        #~ f = plot_trials_by_port_every_session(
            #~ trials_by_port)
        #~ f.savefig(os.path.join(plot_dir, 
            #~ '{}_04_plot_trials_by_port_every_session.pdf'.format(cohort_name)))
        #~ plt.close(f)
        
        #~ f = plot_sweep_task_by_param(
            #~ session_df, trial_data)
        #~ f.savefig(os.path.join(plot_dir, 
            #~ '{}_05_plot_sweep_task_by_param.pdf'.format(cohort_name)))
        #~ plt.close(f)
        
        #~ f1, f2 = imshow_first_poked_port_by_prp(
            #~ trial_data)
        #~ f1.savefig(os.path.join(plot_dir, 
            #~ '{}_06a_imshow_first_poked_port_by_prp.pdf'.format(cohort_name)))
        #~ f2.savefig(os.path.join(plot_dir, 
            #~ '{}_06b_imshow_first_poked_port_by_prp.pdf'.format(cohort_name)))
        #~ plt.close(f1)        
        #~ plt.close(f2)   
    
    except ZeroDivisionError:
        # Leave this here for intentional breakpoints
        raise
    
    except Exception as e:
        # Uncomment this raise for debugging
        # raise
        
        output_log_txt += (
            "error making plots" + 
            ''.join(traceback.format_exception(None, e, e.__traceback__))
            + '\n'
            )
        print(output_log_txt)

    return output_log_txt

def plot_rcp_and_fc(perf_by_mouse_and_date, task2mouse, mouse_names):
    # Plot fc and rcp by mouse over days
    unstacked = perf_by_mouse_and_date[
        ['fc', 'rcp', 'n_trials']].unstack('mouse')
    
    # Extract requested mice only
    unstacked = unstacked.reindex(mouse_names, level='mouse', axis=1)
    
    # Drop dates with no data for any mouse
    unstacked = unstacked.dropna(how='all')

    # Return immediately if no data
    if len(unstacked) == 0:
        return None

    # Extract recent dates only
    # Either do the last 20 sessions, or one month ago, whichever is later
    stop_date = unstacked.index.max()
    start_date1 = stop_date - datetime.timedelta(days=35)
    try:
        start_date2 = unstacked.index[-25]
    except IndexError:
        start_date2 = start_date1
    start_date = np.max([start_date2, start_date1])

    # Make plot
    f, axa = plt.subplots(3, 1, sharex=True, figsize=(8, 9))
    f.autofmt_xdate()
    f.subplots_adjust(right=.75, top=.95, bottom=.1)

    for mouse_name in mouse_names:
        # Dropna so we connect through missing data
        try:
            topl = unstacked['n_trials'][mouse_name].dropna()
        except KeyError:
            continue
        
        # Choose linestyle
        # Keep in mind there may be both poketrain and task sessions
        try:
            if mouse_name in task2mouse.loc['230201_SSS_fixed'].index.values:
                linestyle = '-'
            else:
                linestyle = '--'
        except:
            # e.g., if no mice are 230201_SSS_fixed
            linestyle = '--'
        
        axa[0].plot(topl, marker='o', mfc='none', linestyle=linestyle, label=mouse_name)
    axa[0].plot(unstacked['n_trials'].mean(1), color='k', lw=1.5)
    axa[0].set_ylabel('n_trials')
    axa[0].legend(bbox_to_anchor=(1, 1))

    for mouse_name in mouse_names:
        # Dropna so we connect through missing data
        try:
            topl = unstacked['rcp'][mouse_name].dropna()
        except KeyError:
            continue
        
        # Choose linestyle
        # Keep in mind there may be both poketrain and task sessions
        try:
            if mouse_name in task2mouse.loc['230201_SSS_fixed'].index.values:
                linestyle = '-'
            else:
                linestyle = '--'
        except:
            # e.g., if no mice are 230201_SSS_fixed
            linestyle = '--'
        
        axa[1].plot(topl, marker='o', mfc='none', linestyle=linestyle, label=mouse_name)
    axa[1].plot(unstacked['rcp'].mean(1), color='k', lw=1.5)
    axa[1].set_ylim((4, 0))
    axa[1].hlines(
        3.0, unstacked.index.min(), stop_date, color='k', linestyle='--', lw=1)
    axa[1].set_ylabel('rcp')
    axa[1].legend(bbox_to_anchor=(1, 1))

    for mouse_name in mouse_names:
        # Dropna so we connect through missing data
        try:
            topl = unstacked['fc'][mouse_name].dropna()
        except KeyError:
            continue
        
        # Choose linestyle
        # Keep in mind there may be both poketrain and task sessions
        try:
            if mouse_name in task2mouse.loc['230201_SSS_fixed'].index.values:
                linestyle = '-'
            else:
                linestyle = '--'
        except:
            # e.g., if no mice are 230201_SSS_fixed
            linestyle = '--'
        
        axa[2].plot(topl, marker='o', mfc='none', linestyle=linestyle, label=mouse_name)    
    axa[2].plot(unstacked['fc'].mean(1), color='k', lw=1.5)
    axa[2].set_ylim((0, 1))
    axa[2].hlines(
        1/7., unstacked.index.min(), stop_date, color='k', linestyle='--', lw=1)
    axa[2].set_ylabel('fc')
    axa[2].xaxis.set_major_formatter(myFmt)
    axa[2].legend(bbox_to_anchor=(1, 1))

    
    ## Set up xaxis
    # Label it
    axa[2].set_xlabel('date')

    # Tick every date we have
    axa[2].set_xticks(unstacked.index.values)
    
    # Set the lim
    axa[2].set_xlim([start_date, stop_date + datetime.timedelta(days=1)])
    
    # Center the ticks
    for tick in axa[2].xaxis.get_major_ticks():
        tick.label1.set_horizontalalignment('center')
        tick.label1.set_rotation('center')
        tick.label1.set_rotation(90)
    
    return f

def plot_trials_and_pokes_by_session(perf_by_mouse_and_date, task2mouse, mouse_names):
    # Plot trials and pokes by session
    f, axa = plt.subplots(2, 1, figsize=(8, 7))
    f.autofmt_xdate()
    f.subplots_adjust(right=.75, top=.95, bottom=.1)
    
    for mouse_name in mouse_names:
        # Choose linestyle
        # Keep in mind there may be both poketrain and task sessions
        try:
            if mouse_name in task2mouse.loc['230201_SSS_fixed'].index.values:
                linestyle = '-'
            else:
                linestyle = '--'
        except:
            # e.g., if no mice are 230201_SSS_fixed
            linestyle = '--'
        
        try:
            axa[0].plot(
                perf_by_mouse_and_date.loc[mouse_name]['n_trials'], 
                marker='o', linestyle=linestyle)
        except KeyError:
            print("warning: no data for mouse {}".format(mouse_name))
            continue
        
        try:
            axa[1].plot(
                perf_by_mouse_and_date.loc[mouse_name]['n_pokes'], 
                marker='o', linestyle=linestyle)
        except KeyError:
            print("warning: no data for mouse {}".format(mouse_name))
            continue

    axa[0].set_ylabel('trials')
    axa[1].set_xlabel('date')
    axa[1].set_ylabel('pokes')
    
    # This will be wrong if mice were skipped above
    axa[0].legend(mouse_names, bbox_to_anchor=(1, 1))
    axa[1].legend(mouse_names, bbox_to_anchor=(1, 1))
    
    axa[1].xaxis.set_major_formatter(myFmt)

    for tick in axa[1].xaxis.get_major_ticks():
        tick.label1.set_horizontalalignment('center')
    
    return f

def plot_pokes_by_port_every_session(poked_by_port):
    # Plot pokes by port
    f, ax = plt.subplots(figsize=(16, 6))
    ax.plot(poked_by_port)
    ax.legend(poked_by_port.columns, fontsize='xx-small', bbox_to_anchor=(1,1))
    ax.plot(poked_by_port.mean(1), 'k-')    
    ax.set_ylabel('pokes')
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    
    return f

def plot_trials_by_port_every_session(trials_by_port):
    # Plot trials by port
    f, ax = plt.subplots(figsize=(16, 6))
    f.subplots_adjust(left=.05, right=.8)
    ax.plot(trials_by_port)
    ax.legend(trials_by_port.columns, fontsize='xx-small', bbox_to_anchor=(1, 1))
    ax.plot(trials_by_port.mean(1), 'k-')
    ax.set_ylabel('trials')
    for tick in ax.get_xticklabels():
        tick.set_rotation(90)
    
    return f

def plot_sweep_task_by_param(session_df, trial_data):
    ## Get sessions
    # Select sessions that were done on a sweep task
    # and were pre-HL
    this_sessions = session_df.loc[
        session_df['protocol_filename'].str.contains('sweep')
        ].copy()
    
    #~ # Also filtering for after 5-27 (see above)
    #~ this_sessions = this_sessions.loc[
        #~ (session_df['first_trial'] >=
        #~ datetime.datetime(year=2022, month=5, day=27, hour=23), )        
        #~ ].copy()

    # Slice trial_data in the same way
    this_trial_data = trial_data.loc[
        trial_data.index.get_level_values('session_name').isin(
        this_sessions.index.get_level_values('session_name'))].copy()
    this_trial_data['is_correct'] = (this_trial_data['rcp'] == 0).astype(int)

    

    ## Error check param values
    this_trial_data2 = this_trial_data.reorder_levels(
        ['mouse', 'session_name', 'trial']).sort_index()
    
    params_to_check = [
        'stim_distracter_amplitude', 'stim_distracter_bandwidth',
        'stim_distracter_center_freq', 'stim_distracter_rate',
        'stim_distracter_temporal_std', 
        'stim_target_amplitude', 'stim_target_bandwidth',
        'stim_target_center_freq', 'stim_target_rate',
        'stim_target_temporal_std', 
        'stim_target_spatial_extent',
        'stim_n_distracters',
        ]

    # These params should always be the same
    assert (this_trial_data2['stim_distracter_amplitude'] == -2).all()
    assert (this_trial_data2['stim_distracter_bandwidth'] == 3000).all()
    assert (this_trial_data2['stim_distracter_center_freq'] == 5000).all()
    assert (this_trial_data2['stim_distracter_rate'] == 0).all()
    assert (this_trial_data2['stim_distracter_temporal_std'] == -1).all()
    assert (this_trial_data2['stim_target_spatial_extent'] == 0).all()
    assert (this_trial_data2['stim_target_bandwidth'] == 3000).all()
    assert (this_trial_data2['stim_n_distracters'] == 0).all()


    ## Check the parameters that varied
    param_l = [
        'stim_target_amplitude', 'stim_target_rate', 
        'stim_target_temporal_std', 'stim_target_center_freq']

    # Make figure
    f, axa = plt.subplots(
        1,
        len(param_l),
        figsize=(12, 4),
        sharey=True,
        )
    f.subplots_adjust(wspace=.4, hspace=.6, left=.1, right=.95, bottom=.15)
    
    for param in param_l:
        # Get ax
        ax = axa[
            param_l.index(param),
            ]
        
        # Aggregate
        by_session = this_trial_data2.groupby(
            ['mouse', param])['rcp'].mean()
        by_mouse = by_session.groupby(['mouse', param]).mean()
        
        # Plot
        ax.plot(by_mouse.unstack().T)
        ax.plot(by_mouse.unstack().mean(), 'k--')

        # Pretty
        ax.set_xlabel(param)
        ax.set_ylim((4, 1))
        ax.set_yticks((4, 3, 2, 1))
        ax.set_ylabel('rank of correct port')
        my.plot.despine(ax)

    return f

def imshow_first_poked_port_by_prp(trial_data):
    # Count poked_port vs RP
    poked_port_vs_rp = trial_data.groupby(
        ['mouse', 'first_port_poked', 'rewarded_port']
        ).size()
        
    # Count poked_port vs PRP
    poked_port_vs_prp = trial_data.groupby(
        ['mouse', 'first_port_poked', 'previously_rewarded_port']
        ).size().drop('', level='previously_rewarded_port')

    # Plot first port poked vs rewarded poke
    mouse_l = sorted(poked_port_vs_rp.index.levels[0])
    f1, axa = my.plot.auto_subplot(len(mouse_l), figsize=(12, 8))
    f1.subplots_adjust(wspace=.4, hspace=.4)
    for mouse in mouse_l:
        ax = axa.flatten()[mouse_l.index(mouse)]
        ax.set_title(mouse)
        topl = poked_port_vs_rp.loc[mouse].sort_index().unstack().sort_index(axis=1).fillna(0)
        topl = topl.divide(topl.sum())
        my.plot.imshow(topl, cmap=plt.cm.gray, ax=ax, clim=(0, .5))
        ax.set_xticks(range(topl.shape[1]))
        ax.set_yticks(range(topl.shape[0]))
        ax.set_xticklabels(topl.columns, size='xx-small', rotation=90)
        ax.set_yticklabels(topl.index, size='xx-small')
        ax.set_ylabel(topl.index.name)
        ax.set_xlabel(topl.columns.name)

    # Plot first port poked vs previously rewarded poke
    # Husky_2, Moon_1, Moon_2 strongly cycle leftward
    mouse_l = sorted(poked_port_vs_prp.index.levels[0])
    f2, axa = my.plot.auto_subplot(len(mouse_l), figsize=(12, 8))
    f2.subplots_adjust(wspace=.4, hspace=.4)
    for mouse in mouse_l:
        ax = axa.flatten()[mouse_l.index(mouse)]
        ax.set_title(mouse)
        topl = poked_port_vs_prp.loc[mouse].sort_index().unstack().sort_index(axis=1).fillna(0)
        topl = topl.divide(topl.sum())
        my.plot.imshow(topl, cmap=plt.cm.gray, ax=ax, clim=(0, .5))
        ax.set_xticks(range(topl.shape[1]))
        ax.set_yticks(range(topl.shape[0]))
        ax.set_xticklabels(topl.columns, size='xx-small', rotation=90)
        ax.set_yticklabels(topl.index, size='xx-small')
        ax.set_ylabel(topl.index.name)
        ax.set_xlabel(topl.columns.name)
    
    return [f1, f2]