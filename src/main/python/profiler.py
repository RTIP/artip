import cProfile
import lsprofcalltree


class Profiler(object):
    def __init__(self):
        self.c_profile = cProfile.Profile()

    def __enter__(self):
        self.c_profile.enable()
        return self.c_profile

    def __exit__(self, *args):
        self.c_profile.disable()
        k_profile = lsprofcalltree.KCacheGrind(self.c_profile)
        k_file = open('profile_result.out', 'w+')
        k_profile.output(k_file)
        k_file.close()
        self.c_profile.print_stats('cumulative')
