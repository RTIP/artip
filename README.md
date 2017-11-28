## Introduction

Automated Radio Telescope Image Processing Pipeline (ARTIP) is an end to end pipeline automating the entire process of flagging, calibration and imaging.

ARTIP starts with raw data i.e. Measurement Set and goes through multiple stages like Flux Calibration, Bandpass Calibration, Phase Calibration and Imaging to generate continuum and spectral line images. Each stage can also be run independently. 

It is written using standard python libraries and the CASA package and tested against datasets (~ 6 to 30GB) produced by Giant Metrewave Radio Telescope, Pune (GMRT) , Very Large Array, NM (VLA) , Westerbork Synthesis Radio Telescope Netherlands (WSRT). Its currently being tested for the data from MeerKAT Absorption Line Survey (MALS)

Pipeline also provides ability to generate reports of processed data in graphical format.


### Obtaining ARTIP
ARTIP releases are present at https://github.com/TWARTIP/artip/releases. Download and unzip the artip package to run the pipeline.
 ```markdown
 $ unzip artip.zip -d artip
 ```
### Prerequisites
1. Install Anaconda and CASA

    * Anaconda
        * Install "Anaconda Python 2.7" version from https://www.continuum.io/downloads
        * Add conda to your PATH

    * CASA (Common Astronomy Software Applications)
        * Install "CASA Release 4.7.2" from https://casa.nrao.edu/download/distro
        * Add casa to your PATH
        * Update path and model_path in <conf_dir_path>/casa.yml

     1.1. Installation test
    ```markdown
        Linux:
            $ casa       
            $ conda --version
        OSX:
            $ casapy       
            $ conda --version
    ```     
2. Install pipeline dependencies
   ```markdown
    $ cd artip
    $ ./setup.sh
   ```
    setup.sh will
    
      * Setup casa-pip for installing python modules CASA from PyPI
      * Create "artip" conda environment from artip/environment.yml  
    
    2.1. Installation test            
      ```markdown
        $ source <rc_file_path>
        $ casa-pip -h
        $ source activate artip
        $ pyb --version
      ```
### Documentation
https://github.com/TWARTIP/artipdoc/blob/master/artip_documentation.pdf

### Running Pipeline
1. Default conf directory is present at <artip_path>/conf. You can either update it or create your own conf directory having same format.
2. Specify flags from the observation logs in "<conf_dir_path>/user_defined_flags.txt".
    Flags follow format similar to [CASA flagdata](https://casa.nrao.edu/docs/taskref/flagdata-task.html) command with mode='list'.
   
   Below are the examples for the same :
      
        * Flag antennas
                reason='BAD_ANTENNA' correlation='RR,LL' mode='manual' antenna='1,18' scan='1,7,2,4,6,3,5'
        * Flag Baselines
                reason='BAD_BASELINE' correlation='RR,LL' mode='manual' antenna='11&19' scan='1,7,2,4,6,3,5'   
        * Flag Time
                reason='BAD_ANTENNA_TIME' correlation='LL' mode='manual' antenna='15' scan='1' timerange='2013/01/05/06:59:49~2013/01/05/07:00:00'
                reason='BAD_BASELINE_TIME' correlation='LL' mode='manual' antenna='7&8' scan='4' timerange='2013/01/05/06:59:49~2013/01/05/07:00:00'
    
3. Run pipeline through command line but make sure casa_path is set properly in <conf_dir_path>/casa.yml    
```markdown    
    $ cd <artip_path>
    $ pyb run -P dataset="<ms_dataset_path>" -P conf="<conf_dir_path>" -P output="<output_dir>"
```   

### Pipeline Output
All the output artifacts like caltables, flag files, continuum and spectral line images are persisted in <output_path>/<ms_dataset_name> directory.

### Plotting Flagging Graphs
Pipeline records antenna wise flags summary at different stages. After pipeline completion, user can generate flag summary plots using below scripts :
```markdown
    $ cd <artip_path>/flagged_data_summary
    $ python generate_graph.py "<output_path>/<ms_dataset_name>"  
```
**NOTE : Flags summary is recorded only when pipeline is run with "flag_summary: true" in <conf_dir_path>/pipeline.yml**

Charts can be accessed at http://localhost:8000/chart.html
