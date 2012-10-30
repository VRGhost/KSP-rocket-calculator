import re
import math

from KspCalc import parts as partLib
from KspCalc import messages

TIMES_RE = re.compile(r"^\s*(\d+)\s*x\s+", re.I)

class Rocket(object):

    name = stages = None
    _position = None
    position = property(lambda s: s._position)
    g = property(lambda s: s.position.g)
    ignited = False
    mass = property(lambda s: sum(stage.mass for stage in s.stages))
    weight = property(lambda s: sum(stage.weight for stage in s.stages))
    speed = None

    def __init__(self, name, stages=()):
        self.name = name
        self.stages = []
        if stages:
            for stage in stages:
                self.appendStage(stage)

    def appendStage(self, stage):
        if self.ignited:
            raise Exception("Rocket had been already ignited and simulation is running.")
        self.stages.append(stage)
        stage.attachedToRocket(self)
        
    def fly(self, dt=0.1):
        """Fly rocket till it is out of fuel."""
        self.ignited = True
        self.speed = 0
        absTime = 0
        while self.stages:
            if self.stages[-1].empty:
                yield messages.StageSeparation(
                    rocket=self,
                    stage=self.stages.pop(-1),
                    dt=dt,
                    absTime=absTime,
                )
            else:
                stage = self.stages[-1]
                for msg in stage.fly(dt):
                    msg.setAbsTime(absTime)

                    dV = msg.stage.acceleration * dt
                    if self.position.standingOnSurface:
                        dV = max(dV, 0)
                        self.speed = max(self.speed, 0)

                    self.speed += dV
                    self.position.changeAlt(self.speed * dV)

                    yield msg
                    absTime += dt


    def setPos(self, pos):
        if self.ignited:
            raise Exception("Cannot set position of an ignited rocket.")
        self._position = pos

    @property
    def thrustRate(self):
        return self._thrust

    @thrustRate.setter
    def thrustRate(self, value):
        assert value >= 0 and value <= 1
        self._thrust = float(value)

    @classmethod
    def fromDict(cls, data):
        assert "stages" in data, "Stages have to be specified to build rocket."
        rocket = cls(
            name=data.get("name", "Unknown rocket."),
            stages=(Stage.fromDict(el) for el in data["stages"])
        )
        return rocket

    def getAboveStage(self, stage):
        pos = self.stages.index(stage)
        if pos > 0:
            rv = self.stages[pos - 1]
        else:
            rv = None
        return rv

    def __repr__(self):
        return "<{} {!r} parts={} stages={}>".format(self.__class__.__name__, self.name, self.parts, self.stages)

class Stage(object):
    """Stage of a rocket."""

    parts = name = _rocket = None

    engines = property(lambda s: (part for part in s.parts if part.isEngine))
    fuelTanks = property(lambda s: (part for part in s.parts if part.isFuelTank))

    rocket = property(lambda s: s._rocket)
    aboveStage = property(lambda s: s.rocket.getAboveStage(s))
    position = property(lambda s: s.rocket.position)

    mass = property(lambda s: sum(part.mass for part in s.parts))
    weight = property(lambda s: sum(part.weight for part in s.parts))
    consumptionKg = property(lambda s: sum(el.consumptionKg for el in s.engines))

    empty = property(lambda s: all(tank.empty for tank in s.fuelTanks))

    thrust = property(lambda s: sum(eng.thrust for eng in s.engines))
    twRatio = property(lambda s: s.thrust / s.rocket.weight)
    effectiveThrust = property(lambda s: s.thrust - s.rocket.weight)
    acceleration = property(lambda s: s.effectiveThrust / s.rocket.mass)

    def __init__(self, parts, name):
        self.parts = tuple(partCls(self) for partCls in parts)
        self.name = name
        self._rocket = None

    def fly(self, dt):
        # Fly this stage
        while not self.empty:
            fullMass = self.rocket.mass

            consumeMax = self.consumptionKg * dt
            consumed = consumeMax - self._consume(consumeMax)

            emptyMass = self.rocket.mass
            assert abs(fullMass - (emptyMass + consumed)) < 1e-6
            yield messages.StageFlightLog(
                rocket=self.rocket,
                stage=self,
                consumedKg=consumed,
                dt=dt,
            )


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
        return cls(parts=parts, name=data.get("name"))

    def attachedToRocket(self, newRocket):
        assert self._rocket is None
        self._rocket = newRocket

    @property
    def Isp(self):
        vals = tuple(el.Isp for el in self.engines)
        return sum(vals) / float(len(vals))

    def _consume(self, amount):
        """Consume given number of kilograms of a fuel.

        Returns number of kilograms that were impossible to consume
        because of the fuel tank depletion.
        """
        for tank in self.fuelTanks:
            amount = tank.consumeKg(amount)
            if amount == 0:
                break
        return amount


    def __repr__(self):
        return "<{} {!r} parts={}>".format(self.__class__.__name__, self.name, self.parts)
