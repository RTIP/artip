#!/bin/bash

# Arg1 = path to working dir
# Arg2 = path to MS
# Arg3 = Chunk name
# Arg4 = Chunk number to process

hosts=('hpc082' 'hpc083' 'hpc084' 'hpc085' 'hpc086' 'hpc087' 'hpc088' 'hpc089' 'hpc090' 'hpc091' 'hpc092' 'hpc093' 'hpc094')
#hosts=('hpc086' 'hpc086')
echo $@
ms_path='/scratch/carti/data/spike-1/tclean-MPI/mkt30min_entire_cluster'

for index in {1..13}; do
    host="${hosts[$index-1]}"
    ms_chunk_name="$ms_path/mkt_30min_0_2047_chunk_$index.ms"
    #echo "Processing $ms_chunk_name at $host"

    for path in $ms_path/*.ms; do
        [ -d "${path}" ] || continue # if not a directory, skip
        dirname="$(basename "${path}")"
        #echo $dirname
        echo "Processing $ms_path/$dirname at $host"
        ssh $host /scratch/carti/data/spike-1/tclean-MPI/tclean.py $ms_path/$dirname $host&
        done

    #logout
done
