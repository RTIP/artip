Download Anaconda Python Distribution Python 2.7 version. Casa-python module works only with python 2.7
Refer https://www.continuum.io/downloads
After the download is complete, run the following command to install python packages required to import CASA in python.

>> conda install -c pkgw qt4dbus
>> conda install -c pkgw casa-data casa-python

Install pybuilder
>> pip install pybuilder

After the successful installation of packages, run the following command from within the artip directory to build the application.
>> pyb

If you get 'ImportError: No module named casac', check your pip/pyb installation, it should point to the new anaconda python installation.
If not, uninstall the existing ones, and reinstall pip/pyb normally, and it should automatically pick the new anaconda python installation.

Now, to run tests and build,
Copy datasets in the src/integrationtest/seed_data/ required for testing
Then execute
>> pyb

And to run the application, execute
>> pyb run -P dataset="<ms_dataset_path>"
    e.g. pyb run -P dataset="~/Downloads/may14.ms"
    #Do not forget to put the quotes on the property value

To build the Distributable package
>> $ pyb
>> This will build a distributable package inside "target/dist/artip-version.dev0/dist" 
>> directory 

----------------------------------------------------------------------------------------------
For supporting RFlag/TFcrop configs we are loading Rflag and Tfcrop configs inside casa, this requires
pyaml pip module to be installed in CASA.

-------------------------------------
Imstalling pip modules in CASA
-------------------------------------
1. $ curl -O https://raw.githubusercontent.com/radio-tools/casa-python/master/setup_casapy_pip.py
2. $ python setup_casapy_pip.py
3. You should then add $HOME/.casa/bin/ to your path.
4. $ casa-pip install pyaml
---------------------------------------------------------------------------------------------