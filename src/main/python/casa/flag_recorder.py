import os


class FlagRecorder:

    def mark_entry(self, flag_file, details):
        with open(os.path.realpath(flag_file), "a+") as flag_file:
            dict_tuples = {key: "'{0}'".format(str(value)) for key, value in details.items()}.items()
            entry = ' '.join(["=".join(line) for line in dict_tuples])
            flag_file.write(entry + '\n')
            flag_file.close()
