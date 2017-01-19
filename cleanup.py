import os, re, shutil


def clean():
    dir = "."
    patterns = [".log", ".table", ".last"]
    for f in os.listdir(dir):
        for pattern in patterns:
            if re.search(pattern, f):
                f = os.path.join(dir, f)
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)
