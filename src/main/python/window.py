from amplitude_matrix import AmplitudeMatrix
import numpy
from config import *


class Window:
    def __init__(self, collection, bucket_size=DETAIL_FLAG_CONFIG['sliding_window']['bucket_size'],
                 overlap_count=DETAIL_FLAG_CONFIG['sliding_window']['overlap']):
        self.__collection = collection
        self.__bucket_size = bucket_size
        self.__overlap_count = overlap_count
        self.__window_start_index = 0

    def slide(self):
        window_data = dict(
            (baseline, amp_data[self.__window_start_index:self.__window_start_index + self.__bucket_size]) for
            baseline, amp_data in self.__collection.iteritems())
        if len(numpy.array(window_data.values()).flatten()) > 0:
            self.__window_start_index = (self.__window_start_index + self.__bucket_size) - self.__overlap_count
        return AmplitudeMatrix(None, None, None, None, window_data)

    def current_position(self):
        readings_count = len(self.__collection[self.__collection.keys()[0]])
        start = (self.__window_start_index - self.__bucket_size) + self.__overlap_count
        end = (start + self.__bucket_size) - 1
        if end > readings_count:
            end = readings_count - 1
        return start, end

    def reached_end_of_collection(self):
        start, end = self.current_position()
        return start == end
