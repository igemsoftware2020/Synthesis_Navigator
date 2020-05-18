#!/bin/zsh

echo "Strated running FVA with glpk..."
start_tm=`date +%s%N`;
for li in ../MOD/*
do
    outp=${li:7}
    glpsol -m ${li} -o "../SOL/${outp//mod/sol}" > "../LOG/${outp//mod/log}" &
done
end_tm=`date +%s%N`;
use_tm=`echo $end_tm $start_tm | awk '{ print ($1 - $2) / 1000000000}'`
echo "Time cost: $use_tm s"
echo "Done!"



