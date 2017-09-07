from glob import glob
import subprocess
import time
ms_chunks=glob("*.ms/")
for ms in ms_chunks:
	ms_name = ms.split('.')[0]
	output_file = "exec1/{0}.txt".format(ms_name)
        log_file = "exec1/casa-{0}.log".format(ms_name)
        tclean = "tclean(vis='{0}', imagename='exec1/{1}', imsize=128, cell=['0.5arcsec'], stokes='I', weighting='briggs', robust=0.5, restoringbeam='', uvtaper='', mask='', interactive=F, niter=0, deconvolver='hogbom', specmode='cube', nterms=1, reffreq='', nchan=-1, start='', width='', outframe='topo', veltype='', restfreq='', gridder='standard', facets=1, wprojplanes=1, aterm=True, psterm=False, wbawp=False, conjbeams=True, pblimit=0.2, normtype='flatnoise', pbcor=False, gain=0.1, threshold='10.0mJy', cycleniter=-1, cyclefactor=1.0, savemodel='none', parallel=False, spw='0')".format(ms,ms_name)
        command = "casa --nologger --nogui --logfile {0} -c \"{1}\"".format(log_file,tclean)
	#print command
	time.sleep(0.5)
	subprocess.Popen(command, stdin=subprocess.PIPE, stdout=file(output_file, 'a+'), shell=True)
