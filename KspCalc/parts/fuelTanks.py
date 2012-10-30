from .base import FuelTank

class FlT200(FuelTank):

    name = "FL-T200 Fuel Tank"
    massEmpty = 0.125 * 1000
    massFull = 1.125 * 1000
    fuelL = 200


ALL = (FlT200, )
