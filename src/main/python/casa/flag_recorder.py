import os


class FlagRecorder:
    def __init__(self, flag_file_name):
        self._flag_file_name = flag_file_name
        self.touch_flag_file()

    def touch_flag_file(self):
        flag_record_file = open(self._flag_file_name, 'a')
        flag_record_file.close()

    def mark_entry(self, details):
        with open(os.path.realpath(self._flag_file_name), "a+") as flag_file:
            dict_tuples = {key: "'{0}'".format(str(value)) for key, value in details.items()}.items()
            entry = ' '.join(["=".join(line) for line in dict_tuples])
            flag_file.write(entry + '\n')
            flag_file.close()
