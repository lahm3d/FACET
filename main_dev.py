# -*- coding: utf-8 -*-
"""
Author:             Sam Lamont, Labeeb Ahmed
Created:            6/7/2019
License:            Creative Commons Attribution 4.0 International (CC BY 4.0)
                    http://creativecommons.org/licenses/by/4.0/
Python version:     Tested on Python 3.6x (x64)


PURPOSE
------------------------------------------------------------------------------
[Floodplain and Channel Evaluation Toolkit]

FACET is a standalone Python tool that uses open source modules to map the
floodplain extent and compute stream channel and floodplain geomorphic metrics
such as channel width, streambank height, active floodplain width,
and stream slope from DEMs.


U.S. GEOLOGICAL SURVEY DISCLAIMER
------------------------------------------------------------------------------
This software has been approved for release by the U.S. Geological Survey
(USGS). Although the software has been subjected to rigorous review, the
USGS reserves the right to update the software as needed pursuant to further
analysis and review. No warranty, expressed or implied, is made by the USGS
or the U.S. Government as to the functionality of the software and related
material nor shall the fact of release constitute any such warranty.
Furthermore, the software is released on condition that neither the USGS nor
the U.S. Government shall be held liable for any damages resulting from its
authorized or unauthorized use.

Any use of trade, product or firm names is for descriptive purposes only and
does not imply endorsement by the U.S. Geological Survey.
------------------------------------------------------------------------------


NOTES
------------------------------------------------------------------------------
"""

from pathlib import Path
import configparser
import funcs_v2
import glob
import logging
import os
import pandas as pd
import sys
import time

import config
import funcs_v2

def initialize_logger(log_file):
    logger = logging.getLogger('logger_loader')
    logging.basicConfig(filename=log_file, filemode='w')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(lineno)d] - %(message)s', '%m/%d/%Y %I:%M:%S %p')
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def clear_out_logger(logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)

if __name__ == '__main__':
    
    print('\n<<< Start >>>\r\n')

    # read in config file
    config_file = config.get_config_path()
    Config = configparser.ConfigParser()
    Config.read(config_file)

    # << PARAMETERS >>  
    str_reachid = Config['reach and order']['reach_id']
    str_orderid = Config['reach and order']['order_id']

    # Cross section method:
    parm_ivert = float(Config['cross section method']['parm_ivert'])  # 0.2 default
    XnPtDist = int(
        Config['cross section method']['XnPtDist'])  # 3 is default  Step along Xn length for interpolating elevation
    parm_ratiothresh = float(Config['cross section method']['parm_ratiothresh'])  # 1.5 default
    parm_slpthresh = float(Config['cross section method']['parm_slpthresh'])  # 0.03 default
    p_fpxnlen = int(Config['cross section method']['p_fpxnlen'])  # 2D cross-section method (assign by order?)
    # p_buffxnlen    = Config['cross section method']['p_buffxnlen']  # meters Hardcoded in: get_xn_length_by_order()
    p_xngap = int(Config['cross section method']['p_xngap'])  # 3 default  (spacing between cross sections)

    # Width from curvature via buffering method:
    use_wavelet_curvature_method = Config['width from curvature via buff. method']['use_wavelet_curvature_method']
    i_step = int(Config['width from curvature via buff. method'][
                     'i_step'])  # length of reach segments for measuring width from bank pixels (and others?)
    max_buff = int(Config['width from curvature via buff. method'][
                       'max_buff'])  # maximum buffer length for measuring width based on pixels

    # Preprocessing paths and Flags specifying what to run:
    inputProc = Config['paths and flags']['taudem cores']  # str(2) # number of cores to use for TauDEM processes
    str_mpi_path = Config['paths and flags']['mpi_path']
    str_taudem_dir = Config['paths and flags']['taudem_path']
    run_wg = Config['paths and flags'][
        'wt_grid']  # Run create weight grid by finding start points from a given streamlines layer?
    run_taudem = Config['paths and flags']['taudem']  # Run TauDEM functions?
    physio = Config['paths and flags']['physio']
    census_roads = Config['paths and flags']['census roads']
    census_rails = Config['paths and flags']['census rails']
    gs_path = Config['paths and flags']['go-spatial']

    # define breach method
    rd_strm_breach_wbt = funcs_v2.str2bool(Config['breach options']['rd strm + wbt breach mtd'])
    rd_strm_breach_gs = funcs_v2.str2bool(Config['breach options']['rd strm + go-spatial mtd'])
    breach_gs = funcs_v2.str2bool(Config['breach options']['go-spatial mtd'])
    breach_wbt = funcs_v2.str2bool(Config['breach options']['default wbt breach mtd'])

    # test to see at least one breach method is defined
    mtd_sums = [rd_strm_breach_wbt, rd_strm_breach_gs, breach_wbt]
    print(mtd_sums)
    mtd_sum = sum(map(int, mtd_sums))
    if mtd_sum is 1:
        pass
    else:
        print('None or multiple breach methods defined! Please review config file and try again')
        sys.exit(0)

    # sys.exit(0)
    # CRS:
    spatial_ref = Config['spatial ref']['crs']

    # list of Hucs to exclude from FACET runs
    skip_list = Config['exclude HUCs']['skip_list'].split(',')
    skip_str = ','.join(skip_list)

    # logfile path
    log_file = Config['logging']['log_file']

    # logging
    logger = initialize_logger(log_file)
    logger.info(f'Following HUCs will be skipped based on exclusion list: {skip_str}')

    # ===============================================================================================
    #                             BEGIN BULK PROCESSING LOOP
    # ===============================================================================================

    # << FOR BULK PROCESSING >>
    # Specify path to root:
    data_dir = Config['paths and flags']['data_dir']
    lst_paths = glob.glob(f"{data_dir}\\*")
    lst_paths.sort()  # for testing
    # ===============================================================================================
    #                           Chesapeake file structure:
    # ===============================================================================================
    for i, path in enumerate(lst_paths):
        path = Path(path)  # convert to Windows path
        str_nhdhr_huc4 = path / f'{path.stem}.shp'  # Z:\facet\CFN_CB_HUC10\0206\0206.shp

        if str_nhdhr_huc4.is_file():
            logger.info(f'HUC4 shp does exist!: {str_nhdhr_huc4}')
            pass
        else:
            logger.info(f'HUC4 shp DOES NOT exist!: {str_nhdhr_huc4}')
            break

        # Re-project the NHD to match the DEM:
        str_nhdhr_huc4_proj = funcs_v2.reproject_vector_layer(path, str_nhdhr_huc4,
                                                              spatial_ref)  # Z:\facet\CFN_CB_HUC10\0205\0205_proj.shp

        for root, dirs, files in os.walk(path):
            for huc_dir in dirs:
                start_time_i = time.clock()

                hucID = huc_dir  # HUC 10 or 12 ID
                root = Path(root)  # HUC4 directory
                huc_dir = root / hucID

                print(huc_dir, hucID)

                str_dem = huc_dir / f'{hucID}_dem.tif'
                if str_dem.is_file():
                    logger.info(f'raw DEM exists: {str_dem}')
                else:
                    logger.warning(f'raw DEM DOES NOT exists: {str_dem}')
                    continue

                if hucID in skip_list:
                    continue

                # construct file paths
                str_dem_path = str_dem
                str_nhdhr_huc10 = huc_dir / f'{hucID}_dem_nhdhires.shp'
                str_dem_proj = huc_dir / f'{hucID}_dem_proj.tif'
                str_breached_dem_path = huc_dir / f'{hucID}_breach.tif'

                # Project dem raster
                str_dem_path_proj = funcs_v2.reproject_grid_layer(str_dem_path, spatial_ref, str_dem_proj,
                                                                  resolution=(3.0, 3.0))

                # Clip the HUC4 nhdhr streamlines layer to the HUC10:
                funcs_v2.clip_features_using_grid(str_nhdhr_huc4_proj, str_nhdhr_huc10, str_dem_path_proj, spatial_ref,
                                                  logger)

                # Call preprocessing function:
                if rd_strm_breach_wbt:
                    dem_merge = funcs_v2.cond_dem_for_road_x_stream_crossings(huc_dir, hucID, str_dem_proj,
                                                                              str_nhdhr_huc10, census_roads,
                                                                              census_rails)
                    funcs_v2.breach_dem(dem_merge, str_breached_dem_path)

                elif rd_strm_breach_gs:
                    dem_merge = funcs_v2.cond_dem_for_road_x_stream_crossings(huc_dir, hucID, str_dem_proj,
                                                                              str_nhdhr_huc10, census_roads,
                                                                              census_rails)
                    funcs_v2.breach_using_gs_wbt_method(huc_dir, str_dem_proj, gs_path, str_breached_dem_path,
                                                        spatial_ref)

                elif breach_gs:
                    funcs_v2.breach_using_gs_wbt_method(huc_dir, str_dem_proj, gs_path, str_breached_dem_path,
                                                        spatial_ref)

                elif breach_wbt:
                    # default breach
                    funcs_v2.breach_dem(str_dem_proj, str_breached_dem_path)

                # additional preprocessing steps
                funcs_v2.preprocess_dem(huc_dir, str_nhdhr_huc10, spatial_ref,
                                        str_mpi_path, str_taudem_dir,
                                        run_wg, run_taudem, physio,
                                        hucID, str_breached_dem_path, inputProc)

                # start of post-processing steps(???)
                str_dem_path = huc_dir / f'{hucID}_dem_proj.tif'
                str_hand_path = huc_dir / f'{hucID}_breach_hand.tif'
                str_net_path = huc_dir / f'{hucID}_breach_net.shp'
                str_raster_net_path = huc_dir / f'{hucID}_breach_net.tif'
                str_sheds_path = huc_dir / f'{hucID}_breach_w_diss_physio.shp'
                # output paths
                str_csv_path = huc_dir / f'{hucID}.csv'
                str_chxns_path = huc_dir / f'{hucID}_breach_chxns.shp'
                str_bankpts_path = huc_dir / f'{hucID}_breach_bankpts.shp'
                str_chanmet_segs = huc_dir / f'{hucID}_breach_net_ch_width.shp'
                str_bankpixels_path = huc_dir / f'{hucID}_breach_bankpixels.tif'
                str_fpxns_path = huc_dir / f'{hucID}_breach_fpxns.shp'
                str_fim_path = huc_dir / f'{hucID}_breach_hand_3sqkm_fim.tif'
                str_fim_csv = huc_dir / f'{hucID}_breach_hand_3sqkm_fim_h.csv'
                str_comp_path = huc_dir / f'{hucID}_breach_comp.tif'

                # Convert vector streamlines to raster with pixel streamline values matching linkno:
                funcs_v2.rasterize_gdf(str_net_path, str_hand_path, str_raster_net_path, None, None)

                # << GET CELL SIZE >>
                cell_size = int(funcs_v2.get_cell_size(str_dem_path))  # range functions need int?

                # << BUILD STREAMLINES COORDINATES >>
                logger.info('Generating the stream network coordinates from the csv file...')
                df_coords, streamlines_crs = funcs_v2.get_stream_coords_from_features(str_net_path, cell_size,
                                                                                      str_reachid, str_orderid,
                                                                                      logger)  # YES!
                df_coords.to_csv(str_csv_path)
                logger.info('Reading the stream network coordinates from the csv file...')
                df_coords = pd.read_csv(str_csv_path, )

                # ============================= << CROSS SECTION ANALYSES >> =====================================
                # << CREATE Xn SHAPEFILES >>
                # Channel:
                funcs_v2.write_xns_shp(df_coords, streamlines_crs, str_chxns_path, False, p_xngap, logger)
                # Floodplain:
                funcs_v2.write_xns_shp(df_coords, streamlines_crs, str_fpxns_path, True, int(30), logger)

                # << INTERPOLATE ELEVATION ALONG Xns >>
                df_xn_elev = funcs_v2.read_xns_shp_and_get_dem_window(str_chxns_path, str_dem_path, logger)

                # Calculate channel metrics and write bank point shapefile...# NOTE:  Use raw DEM here??        
                funcs_v2.chanmetrics_bankpts(df_xn_elev, str_chxns_path, str_dem_path,
                                             str_bankpts_path, parm_ivert, XnPtDist,
                                             parm_ratiothresh, parm_slpthresh, logger)

                # ========================== << BANK PIXELS AND WIDTH FROM CURVATURE >> ==========================
                funcs_v2.bankpixels_from_curvature_window(df_coords, str_dem_path, str_bankpixels_path,
                                                          cell_size, use_wavelet_curvature_method,
                                                          logger)

                funcs_v2.channel_width_from_bank_pixels(df_coords, str_net_path, str_bankpixels_path,
                                                        str_reachid, i_step, max_buff,
                                                        str_chanmet_segs, logger)

                # ============================= << DELINEATE FIM >> =====================================
                funcs_v2.fim_hand_poly(str_hand_path, str_sheds_path, str_reachid,
                                       str_fim_path, str_fim_csv, logger)

                # ============================ << FLOODPLAIN METRICS >> =====================================
                # 1D approach:
                funcs_v2.read_fp_xns_shp_and_get_1D_fp_metrics(str_fpxns_path, str_fim_path, str_dem_path, logger)

                # 2D approach:
                funcs_v2.fp_metrics_chsegs(str_fim_path, 'ch_wid_tot', str_chanmet_segs, logger)

                # ==================== << HAND CHARACTERISTICS >> ====================================
                """ 
                Calculate channel and FP metrics through analysis of the HAND grid, separating the 
                in-channel pixels from the FP pixels.
                """
                funcs_v2.hand_analysis_chsegs(str_hand_path, str_chanmet_segs, str_raster_net_path, str_fim_path,
                                              str_dem_path, logger)

                end_time = time.clock() - start_time_i
                logger.info(f'\nRun time for {hucID}:  {end_time}\r\n')
