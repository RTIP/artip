#!/usr/bin/env python

from mpi4py import MPI
import subprocess
import time
#import os
#print os.environ

comm = MPI.COMM_WORLD
size = comm.size
rank = comm.rank

chunk_prefix = "mkt_30min_0_2047_chunk"   # This should be parameterized
ms_name = "{0}_{1}".format(chunk_prefix, rank+1)
output_file = "output/{0}.txt".format(ms_name)
log_file = "logs/casa-{0}.log".format(ms_name)

if rank == 0:
    print("---------- Starting tcleanOnCluster with MPI - cluster size = {0}".format(size))
    print("[MPI Client rank {0}] Starting tclean on chunk {1}.ms".format(rank, ms_name))
else:
    print("[MPI node rank {0}] Starting tclean on chunk {1}.ms".format(rank, ms_name))

#comm.Barrier()   # wait for everybody to synchronize _here_

tclean = "tclean(vis='{0}.ms', imagename='output/{1}', imsize=128, cell=['0.5arcsec'], stokes='I', weighting='briggs', robust=0.5, restoringbeam='', uvtaper='', mask='', interactive=F, niter=0, deconvolver='hogbom', specmode='cube', nterms=1, reffreq='', nchan=-1, start='', width='', outframe='topo', veltype='', restfreq='', gridder='standard', facets=1, wprojplanes=1, aterm=True, psterm=False, wbawp=False, conjbeams=True, pblimit=0.2, normtype='flatnoise', pbcor=False, gain=0.1, threshold='10.0mJy', cycleniter=-1, cyclefactor=1.0, savemodel='none', parallel=False, spw='0')".format(ms_name, ms_name)

#command = "casa --nologger --nogui --logfile {0} -c \"{1}\"".format(log_file,tclean)
command = "casa --nogui --logfile {0} -c \"exit()\"".format(log_file)
#command = "./unsetMpi.py {0} {1}".format(log_file,output_file)
#command = "echo 'Hello'"
print command
time.sleep(0.5)
#print os.environ
subprocess.Popen(command, stdin=subprocess.PIPE, stdout=file(output_file, 'a+'), shell=True).wait()


#comm.Barrier()
#comm.Wait()

if rank == 0:
    print("---------- End of tcleanOnCluster with MPI!")

