from amplitude_matrix import AmplitudeMatrix


class Window:
    def __init__(self, collection, bucket_size, overlap_count):
        self.__key = collection.keys()[0]
        self.__values = collection.values()[0]
        self.__bucket_size = bucket_size
        self.__overlap_count = overlap_count
        self.__window_start_index = 0

    def slide(self):
        # print "BaseLine=",self.__key," Window start=", self.__window_start_index, "  Window End=",(self.__window_start_index + self.__bucket_size)
        window_data = self.__values[self.__window_start_index:self.__window_start_index + self.__bucket_size]
        if len(window_data) > 0:
            self.__window_start_index = (self.__window_start_index + self.__bucket_size) - self.__overlap_count
        return AmplitudeMatrix(None, None, None, None, {self.__key: window_data})

    def current_position(self):
        start = (self.__window_start_index - self.__bucket_size) + self.__overlap_count
        end = (start + self.__bucket_size) - 1
        if end > len(self.__values):
            end = len(self.__values) - 1
        return start, end
