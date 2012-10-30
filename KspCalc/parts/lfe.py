from .base import LFE

class Lv909(LFE):

    name = "LV-909 Liquid Fuel Engine"

    mass = 0.5 * 1000
    thrust = 50 * 1000
    consumptionAtm = 3.4
    consumptionVac = 2.6
    IspAtm = 300
    IspVac = 390

ALL = (Lv909, )
