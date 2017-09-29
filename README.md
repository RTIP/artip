# Prerequisites
##### Anaconda
- Install "Anaconda Python 2.7" version from https://www.continuum.io/downloads
- Add conda to your PATH

##### CASA (Common Astronomy Software Applications)
- Install "CASA Release 4.7.2" from https://casa.nrao.edu/download/distro
- Add casa to your PATH
- Update path and model_path in conf/casa.yml 


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
-  Setup casa-pip for installing python modules CASA from PyPI
-  "artip" conda environment from artip/environment.yml  

##### Installation test
    $ source <rc file path>
    $ casa-pip -h
    $ source activate artip
    $ pyb --version
    
# Run ARTIP
   pyb run -P dataset="<ms_dataset_path>" conf="<conf_dir_path>"
    
    $ pyb run -P dataset="~/Downloads/may14.ms" -P conf="conf"