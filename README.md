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

# (05/20/2019): Update on Breach algorithms

Originally, FACET used [GoSpatial](https://github.com/jblindsay/go-spatial) command line interface utility derived from [Whitebox GAT](https://www.uoguelph.ca/~hydrogeo/Whitebox/index.html) for breaching DEMs. As we transitioned from WB GAT to GoSpatial and finally to WBT, we realized that the breaching algorithms were slightly different in each version of Whitebox. The three breach methods are comprehensive (WB GAT), constrained (WB GAT and GoSpatial) and fast breach (WB GAT, GoSpatial and WBT) (insert John Lindsay paper citation). We are limited to constrained and fast breach algorithms because of their performance, relative accuracy compared to comprehensive breach method and easy command line interface. Additionally, we've developed some methods that condition the DEM and improves breaching results. Currently, FACET uses four different methods of breaching:

1. [Fast breach using Whitebox Tools](https://jblindsay.github.io/wbt_book/available_tools/hydrological_analysis.html?highlight=Breach#breachdepressions)
2. [Constrained breach using GoSpatial.exe](https://github.com/jblindsay/go-spatial/blob/master/tools/breachDepressions.go) and [related publication](https://www.uoguelph.ca/~hydrogeo/pubs/2016_Lindsay_HP.pdf)

Fast and constrained breach methods failed to successfully breach roads and generated pseudo streams that run parallel to roads. We addressed this by running a 150m by 150m filter local minimum filter on the DEM, identified road (Census all roads, 2018) and stream (NHD high-res. streams) cross-sections polygons, and extracted minimum DEM values using the cross-section polygons. Then we merged these cross-sections into our base DEM and ran the breach tool. This resulted in successful breaching of roads (TODO: follow up with detailed comparisons of breach comparisons...)

3. Perform minimum road-stream cross-section conditioning on DEM and then run fast breach using Whitebox Tools
4. Perform minimum road-stream cross-section conditioning on DEM and then run constrained breach using GoSpatial.exe

(For now...) The default option is going to be #3 because it relies on Census road network to successfully address breaching issues encountered in fast breach, with good performance and accuracy (need to do further testing  to validate accuracy) and it is part Whitebox Tools, an active project with several contributors and a significant presence in hydrology and geospatial community. Whereas, GoSpatial is a project that is being mantained for archival purposes, so long term development and support is not possible. 

# Setting up FACET (***Work in progress***)

## How-to:
 1. Download all the applications and files listed under **Requirements**
 2. Follow installation guides
 3. Follow FACET, Anaconda and Whitebox set-up instructions
 4. Set-up data structure, edit config file, and run FACET

## Requirements:
 
 * Anaconda3 (Conda env file is provided which installs correct version of Python and dependencies) 
 * Whitebox Tools (*not Whitebox GAT*) 
 * TauDEM  (*including dependencies*)
 * Download FACET Ancillary Data [here](https://www.sciencebase.gov/catalog/item/5cddaefee4b02927374637a9). The page has various FACET ancillary datasets for Chesapeake Bay Watershed:
   * Physiographic Regions (*required*)
   * Stream network shapefile of study area, such as NHD High Resolution (*required*)
   * One or more digital elevation model(s) (DEM) of study area as a GeoTIFF with at least 3.0 meter resolution(*required*) 
   * [Sample data](https://drive.google.com/open?id=1SOdRf8zumgHHAVa3yRz6GQoHL4r4OZ7F) (*optional*)
* GoSpatial executable: only required if using constratined breach algorithm based on Whitebox GAT, otherwise optional.

## 1. Installation guide:
 * [Download and install Anaconda](https://docs.anaconda.com/anaconda/install/). It is recommended that you follow the instructions in the guide. Alternatively, you can also install Miniconda to save space
 * [Download and install TauDEM](http://hydrology.usu.edu/taudem/taudem5/downloads.html)
 * [Download and install Git](https://gitforwindows.org/) (*Downloading git is optional, but highly recommended for accessing latest changes*)

## 2. Set-up:

First, identify where you are going to store FACET code and the data. In this tutorial, the code and data will be saved under `c:\chesapeake_bay` 

**How to get FACET code?** 

1. The easy way: [Download FACET from GitHub](https://github.com/lahm3d/FACET/archive/develop.zip) and extract it under `c:\cheaspeake_bay` folder
2. Get FACET from git (see instructions below)


For contributors and those who have git installed:

1. Open 'git bash' window from your Windows Start button and navigate to the folder where you would like to add FACET by typing ‘cd’ followed by the path e.g.
    
        cd c:\chesapeake_bay

2. Now download FACET code by typing:
   
        git clone https://github.com/lahm3d/FACET.git

3. Navigate to FACET folder and check out the latest branch `develop`. *Currently, latest code resides on **develop** branch and will be merged back to master after it is stable*

        cd FACET/
        git checkout develop

You've successfully download FACET code and switched to latest branch

## 3. Anaconda and Whitebox Tools

[WhiteboxTools](https://www.uoguelph.ca/~hydrogeo/software.shtml#wgat) (WBT) is a standalone open source swiss army knife of geospatial tools supported by Dr. John Lindsay at University of Guelph, Canada. And FACET relies on WBT's algorithms for hydrological conditioning DEMs as part of pre-processing step. 

### Downloading GoSpatial for alternative breach algorithm:

Download and extract the zip file, and remember the path to `go-spatial_win_*.exe` from [here](https://www.uoguelph.ca/~hydrogeo/software.shtml). The download link is under 'legacy software' 

### Setting up Anaconda

Open Window's Start button, type 'Anaconda Prompt' and launch the prompt. Next type in the following cmd line to navigate to `c:\chesapeake_bay\FACET` folder

        cd c:\chesapeake_bay\FACET

Now we are going to create an unique environment for FACET, copy and paste the following command:

        conda env create -f c:\chesapeake_bay\FACET\facet36_2019.05.17.yml

This creates a new environment called `facet36` and all the relevant packages needed. Next step is to activate the environment and run FACET

After launching Anaconda prompt the window displays:

        (base) C:\chesapeake_bay\FACET>

"base" is the base environment that is currently active, we want to switch from **base** to **facet36**. To activate the new environment:

        activate facet36

Now the prompt should display: 

        (facet36) C:\chesapeake_bay\FACET>

This means you've successfully activated FACET environment and this is where you will be running FACET.

## 4. Configuration file and data structure

### FACET File Structure

Below is sample directory structure for FACET data that outlines where files should go. The users should aim to structure their project directories accordingly. Also, we've provided [sample data](##Requirements) so users can download and quickly test the tool.

        c:\
        └── chesapeake_bay
            ├── facet_ancillary_data 
            |       ├── census_roads_2018_mid_atl.shp
            |       ├── census_rails_2018_mid_atl.shp
            |       ├── CFN_HUC10_prj.shp
            |       ├── HUC10_CBW.shp
            |       └── Physio_prj.shp
            ├── FACET
            ├── go-spatial
            |     └── go-spatial_win_amd64.exe
            └── sample_data 
                  └── 0206
                       ├── 0206.shp
                       └── 0206000403
                               └── 0206000403_dem.tif


Under `sample_data` there can be one or more folders named by HUC 4 values and within each HUC 4 folder there should be a NHD high-resolution streams 1:24k feature layer, and one or more HUC 10 and HUC 12 folders. Inside each HUC 10 or 12 folder there should be a DEM GeoTIFF.

### Configuration file

FACET uses `.INI` configuration file (see `config.ini`) to define paths, toggle features etc., This config file can be opened in any text editor. We recommend creating a copy of the original file and renaming it as `config_orig.ini`, so you have an original back up. Now users are free to make edits to the `config.ini` (Note: FACET will always search for a file name `config.ini` so make sure all your changes are reflected in this specific file).

It is recommended that users **ONLY** modify the following sections: `logging`, `paths and flags`, `breach options`, , `exclude HUCs` and `spatial ref`, and leaving all other values as defaults. In future, guidance and additional documentation will be provided on how to set or configure other parameters. 

Here is an example of config file. Please not `.INI` syntax instructions are provided in the file as well, and carefully read the next section on how to edit configuration file.

        #*****************************************************************#
        # Module Name: config.ini                                         #
        # Type       : FACET configuration file                           #
        # Function   : Define the configuration of a FACET run            #
        # for comments use ; or # and no in-line comments                 #
        # values can be assigned using = or :                             #
        # for paths use / -- DO NOT use \ or \\                           #
        #*****************************************************************#

        [logging]
        log_file: C:/.../sample_data.log

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
        p_xngap           : 3

        [width from curvature via buff. method]
        use_wavelet_curvature_method : False
        i_step      : 100
        max_buff    : 30

        [paths and flags]
        taudem              : True
        mpi_path            : C:/Program Files/Microsoft MPI/Bin/mpiexec.exe
        taudem_path         : C:/Program Files/TauDEM/TauDEM5Exe
        taudem cores        : 2
        go-spatial          : C:/.../go-spatial_win_amd64.exe
        wt_grid             : True
        data_dir            : C:/.../sample_data
        physio              : C:/.../Physio_prj.shp
        census roads        : C:/.../census_roads_2018_mid_atl.shp
        census rails        : C:/.../census_rails_2018_mid_atl.shp

        [breach options]
        # see README for detailed explanation. Pick ONLY ONE!
        rd strm + wbt breach mtd  : False
        rd strm + go-spatial mtd  : False
        go-spatial mtd            : False
        default wbt breach mtd    : True

        [exclude HUCs]
        skip_list : 0206000501,0206000502,0208010306,0208010609,0206000403

        [spatial ref]
        crs : +proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs

### How-to fill out congfig parameters:

* `log_file`: directory and file name for log file. For each run log files are overwritten, so manually save them if needed
* `mpi_path` and `taudem_path`:  users will need to manually find and confirm that `mpiexec.exe` (file) and `TauDEM5Exe` (folder) exist. They are usually located under following folders:
  * `C:/Program Files/Microsoft_MPI/...`
  * `C:/Program Files/TauDEM/...`
* `taudem cores`: number of cores TauDEM can use to process. The default is 2, but can be changed based on your CPU
* `go-spatial`: complete path of `go-spatial_win_amd64.exe`

* `data_dir`:  complete data path e.g. `C:/.../sample_data`. The structure should follow what's listed below (see **FACET File Structure**)
* `physio`: [download physiographic regions shapefile, unzip and provide complete path](##Requirements), unzip and link the path here for the physiographic shapefile 
* `census roads`: [download Census All Roads (2018) shapefile, unzip and provide complete path](##Requirements), unzip and link the path here for the physiographic shapefile 
* `census rails`: [download Census All Rails (2018) shapefile, unzip and provide complete path](##Requirements), unzip and link the path here for the physiographic shapefile 

After successfully modifying the config file and organizing the data folder, we are ready to run the FACET code. At present, FACET is best executed using command line.

        (facet36) C:\chesapeake_bay\FACET>python main_dev.py