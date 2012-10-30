import math

from KspCalc import consts

def memorised(func):
    """Caching property."""
    def _wrapper(self):
        cacheKey =  "__{}_cache".format(func.__name__)
        try:
            return getattr(self, cacheKey)
        except AttributeError:
            rv = func(self)
            setattr(self, cacheKey, rv)
            return rv

    return property(_wrapper)

class Celestial(object):
    """Basic Celestial object."""

    radius = None # in metres
    mass = None # in Kg
    name = None
    _onOrbit = None
    _childrenOrbits = None
    hasAtmosphere = property(lambda s: False)

    def __init__(self, name, radius, mass):
        self.name = name
        self.radius = radius
        self.mass = mass
        self._childrenOrbits = []

    def addSatellite(self, satellite, **orbitParams):
        return Orbit(self, satellite, **orbitParams)

    def addChildOrbit(self, orbit):
        self._childrenOrbits.append(orbit)
        return orbit

    def g(self, distance):
        return consts.G * self.mass / (distance**2)

    def findOne(self, name):
        rv = tuple(self.find(name))
        
        if not rv:
            raise Exception("No {!r} found".format(name))
        elif len(rv) > 1:
            raise Exception("More than one {!r} found".format(name))

        return rv[0]

    def find(self, name):
        if self.name == name:
            yield self
        for el in self.satellites:
            for rv in el.find(name):
                yield rv

    @property
    def satellites(self):
        return (orb.satellite for orb in self._childrenOrbits)

    @property
    def onOrbit(self):
        return self._onOrbit

    @onOrbit.setter
    def onOrbit(self, val):
        if self._onOrbit:
            raise Exception("{} is Already on the orbit {}".fromat(self, self._onOrbit))
        self._onOrbit = val

    @memorised
    def surfaceGravity(self):
        return self.g(self.radius)

    @memorised
    def escapeVelocity(self):
        return math.sqrt(2 * consts.G * self.mass / self.radius)

    @memorised
    def semiMajorAxis(self):
        return self.onOrbit.semiMajorAxis

    @memorised
    def sphereOfInfluence(self):
        return self.onOrbit.sphereOfInfluence

    def __repr__(self):
        return "<{} {!r} r={!r} m={!r}>".format(self.__class__.__name__, self.name, self.radius, self.mass)

class Star(Celestial):
    """Star. """
    pass

class CelestialWithAtmosphere(Celestial):
    """A Celestial object with atmosphere."""

    hasAtmosphere = property(lambda s: True)

    def __init__(self, pressure, *args, **kwargs):
        """
            Pressure is expected to be a formula that given the altitude bove gound (in metres) returns pressure in atmospheres.
        """
        super(CelestialWithAtmosphere, self).__init__(*args, **kwargs)
        self.pressureAboveGround = pressure

    def pressureAt(self, altitude):
        """Pressure with altitude measured to the centre of a planet."""
        return self.pressureAboveGround(altitude - self.radius)

class Orbit(object):

    ap = pe = None # metres
    period = None # seconds
    centre = satellite = None

    def __init__(self, centre, satellite, ap, pe, period):
        self.ap = ap
        self.pe = pe
        self.centre = centre
        self.satellite = satellite
        centre.addChildOrbit(self)
        satellite.onOrbit = self

    @memorised
    def semiMajorAxis(self):
        return (self.ap + self.pe) / 2

    @memorised
    def sphereOfInfluence(self):
        return self.semiMajorAxis * ((self.satellite.mass / self.centre.mass) ** (2.0 / 5))
