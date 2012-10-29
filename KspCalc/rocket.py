import re
import math

from KspCalc import parts as partLib

TIMES_RE = re.compile(r"^\s*(\d+)\s*x\s+", re.I)

class Rocket(object):

    parts = name = stages = None
    _thrust = 1.00
    _position = None
    position = property(lambda s: s._position)

    def __init__(self, parts, name=None):
        self.name = name or "Unknown rocket."
        self.parts = [part(self) for part in parts]
        self.stages = []

    def appendStage(self, stage):
        self.stages.append(stage)

    def getDeltaV(self):
        print(self.position)
        assert self.position, self.position
        massFull = sum(el.mass for el in self.fuelTanks)
        massEmpty = sum(el.massEmpty for el in self.fuelTanks)
        g = self.position.g
        isp = tuple(el.iSp for el in self.engines)
        ans = 0
        return ans + sum(el.getDeltaV() for el in self.stages)
        print(tuple(self.engines))
        print isp

    def setPos(self, pos):
        self._position = pos

    @property
    def thrustRate(self):
        return self._thrust

    @thrustRate.setter
    def thrustRate(self, value):
        assert value >= 0 and value <= 1
        self._thrust = float(value)

    engines = property(lambda s: (part for part in s.parts if part.isEngine))
    fuelTanks = property(lambda s: (part for part in s.parts if part.isFuelTank))

    @classmethod
    def fromDict(cls, data):
        assert "parts" in data, "Parts have to be specified to build rocket."
        parts = []
        for name in data["parts"]:
            name = name.strip()
            match = TIMES_RE.match(name)
            if match:
                times = int(match.group(1))
                name = name[:match.start()] + name[match.end():]
            else:
                times = 1
            part = partLib.findByName(name)
            parts.extend((part, ) * times)
        rocket = cls(parts=parts, name=data.get("name"))
        for stage in data.get("stages", ()):
            rocket.appendStage(cls.fromDict(stage))
        return rocket

    def __repr__(self):
        return "<{} {!r} parts={} stages={}>".format(self.__class__.__name__, self.name, self.parts, self.stages)
