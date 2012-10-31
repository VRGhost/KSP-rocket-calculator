import re
import math

from KspCalc import parts as partLib
from . import messages

TIMES_RE = re.compile(r"^\s*(\d+)\s*x\s+", re.I)
__NULL__ = object()

def AVG(seq):
    sum = 0.0
    len = 0
    for el in seq:
        sum += el
        len += 1

    if len == 0:
        return 0
    else:
        return sum / len

class Rocket(object):

    name = stages = None
    _position = None
    position = property(lambda s: s._position)
    g = property(lambda s: s.position.g)
    ignitedStages = property(lambda s: (stage for stage in s.stages if stage.ignited))
    ignited = property(lambda s: any(stage.ignited for stage in s.stages))
    mass = property(lambda s: sum(stage.mass for stage in s.stages))
    weight = property(lambda s: sum(stage.weight for stage in s.stages))
    speed = None

    drag = 0 # Drag coeficitent for the rocket = C_d <physical "drag coef"> * A <ref. area>

    Isp = property(lambda s: AVG(el.Isp for el in s.ignitedStages))
    thrust = property(lambda s: sum(el.thrust for el in s.ignitedStages))

    def __init__(self, name, stages=(), drag=0):
        self.name = name
        self.stages = []
        self.drag = drag
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
        self.speed = 0
        self.dt = dt
        absTime = 0
        assert self.stages
        while self.stages:
            separated = []
            for stage in tuple(self.ignitedStages):
                if (stage not in separated) and stage.empty:
                    for msg in self.separateStage(stage):
                        separated.append(msg.stage)
                        msg.setAbsTime(absTime)
                        yield msg
            else:
                # No ignited stages
                self._igniteNextStage()

            while self.stages and (self.stages[-1].empty):
                # separate useless bottom stages
                assert self.stages[-1].empty, self.stages[-1].name
                for msg in self.separateStage(self.stages[-1]):
                    separated.append(msg.stage)
                    msg.setAbsTime(absTime)

                    yield msg

            consumed = sum(stage.step(dt) for stage in self.ignitedStages)
            if consumed:
                msg = messages.FlightLog(
                    rocket=self,
                    consumedKg=consumed,
                    absTime=absTime,
                    dt=dt,
                )

                dV = msg.effectivedV
                if self.position.standingOnSurface:
                    dV = max(dV, 0)
                    self.speed = max(self.speed, 0)

                self.speed += dV
                self.position.changeAlt(self.speed * msg.dt)

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

    def ignite(self):
        """Ignite rocket."""
        assert not self.ignited
        self._igniteNextStage()

    def _igniteNextStage(self):
        if not self.stages:
            return
        self.stages[-1].ignite()

    def getStage(self, name, rv=__NULL__):
        out = [stage for stage in self.stages if stage.name == name]
        if not out:
            if rv != __NULL__:
                return rv
            raise ValueError("Stage {!r} not found".format(name))
        elif len(out) > 1:
            raise ValueError("More than one stage with name {!r} present".format(name))
        return out[0]

    def getDefaultStageName(self, stage):
        return "Stage #{}".format(self.stages.index(stage) + 1)

    def separateStage(self, stage):
        pos = self.stages.index(stage)
        # when separating stage, all stages below one
        # that is separated are separated as well.
        toSeparate = self.stages[pos:]
        toSeparate.reverse()
        for el in toSeparate:
            assert el.empty
            self.stages.remove(el)
            yield messages.StageSeparation(
                rocket=self,
                stage=el,
                dt=self.dt,
            )

    def copy(self):
        data = self.toDict()
        cls = type(self)
        obj = cls.fromDict(data)
        obj.setPos(self.position.copy())
        return obj

    def toDict(self):
        return {
            "name": self.name,
            "stages": [stage.toDict() for stage in self.stages],
            "drag": self.drag,
        }

    @classmethod
    def fromDict(cls, data):
        assert "stages" in data, "Stages have to be specified to build rocket."
        rocket = cls(
            name=data.get("name", "Unknown rocket."),
            stages=(Stage.fromDict(el) for el in data["stages"]),
            drag=data.get("drag", 0),
        )
        return rocket

    def __repr__(self):
        return "<{} {!r} parts={} stages={}>".format(self.__class__.__name__, self.name, self.parts, self.stages)

class Stage(object):
    """Stage of a rocket."""

    parts = name = _rocket = _takesFuel = None
    _ignited = False
    ignited = property(lambda s: s._ignited)

    engines = property(lambda s: (part for part in s.parts if part.isEngine))
    localFuelTanks = property(lambda s: (part for part in s.parts if part.isFuelTank))

    rocket = property(lambda s: s._rocket)
    position = property(lambda s: s.rocket.position)

    mass = property(lambda s: sum(part.mass for part in s.parts))
    weight = property(lambda s: sum(part.weight for part in s.parts))
    consumptionKg = property(lambda s: sum(el.consumptionKg for el in s.engines))

    empty = property(lambda s: all(tank.empty for tank in s.fuelTanks))

    thrust = property(lambda s: sum(eng.thrust for eng in s.engines))
    twRatio = property(lambda s: s.thrust / s.rocket.weight)

    Isp = property(lambda s: AVG(el.Isp for el in s.engines))

    def __init__(self, parts, name, ignites, takesFuel):
        self.parts = tuple(partCls(self) for partCls in parts)
        self.name = name
        self._rocket = None
        if isinstance(ignites, str):
            ignites = (ignites, )
        self._ignites = ignites

        if isinstance(takesFuel, str):
            takesFuel = (takesFuel, )

        if takesFuel:
            if "self" not in takesFuel:
                raise ValueError(
                    "If you are specefiing what stages this stage takes fuel from, " \
                    "do not forget to include 'self' in to the list"
                )
            takesFuel = list(takesFuel)
        self._takesFuel = takesFuel

    def step(self, dt):
        # Fly this stage
        if self.empty:
            return 0

        fullMass = self.rocket.mass

        consumeMax = self.consumptionKg * dt
        consumed = consumeMax - self._consume(consumeMax)

        emptyMass = self.rocket.mass
        assert abs(fullMass - (emptyMass + consumed)) < 1e-6
        return consumed

    def attachedToRocket(self, newRocket):
        assert self._rocket is None
        self._rocket = newRocket
        if not self.name:
            self.name = self.rocket.getDefaultStageName(self)

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

    def ignite(self):
        if self.ignited:
            return
        self._ignited = True
        if self._ignites:
            for name in self._ignites:
                self.rocket.getStage(name).ignite()

    @property
    def fuelTanks(self):
        if self._takesFuel:
            toRm = ()
            for name in self._takesFuel:

                if name == "self":
                    stage = self
                else:
                    stage = self.rocket.getStage(name, None)
                    if not stage:
                        toRm += (name, )
                        continue
                for tank in stage.localFuelTanks:
                    yield tank
            for name in toRm:
                self._takesFuel.remove(name)
        else:
            for tank in self.localFuelTanks:
                yield tank

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
        return cls(
            parts=parts,
            name=data.get("name"),
            ignites=data.get("ignites"),
            takesFuel=data.get("takesFuel")
        )

    def toDict(self):
        return {
            "name": self.name,
            "ignites": self._ignites,
            "takesFuel": self._takesFuel,
            "parts": [el.name for el in self.parts],
        }


    def __repr__(self):
        return "<{} {!r} parts={}>".format(self.__class__.__name__, self.name, self.parts)
