#!/usr/bin/env python

import subprocess
import time

command = "casa --nogui --logfile {0} -c \"exit()\"".format("local_log.txt")
print command

subprocess.Popen(command, stdin=subprocess.PIPE, stdout=file("output_file.txt", 'a+'), shell=True)
time.sleep(10)
print("---------- End of tcleanOnCluster with MPI!")

