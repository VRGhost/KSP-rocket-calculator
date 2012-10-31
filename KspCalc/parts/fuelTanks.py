from .base import FuelTank

class FlT200(FuelTank):

    name = "FL-T200 Fuel Tank"
    massEmpty = 0.125 * 1000
    massFull = 1.125 * 1000
    fuelL = 200

class FlT400(FuelTank):

    name = "FL-T400 Fuel Tank"
    massEmpty = 0.25 * 1000
    massFull = 2.25 * 1000
    fuelL = 400

class X200_16(FuelTank):

    name = "Rockomax X200-16 Fuel Tank"
    massEmpty = 1 * 1000
    massFull = 9 * 1000
    fuelL = 1600

class X200_32(FuelTank):

    name = "Rockomax X200-32 Fuel Tank"
    massEmpty = 2 * 1000
    massFull = 18 * 1000
    fuelL = 3200

ALL = (FlT200, FlT400, X200_16, X200_32)
