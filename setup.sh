#!/usr/bin/env bash
# install casa-pip, this will add casa-pip to the PATH variable
python setup_casapy_pip.py

# source your current shell '<rc file>' to make casa-pip available
if [[ $SHELL == '/bin/zsh' ]]; then
  source ~/.zshrc
elif [[ $SHELL == '/bin/sh' ]]; then
  source ~/.bash_profile
else
  echo "Supported shell are 'zsh' and 'bash'. Please add '~/.casa/bin' to your PATH"
fi

casa-pip install pyaml