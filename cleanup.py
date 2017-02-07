import os, re, shutil


def clean():
    dir = "."
    patterns = [".log", ".last"]
    for f in os.listdir(dir):
        for pattern in patterns:
            if re.search(pattern, f):
                f = os.path.join(dir, f)
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.remove(f)


def deep_clean():
    clean()
    dir = "./output"
    for f in os.listdir(dir):
        f = os.path.join(dir, f)
        shutil.rmtree(f)


# deep_clean()
