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

FACET neeeds following programs before getting started:
 
 * Anaconda (Python 3.6)
 * WhiteboxTools (*not Whitebox GAT*)
 * TauDEM  (*including its dependencies*)

## 1. Installation guide:
 * [Download and install Anaconda](https://docs.anaconda.com/anaconda/install/). It is recommended that you follow the instructions in the guide. Alternatively, you can also install Miniconda to save space
 * [Download and install TauDEM](http://hydrology.usu.edu/taudem/taudem5/downloads.html)
 * [Download and install Git](https://gitforwindows.org/) (*Downloading git is optional*) 

## 2. Set-up:

Determine where the FACET is going to reside on your computer and navigate to that path. In this tutorial, we are going to set up FACET
under `c:\chesapeake_bay` (***needs to be manually created by the user***)

Simpler method: FACET can be downloaded directly from GitHub [here](https://github.com/lahm3d/FACET/archive/develop.zip) (***make sure to select develop branch***), unzip and place it under `c:\cheaspeake_bay` folder


For contributors and those who have git installed:

1. Open 'git bash' window from your Windows Start button and navigate to `C:\chesapeake_bay` 
    
        cd c:\chesapeake_bay

2. Now download FACET code:
   
        git clone https://github.com/lahm3d/FACET.git

3. Navigate to FACET folder and check out the latest branch `develop`

        cd FACET/
        git checkout develop

You've successfully download FACET code and switched to latest branch

### Setting up Whitebox Tools

[Install WhiteboxTools](https://www.uoguelph.ca/~hydrogeo/WhiteboxTools/download.html) and [user manual](https://jblindsay.github.io/wbt_book/intro.html). At the time of writing, FACET was tested with WBT 0.12.0 but newer versions should be safe to use so please download the latest version. *Note: FACET uses WhiteboxTools (WBT), not Whitebox Geospatial Analysis Tools (GAT)* 

Unzip `WhiteboxTools_win_amd64.zip` and extract the `WBT` folder under `c:\cheaspeake_bay`

The file structure should look something like this:
       
        c:\
        └── chesapeake_bay
            ├── FACET
            └── WBT

### Setting up Anaconda and running FACET

Before we can execute FACET, we need to set up an environment on Anaconda so from Window's Start button find and launch 'Anaconda Prompt'. Next navigate to `c:\chesapeake_bay\FACET` folder

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

Now we can execute FACET code. Currently only command line execution is supported and following command line executes FACET code

        (facet36) C:\chesapeake_bay\FACET>python main_dev.py