import zipfile
import os


class Packager:
    exclude_directories = ['.git', '.idea', 'output', 'resources', 'target', 'artip']
    exclude_files = ['./.gitignore', './build.pyc', './.DS_Store', './packager.pyc']

    def __init__(self, filename, root_directory):
        self._root_directory = root_directory
        self._filename = filename

    def package(self):
        zip_file = zipfile.ZipFile(self._filename, 'w')
        if os.path.isfile(self._root_directory):
            zip_file.write(self._root_directory)
        else:
            self._addFolderToZip(zip_file, self._root_directory)
        zip_file.close()

    def _addFolderToZip(self, zip_file, folder):
        for file in os.listdir(folder):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path) and not self._is_excluded_file(full_path):
                print 'File added: ' + str(full_path)
                zip_file.write(full_path)
            elif os.path.isdir(full_path):
                if not self._is_excluded_directory(full_path):
                    print 'Entering folder: ' + str(full_path)
                    self._addFolderToZip(zip_file, full_path)

    def _is_excluded_file(self, file_path):
        is_zip_file = file_path.endswith('.zip')
        file_excluded = any(exclude_file == file_path for exclude_file in Packager.exclude_files)
        return is_zip_file or file_excluded

    def _is_excluded_directory(self, directory_path):
        directory_excluded = any(
            exclude_directory in directory_path for exclude_directory in Packager.exclude_directories)
        return directory_excluded
