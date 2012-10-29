class Point(object):
    """Point in space."""

    def __init__(self, planet, altitude):
        self.planet = planet
        self.altitude = altitude

    @property
    def g(self):
        return self.planet.g(self.altitude)
