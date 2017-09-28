#!/usr/bin/env bash
CONDA_ENV_NAME='artip'

# source your current shell '<rc file>' to make casa-pip available
function reload_env_paths(){
	if [ $SHELL == '/bin/zsh' ]; then
        source ~/.zshrc
    elif [ $SHELL == '/bin/bash' ]; then
        source ~/.bashrc
    else
        echo "Supported shell are 'zsh' and 'bash'. Please add '~/.casa/bin' to your PATH"
    fi
}

printf "####################### installing casa-pip ##########################\n"

reload_env_paths

# install casa-pip, this will add casa-pip to the PATH variable
if [ ! -x "$(command -v casa-pip)" ]; then
    echo "Setting up casap-pip"
    python setup_casapy_pip.py
    reload_env_paths
else
    echo "casa-pip already installed"
fi

casa-pip install pyaml

printf "####################### casa-pip installed ###########################\n\n"

printf "####################### Installing pipeline dependencies from environment.yml ###########################\n"
if [ -x "$(command -v conda)" ]; then
    environment_lists=($(conda env list | cut -d ' ' -f1))
    if [[ " ${environment_lists[*]} " == *" $CONDA_ENV_NAME "* ]]; then
        printf "****************** Updating conda environment = $CONDA_ENV_NAME ********************\n\n"
        conda env update -f environment.yml
        source activate $CONDA_ENV_NAME
    else
        printf "****************** Creating conda environment = $CONDA_ENV_NAME ********************\n\n"
        conda env create -f environment.yml
        source activate $CONDA_ENV_NAME
    fi
else
    echo "Please Install anaconda python version 2.7 (https://www.anaconda.com/download) "
fi
printf "####################### Installed pipeline dependencies ###########################\n\n"