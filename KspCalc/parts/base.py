class Part(object):
    """Basic part."""

    name = None
    isEngine = property(lambda s: False)
    isFuelTank = property(lambda s: False)

    def __init__(self, rocket):
        super(Part, self).__init__()
        self.rocket = rocket

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

class Weight(Part):

    mass = None # kg

    def __repr__(self):
        return "<{} {!r} {}kg>".format(self.__class__.__name__, self.name, self.mass)

class FuelTank(Part):

    massEmpty = None # kg
    massFull = None # kg
    fuel = None # litres

    isFuelTank = property(lambda s: True)

    def __init__(self, *args, **kwargs):
        super(FuelTank, self).__init__(*args, **kwargs)
        self._fuelDensity = float(self.fuel) / (self.massFull - self.massEmpty)

    def consume(self, maxAmount):
        amount = max(self.fuel, maxAmount)
        self.fuel -= amount
        return amount

    @property
    def mass(self):
        return self.massEmpty + self.fuelMass

    @property
    def fuelMass(self):
        return self.fuel * self._fuelDensity

    def __repr__(self):
        return "<{} mass=({}, {})kg fuel={}>".format(
            self.__class__.__name__, self.massEmpty, self.massFull, self.fuel)

class LFE(Part):
    """Liquid Fuel Engine."""

    isEngine = property(lambda s: True)

    thrust = None # N
    consumptionAtm = None # Litre/s
    consumptionVac = None # L/s
    IspAtm = None # seconds
    IspVac = None # seconds

    @property
    def effectiveThrust(self):
        return self.rocket.thrustRate * self.thrust

    @property
    def twRatio(self):
        return self.thrust / (self.weight * self.rocket.position.g)

    @property
    def twRatioEffective(self):
        return (self.thrust * self.rocket.thrustRate) / (self.weight * self.rocket.position.g)
