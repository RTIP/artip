from amplitude_matrix import AmplitudeMatrix

class Window:
    def __init__(self, collection, config):
        self._collection = collection
        self._bucket_size = config['bucket_size']
        self._overlap_count = config['overlap']
        self._window_start_index = config['start_index']
        self._window_data = None
        self._config = config

    def slide(self):
        self._window_data = dict(
            (baseline, amp_data[self._window_start_index:self._window_start_index + self._bucket_size]) for
            baseline, amp_data in self._collection.iteritems())
        if self._window_item_count() == self._bucket_size:
            self._window_start_index = self._next_window_start_index()

        return AmplitudeMatrix(None, None, None, None, self._config, self._window_data)

    def current_position(self):
        start = (self._window_start_index - self._bucket_size) + self._overlap_count
        end = (start + self._bucket_size) - 1
        if self._window_item_count() < self._bucket_size:
            start = self._window_start_index
            end = self._collection_size() - 1
        return start, end

    def reached_end_of_collection(self):
        return self.current_position()[1] == (self._collection_size() - 1)

    def _collection_size(self):
        return len(self._collection.values()[0])

    def _next_window_start_index(self):
        return (self._window_start_index + self._bucket_size) - self._overlap_count

    def _window_item_count(self):
        return len(self._window_data.values()[0])
