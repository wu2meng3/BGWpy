#!/usr/bin/env bash

MPIRUN='mpirun -n 1 --npernode 1'
PW='pw.x'
PWFLAGS=''

ln -nfs ../../11-Density/GaAs.save/charge-density.dat GaAs.save/charge-density.dat

cp -f ../11-Density/GaAs.save/data-file.xml GaAs.save/data-file.xml

$MPIRUN $PW $PWFLAGS -in wfn.in &> wfn.out
