import os


def minus(list1, list2):
    return filter(lambda elm: elm not in list2, list1)


def is_last_element(ele, elements):
    return ele == elements[len(elements) - 1]


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def calculate_percentage(favourable, total):
    try:
        percentage = (float(favourable) / float(total)) * 100
    except ZeroDivisionError:
        percentage = 0
    return percentage


def format_spw_with_channels(spw_list, channel):
    return ",".join(["{0}:{1}".format(s, channel) for s in spw_list.split(",")])
