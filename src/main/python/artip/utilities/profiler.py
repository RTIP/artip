import cProfile
import lsprofcalltree
from artip.configs import config


class Profiler(object):
    def __init__(self):
        self.c_profile = cProfile.Profile()

    def __enter__(self):
        self.c_profile.enable()

    def __exit__(self, *args):
        self.c_profile.disable()
        k_profile = lsprofcalltree.KCacheGrind(self.c_profile)
        k_file = open("{0}/profile_result.out".format(config.OUTPUT_PATH), 'w+')
        k_profile.output(k_file)
        k_file.close()
        self.c_profile.print_stats('cumulative')
