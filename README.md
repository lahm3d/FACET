# FACET
[Floodplain and Channel Evaluation Toolkit]

FACET is a standalone Python tool that uses open source modules to map the floodplain extent and compute stream channel and floodplain geomorphic metrics such as channel width, streambank height, active floodplain width, and stream slope from DEMs. 

FACET currently contains several automated methods for extracting metrics including:

Cross Section Automation
- Cross sections automatically created parallel to reach at user specified spacing.
- Geomorphic metrics are calculated at each cross section and summarized by reach.

Identifying Channel Banks using Curvature
- Stream channel banks are delineated by calculating curvature (two methods exist) along the stream channel network.
- Curvature is calculated within a moving window that traverses the stream network, followed by the application of a threshold to identify grid cells representing the bank.
- Channel width for the reach is then computed using a buffering technique applied to each reach segments at user-specified length (e.g., 100m).

Identifying Floodplain Extent using Height Above Nearest Drainage (HAND)
- The active floodplain is delineated based on the HAND technique. The HAND grid is the elevation of every grid cell relative to the nearest stream channel cell it drains to. 
- Field data is used to calibrate the HAND elevation threshold that defines floodplain extent.
- Floodplain and channel metrics can be calculated using 1D and/or 2D cross sections of the HAND grid.
- Analysis of the HAND grid also provides a method for mapping the stream channel at bankfull stage.


# Setting up FACET (***Work in progress***)

## Requirements:
 
 * Anaconda (Python 3.6)
 * WhiteboxTools (*not Whitebox GAT*)
 * TauDEM  (*including its dependencies*)

## 1. Installation guide:
 * [Download and install Anaconda](https://docs.anaconda.com/anaconda/install/). It is recommended that you follow the instructions in the guide. Alternatively, you can also install Miniconda to save space
 * [Download and install TauDEM](http://hydrology.usu.edu/taudem/taudem5/downloads.html)
 * [Download and install Git](https://gitforwindows.org/) (*Downloading git is optional*) 

## 2. Set-up:

First, identify where you are going to store FACET code and the data. In this tutorial, the code and data will be saved under `c:\chesapeake_bay`, if it doesn't exist please create it. 

**How to get FACET code?** 

There are two methods to get the code

1. Easiest method : FACET can be downloaded directly from GitHub [here](https://github.com/lahm3d/FACET/archive/develop.zip) (***make sure to select develop branch***), unzip and place it under `c:\cheaspeake_bay` folder
2. Get FACET from git (see instructions below)


For contributors and those who have git installed:

1. Open 'git bash' window from your Windows Start button and navigate to `C:\chesapeake_bay` 
    
        cd c:\chesapeake_bay

2. Now download FACET code:
   
        git clone https://github.com/lahm3d/FACET.git

3. Navigate to FACET folder and check out the latest branch `develop`

        cd FACET/
        git checkout develop

You've successfully download FACET code and switched to latest branch

## 3. Anaconda and Whitebox Tools

### Setting up Whitebox Tools

[Install WhiteboxTools](https://www.uoguelph.ca/~hydrogeo/WhiteboxTools/download.html) and [user manual](https://jblindsay.github.io/wbt_book/intro.html). Download the latest version of WBT. *Note: FACET uses WhiteboxTools (WBT), not Whitebox Geospatial Analysis Tools (GAT)* 

Unzip `WhiteboxTools_win_amd64.zip` and extract the `WBT` folder under `c:\cheaspeake_bay`

The file structure should look like this:
       
        c:\
        └── chesapeake_bay
            ├── FACET
            └── WBT

### Setting up Anaconda

Open Window's Start button, type 'Anaconda Prompt' and launch the prompt. Next type in the following cmd line to navigate to `c:\chesapeake_bay\FACET` folder

        cd c:\chesapeake_bay\FACET

Now we are going to create an unique environment for FACET copy and paste the following command:

        conda env create -f c:\chesapeake_bay\FACET\facet36_2019.04.02.yml

This creates a new environment called `facet36` and all the relevant packages needed. Next step is to activate the environment and run FACET

After launching Anaconda prompt the window displays:

        (base) C:\chesapeake_bay\FACET>

"base" is the base environment that is currently active, we want to switch from **base** to **facet36**. To activate the new environment:

        activate facet36

Now the prompt should display: 

        (facet36) C:\chesapeake_bay\FACET>

This means you've successfully activated FACET environment and this is where you will be running FACET.

## 4. Configuration file and data structure

### Configuration file

Under FACET folder you should see `config.ini` file and it can be opened in any text editor. At present, we recommend modifying the configurations under `[paths and flags]` and leaving other values as defaults. In future, additional documentation and usage on other parameters and variables will be provided. 

`.INI` syntax instructions are provided in the file as well. Lastly, carefully review the file before executing FACET code.

        #*****************************************************************#
        # Module Name: config.ini                                         #
        # Type       : FACET configuration file                           #
        # Function   : Define the configuration of a FACET run            #
        # for comments use ; or # and no in-line comments                 #
        # values can be assigned using = or :                             #
        # for paths use / -- do not use \ or \\                           #
        #*****************************************************************#

        [reach and order]
        reach_id : LINKNO
        order_id : strmOrder
        ; str_reachid : ARCID
        ; str_reachid : COMID

        [cross section method]
        parm_ivert          : 0.2
        XnPtDist            : 3
        parm_ratiothresh    : 1.5
        parm_slpthresh      : 0.03
        p_fpxnlen           : 100
        ; p_buffxnlen       : 30
        ; p_xngap           : 3

        [width from curvature via buff. method]
        use_wavelet_curvature_method : False
        i_step      : 100
        max_buff    : 30

        [paths and flags]
        mpi_path    : C:/Program Files/Microsoft MPI/Bin/mpiexec.exe
        taudem_path : C:/Program Files/TauDEM/TauDEM5Exe
        wbt_path    : D:/git_projects/FACET/WBT
        whitebox    : True
        wt_grid     : True
        taudem      : True
        huc04_dir   : D:/git_projects/sample_data

### FACET File Structure

Below is sample directory structure for FACET data. Additionally, users can download [sample data](https://drive.google.com/file/d/1lS-6UgkDmnrGUD849ySZ8h9MDiNZeFoJ/view?usp=sharing) test the FACET tool

        c:\
        └── chesapeake_bay
            ├── FACET
            ├── sample_data
            |      └── 0206
            |           ├── 0206.shp
            |           └── 0206000403
            |                   └── 0206000403_dem.tif
            └── WBT

Under `sample_data` there can be one or more folders named by HUC 4 values and within each HUC 4 folder there should be a NHD hi-resolution streams 1:24k feature layer, and one or more HUC 10 and HUC 12 folders. Inside each HUC 10 or 12 folder there should be a DEM GeoTIFF.

After successfully modifying the config file and organizing the data folder, we are ready to run the FACET code. At present, FACET is best executed using command line.

        (facet36) C:\chesapeake_bay\FACET>python main_dev.py