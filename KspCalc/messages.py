import math

class Message(object):
    """Main message object."""

    fields = {}

    def __init__(self, dt, rocket, absTime=None):
        super(Message, self).__init__()
        self.dt = dt
        self.rocket = rocket
        self.absTime = absTime

    def getField(self, name):
        val = self.fields[name]
        if callable(val):
            val = val(self)
        # Cache value
        setattr(self, name, val)
        return val

    def toDict(self):
        return dict((name, self.getField(name)) for name in self.fields.keys())

    def setAbsTime(self, val):
        assert self.absTime is None
        self.absTime = val

    def __getattr__(self, name):
        return self.getField(name)

    def __repr__(self):
        text = " ".join("{!r}={!r}".format(name, self.getField(name)) for name in self.fields.keys())
        return "<{} {}>".format(self.__class__.__name__, text)

class RocketFlightLog(Message):

    fields = {
        "msg": lambda s: s.msg,
    }

    def __init__(self, msg, *args, **kwargs):
        super(RocketFlightLog, self).__init__(*args, **kwargs)
        self.msg = msg
        self.absTime = absTime

class StageFlightLog(Message):

    fields = {
        "Isp": lambda s: s.stage.Isp,
        "g": lambda s: s.rocket.position.g,
        "endMass": lambda s: s.rocket.mass,
        "startMass": lambda s: s.endMass + s.consumedKg,
        "thrustToWeightRatio": lambda s: s.stage.thrust / s.rocket.weight,
        "tsailkovskydV": lambda s: s.g * s.Isp * math.log(s.startMass / s.endMass),
        "tsailkovskydA": lambda s: s.tsailkovskydV / s.dt,
        "effectiveA": lambda s: s.tsailkovskydA - s.g,
        "effectivedV": lambda s: s.effectiveA * s.dt,
    }

    def __init__(self, stage, consumedKg, *args, **kwargs):
        super(StageFlightLog, self).__init__(*args, **kwargs)
        self.stage = stage
        self.consumedKg = consumedKg

class StageSeparation(Message):

    def __init__(self, stage, *args, **kwargs):
        super(StageSeparation, self).__init__(*args, **kwargs)
        self.stage = stage