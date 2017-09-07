#!/bin/bash

# Invoke this script as follows 
# <this-script-name> <fully qualified path to chunk without chunk number> <number of chunks to run>
# ./tcleanOnCluster.sh /scratch/carti/data/spike-1/tclean-MPI/mkt30min_entire_cluster/mkt_30min_0_2047_chunk 16


#hosts=('hpc082' 'hpc083' 'hpc084' 'hpc085' 'hpc086' 'hpc087' 'hpc088' 'hpc089' 'hpc090' 'hpc091' 'hpc092' 'hpc093' 'hpc094')
hosts=('hpc085' 'hpc086')
#hosts=('hpc082' 'hpc086')
# echo $@

startTclean()
{
    myFuncName="startTclean"
    msName=$1
    nChunks=$2
    nHosts=${#hosts[@]}
    
    echo "$myFuncName:: ms name = $msName"
    echo "$myFuncName:: Total chunks = $nChunks"
    echo "$myFuncName:: hosts = $nHosts"

    # if nChunks <= nHosts
    if [ $nChunks -le $nHosts ]
    then
        echo "$myFuncName:: nChunks $nChunks <= nHosts $nHosts"
    else 
        echo "$myFuncName:: nChunks $nChunks > nHosts $nHosts"
    fi
    tclean $@
}

tclean()
{
    myFuncName="tclean"
    
    # Create result directory and subdirectories
    parentDir="$(dirname "${msName}")"
    resultDir="tclean-$nChunks-chunks-$nHosts-nodes-$(date +%Y%m%d-%H%M%S)"
    
    mkdir -p $parentDir/$resultDir
    mkdir -p $parentDir/$resultDir/output
    mkdir -p $parentDir/$resultDir/images
    mkdir -p $parentDir/$resultDir/logs

    echo "$myFuncName:: -------- Result can be found at $parentDir/$resultDir"

    # Run tclean for each chunk
    iChunk=1
    iHost=1
    while [[ $iChunk -le $nChunks ]]
    do
        # Process chunk number iChunk
        onHost="${hosts[$iHost-1]}"
        msChunkPath="${msName}_$iChunk.ms"
        msChunkName="$(basename "${msChunkPath}")" 
        echo "$myFuncName:: Processing $msChunkName on $onHost"

        #ssh $onHost /scratch/carti/data/spike-1/tclean-MPI/tclean.py $msChunkPath $onHost&
        ssh $onHost "cd $parentDir/$resultDir; mkdir -p $onHost; cd $onHost; /scratch/carti/data/spike-1/tclean-MPI/tclean.py $parentDir/$resultDir $msChunkPath $onHost&"

        # increment before iteration ends
        iChunk=$((iChunk + 1))
        iHost=$((iHost + 1))

        if [[ $iHost -gt $nHosts ]]
        then
            iHost=1
        fi

        # Add a delay of few seconds to avoid CASA errors
        sleep 2s
    done
}

startTclean $@
