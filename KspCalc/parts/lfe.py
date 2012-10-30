from .base import (LFE, AtmDependantCls)

class Lv909(LFE):

    name = "LV-909 Liquid Fuel Engine"

    mass = 0.5 * 1000
    thrust = 50 * 1000
    consumptionL = AtmDependantCls(atm=3.4, vac=2.6)

ALL = (Lv909, )
