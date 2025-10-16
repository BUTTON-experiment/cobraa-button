**Cobraa**
The Coincident-background reactor antineutrino analysis is an analysis for reactor discovery via the simulation and evaluation of coincident events. It can also optionally use reconstruction of coincident events. Currently for Button it is being used to study individual background rates so it is not being used for coincidences.

It can be used alongside BONSAI reconstruction.

##**To install:**
Navigate to the same directory level as where BUTTON-RAT2 is installed
If you are just going to use cobraa:
```git clone git@github.com:BUTTON-experiment/cobraa-button.git```
If you are planning on using it for development and changing anything in the program please fork the repository directly on the GitHub and clone that fork instead.

```cd cobraa-button```

```./configure```

```source env_cobraa.sh```

##**Basic Use:**
1. Create macros.
	For Gd-water, the material is called doped_water, use

	```cobraa -m -j -e 2000 -N 1 --singles --bonsai```

	For WbLS with 1%LS, the material is called wbls_gd_01pct_ly100_WM_0121, use

	```cobraa -m -j -e 2000 -N 1 --singles --bonsai --detectMedia wbls_gd_01pct_ly100_WM_0121```

	These options are all written out in load.py. For this option -m = macros are created, -j = create submission scripts, -e = how many events simulated per macro (keep in mind most individual backgrounds will actually simulate 50x this amount usually except U235 chain ones), -N = number of runs to simulate (default is 40 if you do not include this). --singles will let you run each radioactive background separately, --bonsai generates a bonsai fitting macro, --detectMedia allows you to specify the medium in the detector, the only ones with full optics information are doped_water and the WbLS wbls_gd_01pct_ly100_WM_0121.
2. Run jobs (jobs run locally by default)
   
	```source job/job<specific isotope/material you want>.sh```

	If you want to run in a cluster for step 1 include, for example, --cluster Edinburgh. This will change job/job<specific run>.sh to a submission script format Check in io_operations.py to see if one of the existing formats is suitable for your system or if you need to make your own.

4. Merge ntuple root files and calculate background rates
   
	For Gd-water:

	```cobraa -M --singles --triggers```

	Output file in this case will be called 'button_background_triggers_BUTTON_singles_doped_water.csv'

	For WbLS with 1%LS:

	```cobraa -M --singles --triggers --detectMedia wbls_gd_01pct_ly100_WM_0121```

	Output file will be called 'button_background_triggers_BUTTON_singles_wbls_gd_01pct_ly100_WM_0121.csv'


### **Old README instructions from WATCHMAN coincidence**
All of the following text was from cobra usage for watchman and likely early Button. A lot of this will probably still work, but has not been tested recently.

**Cobraa Coincident-background reactor antineutrino analysis** is an analysis for reactor discovery via the simulation and evaluation of coincident events. It can also optionally use reconstruction of coincident events.

It's a toolchain which handles full-detector simulation through to sensitivity analysis
for the current NEO detector design options: 16m/22m with Gd-water or Gd-WbLS.

Adapted from the WATCHMAN Watchmakers package (Author: Marc Bergevin, LLNL), it constitutes a significant overhaul of the original Watchmakers code. Retains the convenience of the directory organisation and macro/job production but incorporates streamlining and a full analysis update.

To be used alongside the FRED (BONSAI) reconstruction or CoRe (BONSAI) pair reconstruction.


Analysis performs full evaluation of coincidences for both signal and background and 
optimises sensitivity to a reactor as a function of cuts in up to 7 dimensions: 

1. Prompt energy threshold
2. Delayed energy threshold
3. Fiducial volume
4. Time between triggers dT
5. Distance between triggers dR (FRED only)
6. Fit quality (BONSAI timing goodness)
7. Maximum prompt energy


To install:

    $git clone https://github.com/ait-watchman/cobraa

    $cd cobraa

    $./configure

    $source env_wm.sh


**Basic use:**

1. Create macros and simulation jobs for a small-ish number of events (16m/Gd-water/20% photocoverage by default)

     ```cobraa -m -j -e 2500 --lightSimWater```

2. Run jobs (locally by default)

   ```source job/job*.sh```

3. Run FRED or CoRe reconstruction (this stage is not incorporated into Cobraa)

4. Merge ntuple root files from reconstruction

   ```cobraa -M```   

4. Map coincidences after cuts

     ```cobraa --coincidences [--core]```

5. Calculate rates and optimise signal significance

     ```cobraa --sensitivity [--core]```


See Wiki for more details
