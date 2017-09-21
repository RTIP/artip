from sh import egrep, ErrorReturnCode_1
from watchdog.events import RegexMatchingEventHandler
import logging


class LogEventHandler(RegexMatchingEventHandler):
    def __init__(self, log_file, pattern, regexes):
        self.previous_logs = []
        self.log_file = log_file
        self.pattern = pattern
        super(LogEventHandler, self).__init__(regexes=regexes)

    def disable_logging(func):
        def wrapper(*args, **kwargs):
            logging.disable(logging.INFO)
            result = func(*args, **kwargs)
            logging.disable(logging.NOTSET)
            return result
        return wrapper

    @disable_logging
    def on_modified(self, event):
        logs = self.get_matching_logs()
        for log in logs:
            if log not in self.previous_logs:
                self.previous_logs.append(log)
                print log

    def get_matching_logs(self):
        logs = []
        try:
            logs = egrep("-i", self.pattern, self.log_file)
        except ErrorReturnCode_1:
            pass
        return logs
