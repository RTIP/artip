import casac


class AgentFlagger:
    def __init__(self, dataset_path):
        _casac = casac.casac
        _casac.logsink().filter('ERROR')
        self._af = _casac.agentflagger()
        self._af.open(dataset_path)

    def flag_summary(self):
        self._af.parsesummaryparameters()
        self._af.selectdata()
        self._af.init()
        summary = self._af.run()['report0']
        percent_flagged = summary['flagged'] / summary['total'] * 100
        print "Total data data flagged {0} %".format(percent_flagged)
