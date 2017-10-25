# Prerequisites
##### Anaconda
- Install "Anaconda Python 2.7" version from https://www.continuum.io/downloads
- Add conda to your PATH

##### CASA (Common Astronomy Software Applications)
- Install "CASA Release 4.7.2" from https://casa.nrao.edu/download/distro
- Add casa to your PATH
- Update path and model_path in artip/conf/casa.yml 

##### Installation test
Linux:

    $ casa       
    $ conda --version

OSX:

    $ casapy       
    $ conda --version


# Install pipeline dependencies
    $ cd artip        
	$ ./setup.sh

setup.sh will

- Setup casa-pip for installing python modules CASA from PyPI
- Create "artip" conda environment from artip/environment.yml  

##### Installation test
    $ source <rc file path>
    $ casa-pip -h
    $ source activate artip
    $ pyb --version
    
# Run ARTIP
   1. Update config files present in "conf/" directory.
   2. Specify flags from the observation logs in "conf/user_defined_flags.txt". 
      Flags follows format similar to CASA flagdata command with mode='list'. 
      
      Below are the examples for the same :
        * Flag antennas

                reason='BAD_ANTENNA' correlation='RR,LL' mode='manual' antenna='1,18' scan='1,7,2,4,6,3,5'
        * Flag Baselines
              
                reason='BAD_BASELINE' correlation='RR,LL' mode='manual' antenna='11&19' scan='1,7,2,4,6,3,5'   
        * Flag Time
                
                reason='BAD_ANTENNA_TIME' correlation='LL' mode='manual' antenna='15' scan='1' timerange='2013/01/05/06:59:49~2013/01/05/07:00:00'
                reason='BAD_BASELINE_TIME' correlation='LL' mode='manual' antenna='7&8' scan='4' timerange='2013/01/05/06:59:49~2013/01/05/07:00:00'
    
   3. Run pipeline through command line
    
    pyb run -P dataset="<ms_dataset_path>" -P conf="<conf_dir_path>"
    $ cd <artip_path>
    $ pyb run -P dataset="~/Downloads/may14.ms" -P conf="conf"
    
# Generate flagging charts 
Flags are recorded only when pipeline is run with "flag_summary: true" in conf/pipeline.yml

To generate charts :
    
    $ cd flagged_data_summary
    $ python generate_graph.py "../output/<ms_dataset_name>"  
    
Charts can be accessed on http://localhost:8000/chart.html