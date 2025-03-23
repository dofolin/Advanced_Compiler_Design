#!/bin/bash

#install deno

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    curl -fsSL https://deno.land/x/install/install.sh | sh
elif [[ "$OSTYPE" == "darwin"* ]]; then
    curl -fsSL https://deno.land/x/install/install.sh | sh
elif [[ "$OSTYPE" == "msys" ]]; then
    irm https://deno.land/install.ps1 | iex
else
    echo "Unsupported OS type: $OSTYPE"
    exit 1
fi


#install flit
pip install flit

#install Bril Tools
#cd C:/Users/Paul/ntu-ac-hw0-dofolin/
cd bril
deno install brili.ts

export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

cd bril-txt
flit install --symlink

# TODO: Add the commands to install the Bril environment tools.
# Make sure your script installs Deno, Flit, and the Bril tools.
# Ensure the script works on any machine and sets up the PATH correctly.
