import math

class Message(object):
    """Main message object."""

    msgType = property(lambda s: s.__class__.__name__)
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

class FlightLog(Message):

    fields = {
        "Isp": lambda s: s.rocket.Isp,
        "g": lambda s: s.rocket.position.g,
        "endMass": lambda s: s.rocket.mass,
        "startMass": lambda s: s.endMass + s.consumedKg,
        "thrustToWeightRatio": lambda s: s.rocket.thrust / s.rocket.weight,
        "tsailkovskydV": lambda s: s.g * s.Isp * math.log(s.startMass / s.endMass),
        "tsailkovskydA": lambda s: s.tsailkovskydV / s.dt,
        "speed": lambda s: s.rocket.speed,
        "dragCoef": lambda s: s.rocket.drag,
        "airDensity": lambda s: s.rocket.position.density,
        "dragForce": lambda s: 0.5 * s.airDensity * (s.speed ** 2) * s.dragCoef,
        "dragDeAccel": lambda s: s.dragForce / s.endMass,

        "effectiveA": lambda s: s.tsailkovskydA - s.g - s.dragDeAccel,
        "effectivedV": lambda s: s.effectiveA * s.dt,
    }

    def __init__(self, consumedKg, *args, **kwargs):
        super(FlightLog, self).__init__(*args, **kwargs)
        self.consumedKg = consumedKg

class StageSeparation(Message):

    def __init__(self, stage, *args, **kwargs):
        super(StageSeparation, self).__init__(*args, **kwargs)
        self.stage = stage