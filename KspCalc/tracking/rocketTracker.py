from . import telemetry

class RocketTracker(object):
    """An object that launches and tracks a rocket."""

    launched = property(lambda s: s.rocket.ignited)
    _flyIter = _dataCollector = None

    def __init__(self, rocket, dt=0.01, reportFreq=1, reportWindows=None):
        self.rocket = rocket
        self.dt = dt
        self.reportFreq = reportFreq
        self._nextReportAt = reportFreq
        self._dataCollector = telemetry.Flight(self.rocket)
        if reportWindows:
            self._reportWindows = tuple(reportWindows)

    def launch(self):
        self._flyIter = self.rocket.fly(dt=self.dt)

    def track(self):
        assert self._flyIter
        msg = self.step()
        while msg is not None:
            doYield = False
            if msg is not True:
                if self._reportWindows:
                    time = msg["time"]
                    doYield = any(start <= time <= end for (start, end) in self._reportWindows)
                else:
                    doYield = True

            if doYield:
                yield msg
            msg = self.step()

    def step(self):
        msg = self._step()

        if msg is None:
            if self._dataCollector:
                rv = self._dataCollector.getData()
                self._dataCollector = None
            else:
                rv = None
            return rv

        assert msg is not None

        if msg.msgType == "StageSeparation":
            tmp = telemetry.StageSeparation(self.rocket)
            tmp.accumulate(msg)
            rv = tmp.getData()
        else:
            assert msg.msgType == "FlightLog"
            self._dataCollector.accumulate(msg)
            if self._nextReportAt <= msg.absTime:
                rv = self._dataCollector.getData()
                self._dataCollector = telemetry.Flight(self.rocket)
                self._nextReportAt = msg.absTime + self.reportFreq
            else:
                rv = True
        return rv


    def _step(self):
        if not self._flyIter:
            return None
        try:
            return self._flyIter.send(None)
        except StopIteration:
            self._flyIter = None
            return None