#!/usr/bin/env python

from glob import glob
import subprocess
import sys
import os
import time
#ms_chunks=glob("*.ms/")

#listobs="listobs(vis='/scratch/carti/aug6.ms', listfile='/scratch/carti/aug6.ms.listobs')"

result_dir = sys.argv[1]
ms_file_path = sys.argv[2]
host = sys.argv[3]
ms_name = os.path.basename(ms_file_path)
#output_path = os.path.dirname(ms_file_path)
ms_file = ms_name.split('.')[0]
image_name = "{0}/images/{1}_{2}".format(result_dir, ms_file, host)
log_file = "{0}/logs/{1}_{2}.log".format(result_dir, ms_file, host)
output_file = "{0}/output/{1}_{2}.txt".format(result_dir, ms_file, host)

tclean = "tclean(vis='{0}', imagename='{1}', imsize=128, cell=['0.5arcsec'], stokes='I', weighting='briggs', robust=0.5, restoringbeam='', uvtaper='', mask='', interactive=F, niter=0, deconvolver='hogbom', specmode='cube', nterms=1, reffreq='', nchan=-1, start='', width='', outframe='topo', veltype='', restfreq='', gridder='standard', facets=1, wprojplanes=1, aterm=True, psterm=False, wbawp=False, conjbeams=True, pblimit=0.2, normtype='flatnoise', pbcor=False, gain=0.1, threshold='10.0mJy', cycleniter=-1, cyclefactor=1.0, savemodel='none', parallel=False, spw='0')".format(ms_file_path,image_name)
command = "casa --nologger --nogui --logfile {0} -c \"{1}\"".format(log_file, tclean)
subprocess.Popen(command, stdin=subprocess.PIPE, stdout=file(output_file, 'a+'), shell=True)
time.sleep(0.5)
