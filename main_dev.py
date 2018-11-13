# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 16:11:00 2016

@author: sam.lamont
"""

#import time
import glob
import timeit
import os
import fnmatch
import sys
import pandas as pd

#from functools import partial
#import multiprocessing

import funcs_v2 


        
if __name__ == '__main__':    
    
    print('\n<<< Start >>>\r\n')
    start_time_0 = timeit.default_timer()    
            
    # << PARAMETERS >>  
    str_reachid='LINKNO'
#    str_reachid='ARCID'
#    str_reachid='COMID'
    str_orderid='strmOrder'
    
    ## Cross section method:
    parm_ivert = 0.2 # 0.2 default
    XnPtDist = 3 # 3 is default  Step along Xn length for interpolating elevation
    parm_ratiothresh = 1.5 # 1.5 default
    parm_slpthresh = 0.03 # 0.03 default
#    p_buffxnlen = 30 # meters (if UTM) ?? (cross section length) Now defined in write_xns_shp
#    p_xngap = 3 # 3 default  (spacing between cross sections)
    p_fpxnlen=100 # 2D cross-section method (assign by order?)
    
    ## Width from curvature via buffering method:
    use_wavelet_curvature_method = False
    i_step = 100 # length of reach segments for measuring width from bank pixels (and others?)
    max_buff = 30 # maximum buffer length for measuring width based on pixels  
    
    ## Preprocessing paths and parameters:
    str_mpi_path=r'C:\Program Files\Microsoft MPI\Bin\mpiexec.exe'
    str_taudem_dir=r'C:\Program Files\TauDEM\TauDEM5Exe' #\D8FlowDir.exe"'
    # str_whitebox_path= r"C:\whitebox_gat\gospatial\go-spatial_win_amd64.exe" # Go version
    str_whitebox_path= r"D:\git_projects\FACET_misc\white_box_go_spatial\go-spatial_win_amd64.exe" # Go version
  
    ## Flags specifying what to run:
    run_whitebox = True  # Run Whitebox-BreachDepressions?
    run_wg = True       # Run create weight grid by finding start points from a given streamlines layer?
    run_taudem = True   # Run TauDEM functions?    

    #=============================================================================================== 
    #                             BEGIN BULK PROCESSING LOOP
    #===============================================================================================    
    
    ## << FOR BULK PROCESSING >>
    ## Specify path to root:
    lst_paths = glob.glob(r"F:\facet\CFN_CB_HUC10\*")[1]
    lst_paths = [lst_paths]
    lst_paths.sort() # for testing

    #===============================================================================================   
    #                           Chesapeake file structure:
    #===============================================================================================   
    for i, path in enumerate(lst_paths):
        str_nhdhr_huc4 = glob.glob(path + '\*.shp')[0] # F:\facet\CFN_CB_HUC10\0206\0206.shp
        
        ## Reproject the nhdhr lines to same as DEM:
        #dst_crs='+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs'      
        dst_crs="+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"

        ## Re-project the NHD to match the DEM:
        str_nhdhr_huc4_proj = funcs_v2.reproject_vector_layer(str_nhdhr_huc4, dst_crs)  # F:\facet\CFN_CB_HUC10\0205\0205_proj.shp       
#        str_nhdhr_huc4_proj = r'F:\facet\CFN_CB_HUC10\0206\0206_proj.shp'
        for root, dirs, files in os.walk(path):
            try:
                str_huc = fnmatch.filter(files, '*.shp')[0]
                str_dem = fnmatch.filter(files, '*.tif')[0]
            except:
                continue

            # HUC IDs
            """ HUC12 ids for naming files:       
                huc12 = root[27:] # assuming huc4 dir with huc10 dirs"""
            huc12 = root.split('\\')[-1:][0] # 0206000603
            
            ## Get the DEM and HUC10 poly mask file paths:
            str_dem_path = root + '\\' + str_dem # F:\facet\CFN_CB_HUC10\0206\0206000603\0206000603_dem.tif

            ## Assign a name for the clipped NHD-HR HUC10 file:
            path_to_dem, dem_filename = os.path.split(str_dem_path)
            str_nhdhr_huc10 = path_to_dem + '\\' + dem_filename[:-4]+'_nhdhires.shp'            
            
            # Project dem raster
            name, ext = str_dem.split('.')
            dst_file = os.path.join(root, f"{name}_proj.{ext}")
            str_dem_path_proj = funcs_v2.reproject_grid_layer(str_dem_path, dst_crs, dst_file, resolution=(3.0, 3.0))

            ## Clip the HUC4 nhdhr streamlines layer to the HUC10:
            funcs_v2.clip_features_using_grid(str_nhdhr_huc4_proj, str_nhdhr_huc10, str_dem_path_proj) 

            ## Call preprocessing function:
#            str_dem_path = r'F:\facet\CFN_CB_HUC10\0206\0206000603\0206000603_dem_proj.tif'
            funcs_v2.preprocess_dem(str_dem_path, str_nhdhr_huc10, dst_crs, str_mpi_path, str_taudem_dir, str_whitebox_path, run_whitebox, run_wg, run_taudem)             
            break
        break
           
    #===============================================================================================           
    ## DRB file structure:
    #===============================================================================================   
#    for i, path in enumerate(lst_paths):
#        
#        if i < 9: continue
#         
#        print('Processing:  ' + path)
#        
#        start_time_i = timeit.default_timer()
#    
#        try:
#            str_dem_path = glob.glob(os.path.join(path,'*_dem.tif'))[0]
#            str_hand_path = glob.glob(os.path.join(path,'*hand*.tif'))[0]
#            str_net_path = glob.glob(os.path.join(path,'*breach_net.shp'))[0]    
#            str_sheds_path = glob.glob(os.path.join(path,'*w_diss_physio*.shp'))[0]
#        except:
#            print('WARNING:  There is an error in the paths!')
#            pass # depending on what's being run, it might not matter if a file doesn't exist
#        
#        path_to_dem, dem_filename = os.path.split(str_dem_path)
#        csv_filename = dem_filename[:-8] + '.csv'
#        str_csv_path = os.path.join(path_to_dem, csv_filename)
#        
#        # Output layers...
#        out_path=r'E:\bulk_processing\drb_chwidpixels_2018.09.10'
#        str_chxns_path = os.path.join(out_path, dem_filename[:-8] + '_chxns.shp')
#        str_chxns_path = os.path.join(out_path, dem_filename[:-8] + '_chxns.shp')
#        str_fpxns_path = os.path.join(out_path, dem_filename[:-8] + '_fpxns.shp')
#        str_bankpts_path = os.path.join(out_path, dem_filename[:-8] + '_bankpts.shp')
#        str_bankpixels_path = os.path.join(out_path, dem_filename[:-8] + '_bankpixels.tif')
#        
#        # Call preprocessing function: 
#        dst_crs = {'init': u'epsg:26918'} # NAD83, UTM18N  
#        funcs_v2.preprocess_dem(str_dem_path, str_net_path, dst_crs, str_mpi_path, str_taudem_dir, str_whitebox_path, run_whitebox, run_wg, run_taudem)         
        
        # << GET CELL SIZE >>
#        cell_size = int(funcs_v2.get_cell_size(str_dem_path)) # range functions need int?        

        # << BUILD STREAMLINES COORDINATES >>
#        df_coords, streamlines_crs = funcs_v2.get_stream_coords_from_features(str_net_path, cell_size, str_reachid, str_orderid) # YES!        
#        df_coords.to_csv(str_csv_path)
#        df_coords = pd.read_csv(str_csv_path, )    
#        streamlines_crs = {'init': u'epsg:26918'} # NAD83, UTM18N     

#        # ============================= << CROSS SECTION ANALYSES >> =====================================
#        # << CREATE Xn SHAPEFILES >>
#        ## Channel:
#        funcs_v2.write_xns_shp(df_coords, streamlines_crs, str(str_chxns_path), False, int(3))             
#        ## Floodplain:
##        funcs_v2.write_xns_shp(df_coords, streamlines_crs, str(str_fpxns_path), True, int(30))     
#
#        # << INTERPOLATE ELEVATION ALONG Xns >>
#        df_xn_elev = funcs_v2.read_xns_shp_and_get_dem_window(str_chxns_path, str_dem_path)
#        
#        # Calculate channel metrics and write bank point shapefile...# NOTE:  Use raw DEM here??        
#        funcs_v2.chanmetrics_bankpts(df_xn_elev, str_chxns_path, str_dem_path, str_bankpts_path, parm_ivert, XnPtDist, parm_ratiothresh, parm_slpthresh)
        
        # ========================== << BANK PIXELS AND WIDTH FROM CURVATURE >> ====================================
#        funcs_v2.bankpixels_from_curvature_window(df_coords, str_dem_path, str_bankpixels_path, cell_size, use_wavelet_curvature_method) # YES!        
#
#        funcs_v2.channel_width_from_bank_pixels(df_coords, str_net_path, str_bankpixels_path, str_reachid, cell_size, i_step, max_buff)        
#       
#  
#        # ============================= << DELINEATE FIM >> =====================================
#        funcs_v2.fim_hand_poly(str_hand_path, str_sheds_path, str_reachid)
#        
#        
#        # ==================== CHANNEL WIDTH, FLOODPLAIN WIDTH, HAND ANALYSIS ALL IN ONE ===========
#        funcs_v2.channel_and_fp_width_bankpixels_segments_po_2Dfpxns(df_coords, str_net_path, str_bankpixels_path, str_reachid, cell_size, p_buffxnlen, str_hand_path, parm_ivert)    
        
        print('\nRun time for {}:  {}\r\n'.format(path, timeit.default_timer() - start_time_i))

        
    #=============================================================================================== 
    #                             BEGIN LOCAL TESTING SECTION
    #===============================================================================================    
    
#    str_fim_path=r"D:\facet\dr_working_data\dr_working_data\dr3m_thresh.tif" ## test test
#    str_dem_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18.tif"
#    str_slp_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18_breach_sd8.tif"
#    str_net_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18_breach_net.shp"
#    str_bankpixels_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_utm18_bankpixels.tif"
##    str_bankpts_path = r'D:\CFN_data\DEM_Files\020502061102_ChillisquaqueRiver\bankpts_TEST.shp'      
##    str_chxns_path = r"D:\hand\nfie\020700\usgs\020700_chxns_test.shp"
##    str_fpxns_path = r"D:\hand\nfie\020700\usgs\020700_fpxns_test.shp"
#    str_hand_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18_breach_hand.tif"
##    str_sheds_path = r"D:\drb\02040205\02040205_w_diss_physio.shp"
##    str_startptgrid_path = r'D:\CFN_data\DEM_Files\020502061102_ChillisquaqueRiver\DEMnet_UNIQUE_ID.shp'
#    
#    ## Openness: THIS NEEDS WORK -- Table this til later if you have time (July5)
##    str_pos_path = r'D:\Terrain_and_Bathymetry\USGS\CBP_analysis\DifficultRun\facet_tests\dr_pos_raw.tif'    
#    ## Flow direction: For discerning between right/left bank?
##    str_fdr_path = r"D:\Terrain_and_Bathymetry\USGS\CBP_analysis\DifficultRun\raw\dr3m_raw_dem_clip_utm18_breach_p.tif"     
#    
##    # << GET CELL SIZE >>
#    cell_size = int(funcs_v2.get_cell_size(str_dem_path)) # range functions need int?
##    
##    # << DEM PRE-PROCESSING using TauDEM and Whitebox-GoSpatial >>              
##    # (1) If necessary, clip original streamlines layer (NHD hi-res 4 digit HUC to DEM of interest)...     
##    # Build the output streamlines file name...
##    path_to_dem, dem_filename = os.path.split(str_dem_path)
##    str_output_nhdhires_path = path_to_dem + '\\' + dem_filename[:-4]+'_nhdhires.shp' 
##    funcs_v2.clip_features(str_net_in_path, str_output_nhdhires_path, str_dem_path)     
##     
###      Call preprocessing function: 
##    funcs_v2.preprocess_dem(str_dem_path, str_net_in_path, str_mpi_path, str_taudem_dir, str_whitebox_path, run_whitebox, run_wg, run_taudem)        
#     
###    # << BUILD STREAMLINES COORDINATES >>
###    # Build reach coords and get crs from a pre-existing streamline shapefile...
##    df_coords, streamlines_crs = funcs_v2.g str_fim_path=r"D:\facet\dr_working_data\dr_working_data\dr3m_thresh.tif" ## test test
#    str_dem_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18.tif"
#    str_slp_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18_breach_sd8.tif"
#    str_net_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18_breach_net.shp"
#    str_bankpixels_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_utm18_bankpixels.tif"
##    str_bankpts_path = r'D:\CFN_data\DEM_Files\020502061102_ChillisquaqueRiver\bankpts_TEST.shp'      
##    str_chxns_path = r"D:\hand\nfie\020700\usgs\020700_chxns_test.shp"
##    str_fpxns_path = r"D:\hand\nfie\020700\usgs\020700_fpxns_test.shp"
#    str_hand_path = r"D:\facet\dr_working_data\dr_working_data\dr3m_raw_dem_clip_utm18_breach_hand.tif"
##    str_sheds_path = r"D:\drb\02040205\02040205_w_diss_physio.shp"
##    str_startptgrid_path = r'D:\CFN_data\DEM_Files\020502061102_ChillisquaqueRiver\DEMnet_UNIQUE_ID.shp'
#    
#    ## Openness: THIS NEEDS WORK -- Table this til later if you have time (July5)
##    str_pos_path = r'D:\Terrain_and_Bathymetry\USGS\CBP_analysis\DifficultRun\facet_tests\dr_pos_raw.tif'    
#    ## Flow direction: For discerning between right/left bank?
##    str_fdr_path = r"D:\Terrain_and_Bathymetry\USGS\CBP_analysis\DifficultRun\raw\dr3m_raw_dem_clip_utm18_breach_p.tif"     
#    
##    # << GET CELL SIZE >>
#    cell_size = int(funcs_v2.get_cell_size(str_dem_path)) # range functions need int?
##    
##    # << DEM PRE-PROCESSING using TauDEM and Whitebox-GoSpatial >>              
##    # (1) If necessary, clip original streamlines layer (NHD hi-res 4 digit HUC to DEM of interest)...     
##    # Build the output streamlines file name...
##    path_to_dem, dem_filename = os.path.split(str_dem_path)
##    str_output_nhdhires_path = path_to_dem + '\\' + dem_filename[:-4]+'_nhdhires.shp' 
##    funcs_v2.clip_features(str_net_in_path, str_output_nhdhires_path, str_dem_path)     
##     
###      Call preprocessing function: 
##    funcs_v2.preprocess_dem(str_dem_path, str_net_in_path, str_mpi_path, str_taudem_dir, str_whitebox_path, run_whitebox, run_wg, run_taudem)        
#     
###    # << BUILD STREAMLINES COORDINATES >>
###    # Build reach coords and get crs from a pre-existing streamline shapefile...
##    df_coords, streamlines_crs = funcs_v2.get_stream_coords_from_features(str_net_path, cell_size, str_reachid, str_orderid) # YES!
##    df_coords.to_csv(r"D:\facet\dr_working_data\dr_working_data\dr3m_coords.csv") # save to a csv for testing (faster to read pre-calculated coords)
#    
##    print('NOTE:  Reading pre-calculated csv file...')
#    df_coords = pd.read_csv(r"D:\facet\dr_working_data\dr_working_data\dr3m_coords.csv")
##    df_coords = pd.read_csv('df_coords_Chillisquaque.csv', )
##    df_coords = pd.read_csv('df_coords_020802.csv', )    
##    df_coords = pd.read_csv(r"D:\hand\nfie\020700\df_coords_020700.csv", )
#    streamlines_crs = {'init': u'epsg:26918'} # NAD83, UTM18N    
#    
##   # << BANK POINTS FROM CROSS-SECTIONS >>
#    # Create Xn shapefiles:
##    # Channel:
##    funcs_v2.write_xns_shp(df_coords, streamlines_crs, str(str_xns_path), False, int(3), int(3), float(30))     
##    # FP:
##    funcs_v2.write_xns_shp(df_coords, streamlines_crs, str(str_fpxns_path), True, int(30))  # For FP width testing
##
###    # Interpolate elevation along Xns:
##    df_xn_elev = funcs_v2.read_xns_shp_and_get_dem_window(str_xns_path, str_dem_path)
##    
###    print('Writing df_xn_elev to .csv for testing...')
###    df_xn_elev.to_csv(columns=['index','linkno','elev','xn_row','xn_col']) 
###    df_xn_elev2 = pd.read_csv('df_xn_elev.csv') #, dtype={'linko':np.int,'elev':np.float,'xn_row':np.float,'xn_col':np.float})
## 
##    # Calculate channel metrics and write bank point shapefile:
##    print('Calculating channel metrics from bank points...')
##    funcs_v2.chanmetrics_bankpts(df_xn_elev, str_xns_path, str_dem_path, str_bankpts_path, parm_ivert, XnPtDist, parm_ratiothresh, parm_slpthresh)    
#  
##    # << BANK PIXELS FROM CURVATURE >>
##    funcs_v2.bankpixels_from_curvature_window(df_coords, str_dem_path, str_bankpixels_path, cell_size, use_wavelet_curvature_method)
#    
##    # Testing openness:
##    funcs_v2.bankpixels_from_openness_window(df_coords, str_pos_path, str_bankpixels_path) 
##    funcs_v2.bankpixels_from_openness_window_buffer_all(df_coords, str_dem_path, str_net_path, str_pos_path, str_neg_path) 
#
#    # << FLOOD INUNDATION MAP (FIM) FROM HAND AND A POLYGON (eg, catchments) >>
##    funcs_v2.fim_hand_poly(str_hand_path, str_sheds_path) # NOTE:  Will need to know which regression eqn to use?
#    
##     << TESTING FLOODPLAIN WIDTH METHODS >> 
##    buff_dist = 40
##    funcs_v2.floodplain_width_2D_xns(str_xns_path, str_floodplain_path, buff_dist)
##    funcs_v2.floodplain_width_fppixels_segments_po(df_coords, str_net_in_path, str_floodplain_path, str_reachid, cell_size)
##    funcs_v2.floodplain_width_reach_buffers_po(funcs, str_net_path, str_fp_path, str_reachid, cell_size)
#    
#    # << CHANNEL WIDTH, FLOODPLAIN WIDTH, HAND ANALYSIS ALL IN ONE >>
##    funcs_v2.channel_and_fp_width_bankpixels_segments_po_2Dfpxns(df_coords, str_net_path, str_bankpixels_path, str_reachid, cell_size, p_buffxnlen, str_hand_path, parm_ivert)    
#    funcs_v2.channel_et_stream_coords_from_features(str_net_path, cell_size, str_reachid, str_orderid) # YES!
##    df_coords.to_csv(r"D:\facet\dr_working_data\dr_working_data\dr3m_coords.csv") # save to a csv for testing (faster to read pre-calculated coords)
#    
##    print('NOTE:  Reading pre-calculated csv file...')
#    df_coords = pd.read_csv(r"D:\facet\dr_working_data\dr_working_data\dr3m_coords.csv")
##    df_coords = pd.read_csv('df_coords_Chillisquaque.csv', )
##    df_coords = pd.read_csv('df_coords_020802.csv', )    
##    df_coords = pd.read_csv(r"D:\hand\nfie\020700\df_coords_020700.csv", )
#    streamlines_crs = {'init': u'epsg:26918'} # NAD83, UTM18N    
#    
##   # << BANK POINTS FROM CROSS-SECTIONS >>
#    # Create Xn shapefiles:
##    # Channel:
##    funcs_v2.write_xns_shp(df_coords, streamlines_crs, str(str_xns_path), False, int(3), int(3), float(30))     
##    # FP:
##    funcs_v2.write_xns_shp(df_coords, streamlines_crs, str(str_fpxns_path), True, int(30))  # For FP width testing
##
###    # Interpolate elevation along Xns:
##    df_xn_elev = funcs_v2.read_xns_shp_and_get_dem_window(str_xns_path, str_dem_path)
##    
###    print('Writing df_xn_elev to .csv for testing...')
###    df_xn_elev.to_csv(columns=['index','linkno','elev','xn_row','xn_col']) 
###    df_xn_elev2 = pd.read_csv('df_xn_elev.csv') #, dtype={'linko':np.int,'elev':np.float,'xn_row':np.float,'xn_col':np.float})
## 
##    # Calculate channel metrics and write bank point shapefile:
##    print('Calculating channel metrics from bank points...')
##    funcs_v2.chanmetrics_bankpts(df_xn_elev, str_xns_path, str_dem_path, str_bankpts_path, parm_ivert, XnPtDist, parm_ratiothresh, parm_slpthresh)    
#  
##    # << BANK PIXELS FROM CURVATURE >>
##    funcs_v2.bankpixels_from_curvature_window(df_coords, str_dem_path, str_bankpixels_path, cell_size, use_wavelet_curvature_method)
#    
##    # Testing openness:
##    funcs_v2.bankpixels_from_openness_window(df_coords, str_pos_path, str_bankpixels_path) 
##    funcs_v2.bankpixels_from_openness_window_buffer_all(df_coords, str_dem_path, str_net_path, str_pos_path, str_neg_path) 
#
#    # << FLOOD INUNDATION MAP (FIM) FROM HAND AND A POLYGON (eg, catchments) >>
##    funcs_v2.fim_hand_poly(str_hand_path, str_sheds_path) # NOTE:  Will need to know which regression eqn to use?
#    
##     << TESTING FLOODPLAIN WIDTH METHODS >> 
##    buff_dist = 40
##    funcs_v2.floodplain_width_2D_xns(str_xns_path, str_floodplain_path, buff_dist)
##    funcs_v2.floodplain_width_fppixels_segments_po(df_coords, str_net_in_path, str_floodplain_path, str_reachid, cell_size)
##    funcs_v2.floodplain_width_reach_buffers_po(funcs, str_net_path, str_fp_path, str_reachid, cell_size)
#    
#    # << CHANNEL WIDTH, FLOODPLAIN WIDTH, HAND ANALYSIS ALL IN ONE >>
##    funcs_v2.channel_and_fp_width_bankpixels_segments_po_2Dfpxns(df_coords, str_net_path, str_bankpixels_path, str_reachid, cell_size, p_buffxnlen, str_hand_path, parm_ivert)    
##    funcs_v2.channel_and_fp_2Dxn_analysis(df_coords, str_net_path, str_bankpixels_path, str_hand_path, str_fim_path, str_reachid, cell_size, i_step, max_buff, p_fpxnlen)

    print('\n<<< End >>>\r\n')
    print('Total Run Time:  {}'.format(timeit.default_timer() - start_time_0))
    
