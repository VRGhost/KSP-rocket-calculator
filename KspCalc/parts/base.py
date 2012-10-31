from . import consts

class Part(object):
    """Basic part."""

    name = None
    isEngine = property(lambda s: False)
    isFuelTank = property(lambda s: False)

    def __init__(self, parent):
        super(Part, self).__init__()
        self.rocket = parent
        
        typeDict = type(self).__dict__
        for (name, value) in typeDict.items():
            try:
                instanciate = value.instanciate
            except AttributeError:
                continue
            setattr(self, name, instanciate(self))

    @property
    def weight(self):
        return self.rocket.position.g * self.mass

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

class Weight(Part):

    mass = None # kg

    def __repr__(self):
        return "<{} {!r} {}kg>".format(self.__class__.__name__, self.name, self.mass)

class _FuelElement(Part):
    """Element that is related to fuel consumption or carriage."""

    def kgToLitres(self, val):
        return val * consts.FUEL_RHO

    def litresToKg(self, val):
        return val / consts.FUEL_RHO

class FuelTank(_FuelElement):

    massEmpty = None # kg
    massFull = None # kg
    fuelL = None # litres

    fuelKg = property(lambda s: s.litresToKg(s.fuelL))
    mass = property(lambda s: s.massEmpty + s.fuelKg)

    isFuelTank = property(lambda s: True)
    empty = property(lambda s: s.fuelL < 1e-6)

    def __init__(self, *args, **kwargs):
        super(FuelTank, self).__init__(*args, **kwargs)
        fuelDensity = float(self.fuelL) / (self.massFull - self.massEmpty)
        assert abs(fuelDensity - consts.FUEL_RHO) < 1e-5, "Fuel is expected to have constant density"
        assert self.mass == self.massFull

    def consumeL(self, maxAmount):
        amount = min(self.fuelL, maxAmount)
        self.fuelL -= amount
        return (maxAmount - amount)

    def consumeKg(self, maxAmount):
        return self.litresToKg(self.consumeL(self.kgToLitres(maxAmount)))

    def __repr__(self):
        return "<{} mass=({}, {})kg fuel={}L>".format(
            self.__class__.__name__, self.massEmpty, self.massFull, self.fuelL)


class LFE(_FuelElement):
    """Liquid Fuel Engine."""

    isEngine = property(lambda s: True)

    thrust = None # N
    consumptionL = None # L/s
    consumptionKg = property(lambda s: s.litresToKg(s.consumptionL.val)) # Kg/s
    Isp = property(lambda s: s.thrust / (s.consumptionKg * s.rocket.position.g)) # s

    @property
    def twRatio(self):
        return self.thrust / self.weight

class AtmDependant(object):
    """Parameter that is dependant from the atmospheric pressure.
    (instance object).

    """

    def __init__(self, atm, vac, parent):
        super(AtmDependant, self).__init__()
        self.atm = atm
        self.vac = vac
        self.parent = parent

    @property
    def val(self):
        pressure = self.parent.rocket.position.pressure
        delta = self.atm - self.vac
        return self.vac + delta * pressure

class AtmDependantCls(object):
    """Parameter that is dependant from the atmospheric pressure.

    This is dummy object to be used in class objects. Gets automatically replaced with an instance
    of `instanceCls' by parent class.
    """

    __slots__ = ("atm", "vac")
    instanceCls = AtmDependant

    def __init__(self, atm, vac):
        super(AtmDependantCls, self).__init__()
        self.atm = atm
        self.vac = vac

    def instanciate(self, parent):
        return self.instanceCls(parent=parent, atm=self.atm, vac=self.vac)