**Cobraa**

It's a toolchain which handles full-detector simulation through to sensitivity analysis for BUTTON or any other input geometry and different fills.

Adapted by Liz Kneale from the WATCHMAN Watchmakers package (Author: Marc Bergevin, LLNL), it constitutes a significant overhaul of the original Watchmakers code. Retains the convenience of the directory organisation and macro/job production but incorporates streamlining and a full analysis update. Updated by Emma Ellingwood for the BUTTON experiment.


## **To install:**
Navigate to the same directory level as where BUTTON-RAT2 is installed

If you are just going to use cobraa:

```git clone git@github.com:BUTTON-experiment/cobraa-button.git```

If you are planning on using it for development and changing anything in the program please fork the repository directly on the GitHub and clone that fork instead.

```cd cobraa-button```

```./configure```

```source env_cobraa.sh```




### **Using cobraa for reactor neutrino studies:**
Note that this is a work in progress. There are still things (as of 2026-03-04) that have not been worked out, for example how many of events in each of the reactions needs to be run or what exact statistical mode should be used for the significance.

1. Create macros and simulation jobs for a small-ish number of events (Gd-water by default, here showing 1% WbLS). Change number of events (-e) and number of runs (-N) if you want.

     ```cobraa -m -j -e 400 -N 1 --bonsai --detectMedia wbls_gd_01pct_ly100_WM_0121```
     Can also make the jobs to be able to run in a cluster. See io_operations.py for available clusters and just add '--cluster=<cluster name>' to the line above filling in whatever cluster has the right format for you.

2. Run jobs (locally by default if a cluster has not been defined)

   ```source job/job*.sh```

   For the reactor neutrinos you need to run the following reactions:
   	• Li9
	• N17
	• Reactor (like hartlepool_1)
	• Other reactors (like hartlepool_2, gravelines_full, heysham_2, heysham_full, sizewell_B, torness_full, hinkley_C)
	• Boulby_geo
	• Boulby_worldbg
	• Singles

   Output files will be saved in  reconstructed_root_files_BUTTON_<material>

3. Merge ntuple root files from reconstruction

   ```cobraa -M --detectMedia wbls_gd_01pct_ly100_WM_0121```
   
4. Map coincidences after cuts

     ```cobraa --coincidences --detectMedia wbls_gd_01pct_ly100_WM_0121 [options]```
     For example, ```cobraa --coincidences --detectMedia wbls_gd_01pct_ly100_WM_0121 --maxNXprompt 7 --maxNXdelayed 7 --dRmax 1.8 --maxEpmax 30```
     type cobraa --help for options

5. Calculate rates and optimise signal significance

     ```cobraa --coincidences --detectMedia wbls_gd_01pct_ly100_WM_0121 [options]```
     If you choose options in the coincidence it appears to be good to include them here as well.
     For example, ```cobraa --coincidences --detectMedia wbls_gd_01pct_ly100_WM_0121 --maxNXprompt 7 --maxNXdelayed 7 --dRmax 1.8 --maxEpmax 30```



### **Using cobraa for detector background studies:**

1. Create macros and simulation jobs (Gd-water by default, here showing 1% WbLS). Note that for most 238U and 232Th chains for different components, the actual number of events is 50x the number of events given in -e. If a particular component decay has a very low activity it may be necessary to run more events in order to get any detectable signals.

     ```cobraa -m -j -e 2000 -N 1 --singles --bonsai --detectMedia wbls_gd_01pct_ly100_WM_0121```

2. Run jobs (locally by default)

   ```source job/job*.sh```

   Output files will be saved in  reconstructed_root_files_BUTTON_singles_<material>

3. Merge ntuple root files from reconstruction

   ```cobraa -M --singles --trigger --detectMedia wbls_gd_01pct_ly100_WM_0121```

4. Check background rate results are found in 'button_background_triggers_BUTTON_singles_wbls_gd_01pct_ly100_WM_0121.csv' for WbLS. If the earlier rate columns are non-zero but the last rate for nhits>3 is zero then potentially run more events. You can also run more events if you want to cover a specific amount of live time for a reaction.



See Wiki for more details
