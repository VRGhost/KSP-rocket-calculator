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
        return val

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
        "rocket": lambda s: s.rocket.name,
        "msg": lambda s: s.msg,
    }

    def __init__(self, msg, *args, **kwargs):
        super(RocketFlightLog, self).__init__(*args, **kwargs)
        self.msg = msg
        self.absTime = absTime

class StageFlightLog(Message):

    fields = {
        "thrustToWeightRatio": lambda s: s.stage.thrust / s.rocket.weight,
        "dV": lambda s: s.rocket.position.g * s.stage.Isp * math.log((s.rocket.mass + s.consumedKg) / s.rocket.mass),
    }

    def __init__(self, stage, consumedKg, *args, **kwargs):
        super(StageFlightLog, self).__init__(*args, **kwargs)
        self.stage = stage
        self.consumedKg = consumedKg

class StageSeparation(Message):

    def __init__(self, stage, *args, **kwargs):
        super(StageSeparation, self).__init__(*args, **kwargs)
        self.stage = stage