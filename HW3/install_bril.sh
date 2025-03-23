#!/bin/bash

cd bril
deno install brili.ts
pip install --user flit
cd bril-txt
flit install --symlink --user