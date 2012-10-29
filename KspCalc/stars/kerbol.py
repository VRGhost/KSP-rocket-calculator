from . import base

def BuildSystem():
    sun = base.Star("Kerbol", radius=261600000, mass=1.756567E+28)

    kerbin = base.Celestial("Kerbin", radius=600000, mass=5.2915793E+22)
    sun.addSatellite(kerbin, ap=13599840256, pe=13599840256, period=9203544.6)

    mun = base.Celestial("Mun", radius=200000, mass=9.7600236E+20)
    kerbin.addSatellite(mun, ap=12000000, pe=12000000, period=138984.38)

    return sun
