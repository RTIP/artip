import os


class FlagRecorder:
    @staticmethod
    def mark_entry(details):
        with open(os.path.realpath('casa_scripts/flags.txt'), "a+") as flag_file:
            dict_tuples = {key: "'{0}'".format(str(value)) for key, value in details.items()}.items()
            entry = ' '.join(["=".join(line) for line in dict_tuples])
            flag_file.write(entry + '\n')
            flag_file.close()
