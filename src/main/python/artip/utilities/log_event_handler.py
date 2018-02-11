from sh import egrep, ErrorReturnCode_1
from watchdog.events import RegexMatchingEventHandler
import logging
from artip.configs import config


class LogEventHandler(RegexMatchingEventHandler):
    IMAGING_LOGS_EVENT_HANDLER = None

    def __init__(self, log_file, pattern, regexes):
        self.previous_logs = []
        self.log_file = log_file
        self.pattern = pattern
        self._disable_third_party_loggers()
        super(LogEventHandler, self).__init__(regexes=regexes)

    @staticmethod
    def imaging_log_handler():
        if not LogEventHandler.IMAGING_LOGS_EVENT_HANDLER:
            LogEventHandler.IMAGING_LOGS_EVENT_HANDLER = LogEventHandler(log_file=config.OUTPUT_PATH + "/casa.log",
                                  pattern="(Reached global stopping criterion)|(>>>>)",
                                  regexes=[r".*\.log"])

        return LogEventHandler.IMAGING_LOGS_EVENT_HANDLER

    def _disable_third_party_loggers(self):
        loggers = ['sh.command', 'sh.command.process', 'sh.command.process.streamreader', 'sh.stream_bufferer',
                   'sh.streamreader', 'sh.stream_bufferer','watchdog.observers.inotify_buffer']
        for logger in loggers:
            logger = logging.getLogger(logger)
            logger.disabled = 1

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
