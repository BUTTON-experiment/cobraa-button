import os.path

from stat import S_IRWXG,S_IRWXU
from shutil import rmtree
import warnings

import numpy as np
from numpy import sqrt
from numpy import array as npa
from numpy import power,absolute,logical_and,column_stack,zeros,empty,append,\
sqrt,absolute,recarray


from math import pow,exp,log10,pi,isinf

try:
    from rootpy.plotting import Canvas,Hist,Hist2D,Graph
    from rootpy.plotting.style import set_style
    from rootpy.io import root_open


    warnings.simplefilter("ignore")
except:
    print("Historical package rootpy is not loaded. This package is not needed.")

# This reads in flags and arguments from the command line and loads rates for the specified detector design.
# Author Marc Bergevin
# Adapted by Liz Kneale (2021)
# Adapted for BUTTON by Liz Kneale (2022)

docstring = """
    Usage: watchmakers.py [options]

    Arguments:

    Options:

    ## System options

    --force                Forcing the recreation of the root_file,bonsai_root_file and log folders
    -v                     Verbose. Allow print out of additional information.
    --cluster=<_clus>      Specify cluster to use (options: lassen, sheffield, warwick) [Default: local]
    --reset                Delete job, mac, log, raw, and reconstruction directories, start fresh.

    ## Create macros and job scripts for a user defined detector configuration

    -m                     Generate rat-pac macro files
    -j                     Create rat-pac/bonsai submision scripts for option above. Can be run with -m.
    --bonsai               Generate BONSAI fitting macro which can be used within RAT-PAC run (New for RAT-PAC2).
    --jobTime=<_jt>        Length of job in minutes for LASSEN [Default: 200]
    --energyEst=<_EE>      Default energy estimator (n9,n100,n400,nX) [Default: n9]
    -N=<_N>                Number of runs to simulate [Default: 40]

    ## Perform efficiency and sensitivity evaluation (after simulation and reconstruction).

    -M                     Merge result files from trial ntuples. Step one.
    --mergeRATFiles        Merge raw ratds files (off by default)
    --coincidences         Map the efficiencies of coincidences which pass the cuts (analysis step 1)
    --core                 Use the combined reconstruction (option to pass with -m, -j and --coincidences)
    --evtype=<_ev>         Set process to evaluate for coincidences
    --sensitivity          Calculate the rates for final optimisation of signal significance (analysis step 2)
    --triggers             Get the number of triggers for singles processes
    --backgrounds          Plot backgrounds as a function of distance from rPMT
    --positiveScan         Only look at nx delayed above nx prompt
    --negativeScan         only look at nx delayed below nx prompt
    --singlesrate          calculate singles rate per sec

    ############# Detector options ##############
    ## Define detector geometry and other features

    --expname=<_exp>       Name of the RAT-PAC2 experiment [Default: BUTTON] #Default is for the button folder within ratdb and for button.sh envirnment script
    --geofile=<_geo>       Name of detector geofile [Default: button_frame] # don't include the .geo at the end
    --muMetal=<_MM>        Implement muMetal [Default: 0]
    --lightCone=<_LC>      Implement lightConcentrators [Default: 0]
    --depth=<depthD>       Depth of detector (for fast neutron spectra) [Default: 2805.]
    --detectMedia=<_dM>    Detector media (doped_water,...) [Default: doped_water]
    --collectionEff=<CE>   Collection efficiency (e.g.: 0.85,0.67,0.475)
    --pmtModel=<_PMTM>     PMT Model (r7081_lqe/r7081_hqe for 10inch or r11780_lqe/r11780_hqe for 12inch)
    --vetoModel=<_vPMTM>   Veto PMT Model (ETEL, r7081_lqe/r7081_hqe for 10inch or r11780_lqe/r11780_hqe for 12inch)
    --photocath =<_PC>     PMT photocathode (R7081HQE)
    --pmtCtrPoint          Point inner PMTs of Watchman geometry to detector center

    # Options to allow scaling of PMT numbers/activity
    --rPMT=<_rpmt>         Inner PMT radius in mm [Default: 5700]
    --rU238_IP=<_ruip>     Relative U238 Inner PMTs level [Default: 1.0]
    --rT232_IP=<_rtip>     Relative Th232 Inner PMTs level [Default: 1.0]
    --rK40_IP=<_rkip>      Relative K40 Inner PMTs level [Default: 1.0]

    --lightSimWater        Option to run only decays for which singles rate >10-4 Hz (fiducial = rPMT-0.5;n9>9)
    --lightSimWbLS         Option to run only decays for which singles rate >10-4 Hz (fiducial = rPMT-0.5;n100>9)
    -e=<runBeamEntry>      Number of events to be simulated per macro [Default: 2500]
    --singles              Option to run the simulation of individual radioactive backgrounds

    
    ########### Optimisation options ###############
    ## Define the cuts/ranges over which to optimise
    ## (ranges also used for plotting backgrounds in extras)

    --minNXprompt=<_minNXp>      Minimum threshold number of direct hits [Default: 4.]
    --maxNXprompt=<_maxNXp>      Maximum threshold number of direct hits [Default: 30.]
    --minNXdelayed=<_minNXd>     Minimum threshold number of direct hits [Default: 4.]
    --maxNXdelayed=<_maxNXd>     Maximum threshold number of direct hits [Default: 30.]
    --minFid =<_minFid>          Minimum fiducial cut (distance from PMT radius) [Default: 0.1]
    --maxFid =<_maxFid>          Maximum fiducial cut (distance from PMT radius) [Default: 1.5]
    --binwidthNX=<_binNX>        Bin width for scan over nX cut range [Default: 1]
    --binwidthFid=<_binFid>      Bin width for scan over closest PMT cut range [Default: 0.1]
    --binwidthdT=<binT>          Bin width for scan over dT cut [Default: 10]
    --binwidthdR=<binR>          Bin width for scan over dR cut [Default: 0.1]
    --binwidthG=<binG>           Bin width for scan over goodness cut g [Default: 0.1]
    --dTmin=<_dTmin>             Minimum value for dt cut [Default: 130]
    --dTmax=<_dTmax>             Maximum value for dt cut [Default: 160]
    --dRmin=<_dRmin>             Mimumum value for dR cut [Default: 1.8]
    --dRmax=<_dRmax>             Maximum value for dR cut [Default: 2.2]
    --gmin=<_gmin>               Minimum value for g cut [Default: 0.1]
    --gmax=<_gmax>               Maximum value for g cut [Default: 0.3]
    --minEpmax=<_minEpmax>       Minimum value for maximum value of Ep [Default: 20.]
    --maxEpmax=<_maxEpmax>       Maximum value for maximum value of Ep [Default: 35.]
    --binwidthEpmax=<_binEp>     Bin width for scan over maximum value Ep [Default: 5.]
    -G=<Goodness>                Bonsai direction goodness parameter [Default: 0.1]
    --se=<_se>                   Default signal efficiency [Default: 1.00]

    ###### Signal options #######
    ## Define alternative signals
    --Hartlepool1                Uses 1-core Hartlepool (reactor 1, operating at higher power)
    --Hartlepool2                Uses 1-core Hartlepool signal (reactor 2, operating at lower power)
    --Heysham                    Uses Heysham reactor spectrum in place of Hartlepool
    --Heysham2                   2-core Heysham signal
    --HeyshamTorness             Heysham 2-core + Torness signal
    --Torness                    Torness signal
    --Gravelines                 Gravelines signal (all 6 cores)
    --HinkleyC                   Hinkley Point C signal (both cores)
    --Sizewell                   Sizewell signal (all cores)
    --GSH                        Gravelines, Hinkley Point C and Sizewell signal
    --SH                         Sizewell + Hinkley Point C signal
    --GH                         Gravelines + HInkley Point C signal

    # ################### Sensitivity metric options #########################
    # specify the sensitivity metric to use (default uses Gaussian statistics)

    --poisson              calculate significance and anomaly dwell time using poisson (gaussian-distributed bg)
    --poissonpoisson       calculate significance and anomaly dwell time using poisson (poisson-distributed bg)
    --knoll                calculate dwell time to 3 sigma detection at 95% confidence (gaussian sig and bg)
    --measurement          calculate dwell time to 3 sigma reactor measurement
    --2sigma               calculate dwell time to 2 sigma detection (gaussian) at 90% confidence (knoll)
    --optimiseSoB          optimise signal over background rather than dwell time (useful in stats-limited regime)
"""

try:
    import docopt
    arguments = docopt.docopt(docstring)

    print('\nUsing docopt as the user control interface\n')
except ImportError:
    print('docopt is not a recognized module, it is required to run this module')

if (arguments['--Heysham']):
        print("Using Heysham spectrum (all 4 cores) and assuming Hartlepool is off")


def loadSimulationParameters():
    #Chain and subsequent isotopes
    d = {}
    process = {}
   
    if arguments['--lightSimWater']:
        # Define which component and event type is associated with each process.
        # Removing negligible radioactive decays for Gd-water in 16m detector.
        # Only decays with rates > 10-3 Hz with fiducial rPMT-0.5m and n9>9 included.
	# Also includes 210Tl which can decay with a coincident beta-neutron.
        '''
        PMT             232Th: 208Tl, 212Bi,228Ac;      238U: 210Tl, 214Bi, 234Pa;       40K 
        PSUP            232Th: 208Tl;                   238U: 210Tl, 214Bi;              40K;    60Co;   54Mn
        IBEAM           232Th: 208Tl;                   238U: 210Tl, 214Bi; 
        TANK            232Th: 20i8Tl;                   238U: 210Tl, 214Bi;             40K;    60Co;   54Mn
        GD-WATER        232Th: 208Tl, 212Bi;            238U: 210Tl, 214Bi, 234Pa;
        ROCK (inner)    232Th: 208Tl;                   238U: 210Tl;                     Radiogenic neutrons
        ENCAPSULATION   232Th: 208Tl;                   238U: 210Tl, 214Bi;              40K;    60Co;   54Mn
        '''
        print('Running the lightSim option for water - only decays with singles rates > 10-3 and 210Tl are included \n')

        d['CHAIN_238U_NA'] = {'LIQUID':['210Tl', '214Bi', '234Pa'],\
                'PMT':[ '210Tl', '214Bi', '234Pa'],\
                'TANK':['210Tl', '214Bi'],\
                'IBEAM':['210Tl'],\
                'ROCK_2':['210Tl'],\
                'PSUP':['210Tl', '214Bi'],\
                'ENCAP':['210Tl', '214Bi']}

        d['CHAIN_232Th_NA'] = {'LIQUID':['208Tl'],\
                'PSUP':['208Tl'],\
                'PMT':['208Tl', '212Bi','228Ac'],\
                'TANK':['208Tl'],\
                'IBEAM':['208Tl'],\
                'ROCK_2':['208Tl'],\
                'ENCAP':['208Tl', '212Bi', '228Ac']}

        d['40K_NA'] = {'PMT':['40K'],\
                'ENCAP':['40K'],\
                'PSUP':['40K'],\
                'TANK':['40K']}

        d['60Co_NA'] = {'PSUP':['60Co'],\
                'ENCAP':['60Co'],\
                'TANK':['60Co']}

        d['54Mn_NA'] = {'PSUP':['54Mn'],\
                'ENCAP':['54Mn'],\
                'PSUP':['54Mn'],\
                'TANK':['54Mn']}

        d['RADIOGENIC'] = {'ROCK_2':['rock_neutrons']}


#        d['pn_ibd'] = {'LIQUID':['boulby_geo','hartlepool_1','hartlepool_2','boulby_worldbg','heysham_full','heysham_2','torness_full','gravelines_full','hinkley_C','sizewell_B']}

        d['singles'] = {'ALL':['singles']}
        d['A_Z'] = {'LIQUID':['li 9','n 17','he 8']}
        d['FASTNEUTRONS'] = {'ROCK_2':['fast_neutrons']}
        d['mono'] = {'LIQUID':['e-']}

        # Define what components are associated with each physical process.
        # Components included only where processes are non-negligible.
        process = {
        'CHAIN_238U_NA': ['PMT','PSUP','LIQUID','TANK','IBEAM','ROCK_2','ENCAP'],\
        'CHAIN_232Th_NA':['PMT','PSUP','LIQUID','TANK','IBEAM','ROCK_2','ENCAP'],\
        '40K_NA':        ['PMT','PSUP'],\
        '60Co_NA':       ['PSUP'],\
        'RADIOGENIC':    ['ROCK_2'],\
        #'pn_ibd':        ['LIQUID'],\
        'A_Z':           ['LIQUID'],\
        'singles':       ['ALL'],\
        'mono':          ['LIQUID'],\
        'FASTNEUTRONS':  ['ROCK_2'],\
        }

    elif arguments['--lightSimWbLS']:

        # Define which component and event type is associated with each process.
        # Removing negligible radioactive decays for Gd-WbLS in 16m detector.
        # Only decays with rates > 10-3 Hz with fiducial rPMT-0.5m and n100>9 included.
	# Also includes 210Tl which can decay with a coincident beta-neutron.
        d['CHAIN_238U_NA'] = {'LIQUID':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'PMT':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'TANK':['214Bi','210Tl'],\
                             'ROCK_2':['214Bi','210Tl'],\
                             'IBEAM':['214Bi','210Tl'],\
                             'PSUP':['234Pa','214Pb','214Bi','210Tl']}
        d['CHAIN_232Th_NA'] = {'LIQUID':['228Ac','208Tl'],\
                'PMT':['228Ac','212Bi','208Tl'],\
                'TANK':['228Ac','212Pb','208Tl'],\
                'ROCK_2':['212Bi','208Tl'],\
                'IBEAM':['208Tl'],\
                'PSUP':['228Ac','212Pb','208Tl']}
        d['CHAIN_235U_NA'] = {'LIQUID':['211Pb','207Tl'],\
                'PSUP':['211Pb']}

        d['40K_NA'] = {'LIQUID':['40K'],\
                'TANK':['40K'],\
                'IBEAM':['40K'],\
                'PSUP':['40K'],\
                'PMT':['40K'],\
                'ROCK_2':['40K']}

        d['60Co_NA'] = {'PSUP':['60Co'],\
                'TANK':['60Co'],\
                'IBEAM':['60Co']}
        d['137Cs_NA'] = {'PSUP':['137Cs']}
        #d['pn_ibd'] = {'LIQUID':['boulby_geo','hartlepool_1','hartlepool_2','boulby_worldbg','heysham_full','heysham_2','torness_full','gravelines_full','hinkley_C','sizewell_B']}

        d['singles'] = {'ALL':['singles']}
        d['A_Z'] = {'LIQUID':['li 9','n 17','he 8']}

        d['FASTNEUTRONS'] = {'ROCK_2':['fast_neutrons']}

        d['RADIOGENIC'] = {'ROCK_2':['rock_neutrons']}
        d['mono'] = {'LIQUID':['e-']}

        # Define what components are associated with each physical process
        # Components included only where processes are non-negligible.
        process = {
        'CHAIN_238U_NA':['PMT','PSUP','IBEAM','TANK','ROCK_2','LIQUID'],\
        'CHAIN_232Th_NA':['PMT','PSUP','IBEAM','TANK','ROCK_2','LIQUID'],\
        'CHAIN_235U_NA':['PSUP','LIQUID'],\
        '40K_NA':['LIQUID','PMT','PSUP', 'IBEAM','TANK','ROCK_2'],\
        '60Co_NA':['TANK','PSUP','IBEAM'],\
        '137Cs_NA':['PSUP'],\
        #'pn_ibd':['LIQUID'],\
        'A_Z':['LIQUID'],\
        'singles':['ALL'],\
        'mono':['LIQUID'],\
        'RADIOGENIC':['ROCK_2'],\
        'FASTNEUTRONS':['ROCK_2']}

    else:

        print('Running the full range of decays - NB some may never trigger \n')

        d['CHAIN_238U_NA'] = {'LIQUID':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'PMT':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'TANK':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'ROCK_2':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'IBEAM':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'PSUP':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'ENCAP':['234Pa','214Pb','214Bi','210Bi','210Tl'],\
                             'LINER':['234Pa','214Pb','214Bi','210Bi','210Tl']}

        d['CHAIN_232Th_NA'] = {'LIQUID':['228Ac','212Pb','212Bi','208Tl'],\
                'PMT':['228Ac','212Pb','212Bi','208Tl'],\
                'TANK':['228Ac','212Pb','212Bi','208Tl'],\
                'ROCK_2':['228Ac','212Pb','212Bi','208Tl'],\
                'IBEAM':['228Ac','212Pb','212Bi','208Tl'],\
                'PSUP':['228Ac','212Pb','212Bi','208Tl'],\
                'ENCAP':['228Ac','212Pb','212Bi','208Tl'],\
                'LINER':['228Ac','212Pb','212Bi','208Tl']}

        d['CHAIN_235U_NA'] = {'LIQUID':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'PMT':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'TANK':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'IBEAM':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'PSUP':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'ENCAP':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'ROCK_2':['231Th','223Fr','211Pb','211Bi','207Tl'],\
                'LINER':['231Th','223Fr','211Pb','211Bi','207Tl']}

        d['40K_NA'] = {'LIQUID':['40K'],\
                'TANK':['40K'],\
                'IBEAM':['40K'],\
                'PSUP':['40K'],\
                'PMT':['40K'],\
                'ROCK_2':['40K'],\
                'ENCAP':['40K'],\
                'LINER':['40K']}

        d['60Co_NA'] = {'PSUP':['60Co'],\
                'TANK':['60Co'],\
                'PMT':['60Co'],\
                'IBEAM':['60Co'],\
                'ENCAP':['60Co'],\
                'LINER':['60Co']}

        d['54Mn_NA'] = {'PSUP':['54Mn'],\
                'TANK':['54Mn'],\
                'ENCAP':['54Mn']}

        d['137Cs_NA'] = {'PSUP':['137Cs'],\
                'TANK':['137Cs'],\
                'IBEAM':['137Cs']}

        #d['pn_ibd'] = {'LIQUID':['boulby_geo','hartlepool_1','hartlepool_2','boulby_worldbg','heysham_full','heysham_2','torness_full','gravelines_full','hinkley_C','sizewell_B']}

        d['singles'] = {'ALL':['singles']}
        d['A_Z'] = {'LIQUID':['li 9','n 17','he 8']}

        d['FASTNEUTRONS'] = {'ROCK_2':['fast_neutrons'],\
                             'ROCK_1':['fast_neutrons']}
     
        d['RADIOGENIC'] = {'ROCK_1':['rock_neutrons'],\
                           'ROCK_2':['rock_neutrons']}
        d['mono'] = {'LIQUID':['e+','e-','gamma']}

        # Define what components are associated with each physical process
        # (all processes included, some may not trigger a detector response)
        process = {
        'CHAIN_238U_NA':['PMT','PSUP','IBEAM','TANK','ROCK_2','LIQUID','ENCAP','LINER'],\
        'CHAIN_232Th_NA':['PMT','PSUP','IBEAM','TANK','ROCK_2','LIQUID','ENCAP','LINER'],\
        'CHAIN_235U_NA':['TANK','PSUP','LIQUID','IBEAM','PMT','ROCK_2','ENCAP','LINER'],\
        '40K_NA':['LIQUID','PMT','PSUP', 'IBEAM','TANK','ROCK_2','ENCAP','LINER'],\
        '60Co_NA':['TANK','PSUP','IBEAM','PMT','ENCAP','LINER'],\
        '54Mn_NA':['PSUP','TANK','ENCAP'],\
        '137Cs_NA':['TANK','PSUP','IBEAM'],\
        #'pn_ibd':['LIQUID'],\
        'A_Z':['LIQUID'],\
        'singles':['ALL'],\
        'mono':['LIQUID'],\
        'RADIOGENIC':['ROCK_2','ROCK_1'],\
        'FASTNEUTRONS':['ROCK_2','ROCK_1']}
      
        for p in process:
                for loc in process[p]:
                        print("{0}: {1}: {2}".format(p,loc,d[p][loc]))  
                print("")

    ## This part defines the rates for the given detector configuration

    ## First column is the production rate per second of the process, second column is the fractional changes to the event generation.
    # Get fractional changes to 238U, 232Th and 40K for PMTs, if arguments used
    uip   = float(arguments["--rU238_IP"])
    tip    = float(arguments["--rT232_IP"])
    kip    = float(arguments["--rK40_IP"])

    print('Using rates for BUTTON')
    # TODO removed for now, need correct rates if used
    # TODO spontaneous fission not included
    # TODO only 9Li, 17N and 8He are included for spallation
    jobRate = {\
#'hartlepool_1_LIQUID_pn_ibd': [1.052e-04*pmtVolCorr , 1],\
#'hartlepool_2_LIQUID_pn_ibd': [7.889e-05*pmtVolCorr , 1],\
#'boulby_geo_LIQUID_pn_ibd': [6.368e-06*pmtVolCorr , 1],\
#'boulby_world_LIQUID_pn_ibd': [2.146e-05*pmtVolCorr , 1],\
#'heysham_full_LIQUID_pn_ibd': [1.231e-05*pmtVolCorr , 1],\
#'heysham_2_LIQUID_pn_ibd': [7.005e-06*pmtVolCorr , 1],\
#'torness_full_LIQUID_pn_ibd': [4.422e-06*pmtVolCorr , 1],\
#'boulby_worldbg_LIQUID_pn_ibd': [1.491e-05*pmtVolCorr , 1],\
#'gravelines_full_LIQUID_pn_ibd': [2.6e-06*pmtVolCorr , 1],\
#'hinkley_C_LIQUID_pn_ibd': [2.565e-06*pmtVolCorr , 1],\
#'sizewell_B_LIQUID_pn_ibd': [1.331e-06*pmtVolCorr , 1],\
'40K_LIQUID_40K_NA': [1.20e-1, 50], \
'40K_PMT_40K_NA': [3.48e+02 * kip, 50], \
'40K_IBEAM_40K_NA': [0, 50], \
'40K_PSUP_40K_NA': [4.92e+00, 50], \
'40K_TANK_40K_NA': [9.70e+01, 50], \
'40K_ROCK_2_40K_NA': [2.23e+06, 1000], \
'40K_ENCAP_40K_NA': [3.87e+01, 50], \
'40K_LINER_40K_NA': [5.08e+00, 50], \
'234Pa_PMT_CHAIN_238U_NA': [1.07e+02 * uip, 50], \
'214Pb_PMT_CHAIN_238U_NA': [1.07e+02 * uip, 50], \
'214Bi_PMT_CHAIN_238U_NA': [1.07e+02 * uip, 50], \
'210Bi_PMT_CHAIN_238U_NA': [1.07e+02 * uip, 50], \
'210Tl_PMT_CHAIN_238U_NA': [1.07e+02*0.0002 * uip, 50], \
'234Pa_IBEAM_CHAIN_238U_NA': [0, 1], \
'214Pb_IBEAM_CHAIN_238U_NA': [0, 1], \
'214Bi_IBEAM_CHAIN_238U_NA': [0, 1], \
'210Bi_IBEAM_CHAIN_238U_NA': [0, 1], \
'210Tl_IBEAM_CHAIN_238U_NA': [0*0.0002, 1], \
'234Pa_PSUP_CHAIN_238U_NA': [6.56e+00, 50], \
'214Pb_PSUP_CHAIN_238U_NA': [6.56e+00, 50], \
'214Bi_PSUP_CHAIN_238U_NA': [6.56e+00, 50], \
'210Bi_PSUP_CHAIN_238U_NA': [6.56e+00, 50], \
'210Tl_PSUP_CHAIN_238U_NA': [6.56e+00*0.0002, 50], \
'234Pa_TANK_CHAIN_238U_NA': [3.20e+01, 50], \
'214Pb_TANK_CHAIN_238U_NA': [3.20e+01, 50], \
'214Bi_TANK_CHAIN_238U_NA': [3.20e+01, 50], \
'210Bi_TANK_CHAIN_238U_NA': [3.20e+01, 50], \
'210Tl_TANK_CHAIN_238U_NA': [3.20e+01*0.0002, 50], \
'234Pa_ROCK_2_CHAIN_238U_NA': [3.24e+04, 1000], \
'214Pb_ROCK_2_CHAIN_238U_NA': [3.24e+04, 1000], \
'214Bi_ROCK_2_CHAIN_238U_NA': [3.24e+04, 1000], \
'210Bi_ROCK_2_CHAIN_238U_NA': [3.24e+04, 1000], \
'210Tl_ROCK_2_CHAIN_238U_NA': [3.24e+04*0.0002, 1000], \
'234Pa_LIQUID_CHAIN_238U_NA': [2.99e-2, 50], \
'214Pb_LIQUID_CHAIN_238U_NA': [2.99e-2, 50], \
'214Bi_LIQUID_CHAIN_238U_NA': [2.99e-2, 50], \
'210Bi_LIQUID_CHAIN_238U_NA': [2.99e-2, 50], \
'210Tl_LIQUID_CHAIN_238U_NA': [2.99e-2*0.0002, 50], \
'234Pa_ENCAP_CHAIN_238U_NA': [1.92e+01, 50], \
'214Pb_ENCAP_CHAIN_238U_NA': [1.92e+01, 50], \
'214Bi_ENCAP_CHAIN_238U_NA': [1.92e+01, 50], \
'210Bi_ENCAP_CHAIN_238U_NA': [1.92e+01, 50], \
'210Tl_ENCAP_CHAIN_238U_NA': [1.92e+01*0.0002, 50], \
'234Pa_LINER_CHAIN_238U_NA': [2.91e+00, 50], \
'214Pb_LINER_CHAIN_238U_NA': [2.91e+00, 50], \
'214Bi_LINER_CHAIN_238U_NA': [2.91e+00, 50], \
'210Bi_LINER_CHAIN_238U_NA': [2.91e+00, 50], \
'210Tl_LINER_CHAIN_238U_NA': [2.91e+00*0.0002, 50], \
'228Ac_PMT_CHAIN_232Th_NA': [9.38e+01 * tip, 50], \
'212Pb_PMT_CHAIN_232Th_NA': [9.38e+01 * tip, 50], \
'212Bi_PMT_CHAIN_232Th_NA': [9.38e+01*0.64 * tip, 50], \
'208Tl_PMT_CHAIN_232Th_NA': [9.38e+01*0.36 * tip, 50], \
'228Ac_IBEAM_CHAIN_232Th_NA': [0, 1], \
'212Pb_IBEAM_CHAIN_232Th_NA': [0, 1], \
'212Bi_IBEAM_CHAIN_232Th_NA': [0*0.64, 1], \
'208Tl_IBEAM_CHAIN_232Th_NA': [0*0.36, 1], \
'228Ac_PSUP_CHAIN_232Th_NA': [5.64e-01, 50], \
'212Pb_PSUP_CHAIN_232Th_NA': [5.64e-01, 50], \
'212Bi_PSUP_CHAIN_232Th_NA': [5.64e-01*0.64, 50], \
'208Tl_PSUP_CHAIN_232Th_NA': [5.64e-01*0.36, 50], \
'228Ac_TANK_CHAIN_232Th_NA': [2.50E+00, 50], \
'212Pb_TANK_CHAIN_232Th_NA': [2.50E+00, 50], \
'212Bi_TANK_CHAIN_232Th_NA': [2.50E+00*0.64, 50], \
'208Tl_TANK_CHAIN_232Th_NA': [2.50E+00*0.36, 50], \
'228Ac_ROCK_2_CHAIN_232Th_NA': [3.74e+04, 1000], \
'212Pb_ROCK_2_CHAIN_232Th_NA': [3.74e+04, 1000], \
'212Bi_ROCK_2_CHAIN_232Th_NA': [3.74e+04*0.64, 1000], \
'208Tl_ROCK_2_CHAIN_232Th_NA': [3.74e+04*0.36, 1000], \
'228Ac_LIQUID_CHAIN_232Th_NA': [2.99e-03, 1], \
'212Pb_LIQUID_CHAIN_232Th_NA': [2.99e-03, 1], \
'212Bi_LIQUID_CHAIN_232Th_NA': [2.99e-03*0.64, 1], \
'208Tl_LIQUID_CHAIN_232Th_NA': [2.99e-03*0.36, 1], \
'228Ac_ENCAP_CHAIN_232Th_NA': [8.39e+00, 50], \
'212Pb_ENCAP_CHAIN_232Th_NA': [8.39e+00, 50], \
'212Bi_ENCAP_CHAIN_232Th_NA': [8.39e+00*0.64, 50], \
'208Tl_ENCAP_CHAIN_232Th_NA': [8.39e+00*0.36, 50], \
'228Ac_LINER_CHAIN_232Th_NA': [1.99e-01, 50], \
'212Pb_LINER_CHAIN_232Th_NA': [1.99e-01, 50], \
'212Bi_LINER_CHAIN_232Th_NA': [1.99e-01*0.64, 50], \
'208Tl_LINER_CHAIN_232Th_NA': [1.99e-01*0.36, 50], \
'231Th_IBEAM_CHAIN_235U_NA': [0, 50], \
'223Fr_IBEAM_CHAIN_235U_NA': [0*0.0138, 50], \
'211Pb_IBEAM_CHAIN_235U_NA': [0, 50], \
'211Bi_IBEAM_CHAIN_235U_NA': [0*0.00270, 50], \
'207Tl_IBEAM_CHAIN_235U_NA': [0, 50], \
'231Th_PSUP_CHAIN_235U_NA': [3.02e-01, 50], \
'223Fr_PSUP_CHAIN_235U_NA': [3.02e-01*0.0138, 50], \
'211Pb_PSUP_CHAIN_235U_NA': [3.02e-01, 50], \
'211Bi_PSUP_CHAIN_235U_NA': [3.02e-01*0.00270, 50], \
'207Tl_PSUP_CHAIN_235U_NA': [3.02e-01, 50], \
'231Th_TANK_CHAIN_235U_NA': [1.01e+00, 50], \
'223Fr_TANK_CHAIN_235U_NA': [1.01e+00*0.0138, 50], \
'211Pb_TANK_CHAIN_235U_NA': [1.01e+00, 50], \
'211Bi_TANK_CHAIN_235U_NA': [1.01e+00*0.00270, 50], \
'207Tl_TANK_CHAIN_235U_NA': [1.01e+00, 50], \
'231Th_LIQUID_CHAIN_235U_NA': [1.40e-03, 1], \
'223Fr_LIQUID_CHAIN_235U_NA': [1.40e-03*0.0138, 1], \
'211Pb_LIQUID_CHAIN_235U_NA': [1.40e-03, 1], \
'211Bi_LIQUID_CHAIN_235U_NA': [1.40e-03*0.00270, 1], \
'207Tl_LIQUID_CHAIN_235U_NA': [1.40e-03, 1], \
'231Th_PMT_CHAIN_235U_NA': [4.93e+00, 1], \
'223Fr_PMT_CHAIN_235U_NA': [4.93e+00*0.0138, 1], \
'211Pb_PMT_CHAIN_235U_NA': [4.93e+00, 1], \
'211Bi_PMT_CHAIN_235U_NA': [4.93e+00*0.00270, 1], \
'207Tl_PMT_CHAIN_235U_NA': [4.93e+00, 1], \
'231Th_LINER_CHAIN_235U_NA': [1.34e-01, 1], \
'223Fr_LINER_CHAIN_235U_NA': [1.34e-01*0.0138, 1], \
'211Pb_LINER_CHAIN_235U_NA': [1.34e-01, 1], \
'211Bi_LINER_CHAIN_235U_NA': [1.34e-01*0.00270, 1], \
'207Tl_LINER_CHAIN_235U_NA': [1.34e-01, 1], \
'231Th_ROCK_2_CHAIN_235U_NA': [1.49e+03, 1], \
'223Fr_ROCK_2_CHAIN_235U_NA': [1.49e+03*0.0138, 1], \
'211Pb_ROCK_2_CHAIN_235U_NA': [1.49e+03, 1], \
'211Bi_ROCK_2_CHAIN_235U_NA': [1.49e+03*0.00270, 1], \
'207Tl_ROCK_2_CHAIN_235U_NA': [1.49e+03, 1], \
'231Th_ENCAP_CHAIN_235U_NA': [9.44e-01, 1], \
'223Fr_ENCAP_CHAIN_235U_NA': [9.44e-01*0.0138, 1], \
'211Pb_ENCAP_CHAIN_235U_NA': [9.44e-01, 1], \
'211Bi_ENCAP_CHAIN_235U_NA': [9.44e-01*0.00270, 1], \
'207Tl_ENCAP_CHAIN_235U_NA': [9.44e-01, 1], \
'60Co_IBEAM_60Co_NA': [0, 50], \
'60Co_TANK_60Co_NA': [6.60e+01, 50], \
'60Co_PSUP_60Co_NA': [6.14e+00, 50], \
'60Co_PMT_60Co_NA': [5.49e+02, 50], \
'60Co_ENCAP_60Co_NA': [9.90e-01, 50], \
'60Co_LINER_60Co_NA': [3.52e-03, 50], \
'54Mn_TANK_54Mn_NA': [1.20e+01, 50], \
'54Mn_PSUP_54Mn_NA': [1.29e+00, 50], \
'54Mn_ENCAP_54Mn_NA': [3.76e-01, 50], \
'137Cs_IBEAM_137Cs_NA': [0, 50], \
'137Cs_TANK_137Cs_NA': [0, 50], \
'137Cs_PSUP_137Cs_NA': [0, 50], \
'li9_LIQUID_A_Z': [2.357E-06,1], \
'n17_LIQUID_A_Z': [1.441E-06,1],\
'he8_LIQUID_A_Z': [8.986E-08,1],\
'singles_ALL_singles': [ 996951.6168340801,1],\
'e-_LIQUID_mono':[1,1],\
'e+_LIQUID_mono':[1,1],\
'gamma_LIQUID_mono':[1,1],\
'rock_neutrons_ROCK_2_RADIOGENIC': [6.58E-1,1],\
'rock_neutrons_ROCK_1_RADIOGENIC': [6.54, 1],\
'fast_neutrons_ROCK_2_FASTNEUTRONS': [8.26E-03, 1]}

    return d,process,jobRate

