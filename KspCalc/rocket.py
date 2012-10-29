import re
from KspCalc import parts as partLib

TIMES_RE = re.compile(r"^\s*(\d+)\s*x\s+", re.I)

class Rocket(object):

    parts = name = stages = None

    def __init__(self, parts, name=None):
        self.name = name or "Unknown rocket."
        self.parts = [part() for part in parts]
        self.stages = []

    def appendStage(self, stage):
        self.stages.append(stage)

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
