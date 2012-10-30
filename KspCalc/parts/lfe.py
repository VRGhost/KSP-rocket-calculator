from .base import (LFE, AtmDependantCls)


class LvT30(LFE):

    name = "LV-T30 Liquid Fuel Engine"

    mass = 1.25 * 1000
    thrust = 215 * 1000
    consumptionL = AtmDependantCls(atm=13.7, vac=11.8)

class LvT45(LFE):

    name = "LV-T45 Liquid Fuel Engine"

    mass = 1.5 * 1000
    thrust = 200 * 1000
    consumptionL = AtmDependantCls(atm=12.7, vac=11.0)

class Lv909(LFE):

    name = "LV-909 Liquid Fuel Engine"

    mass = 0.5 * 1000
    thrust = 50 * 1000
    consumptionL = AtmDependantCls(atm=3.4, vac=2.6)

ALL = (Lv909, LvT45, LvT30)
