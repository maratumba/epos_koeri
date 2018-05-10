#!/bin/bash

# bash setup-seiscomp3.sh

seiscomp enable fdsnws
seiscomp start

exec "$@"
