import os
import sys
import yaml
import argparse

# Add local package to the path
sys.path.append(os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..")))

from KspCalc.stars import Kerbol
from KspCalc.rocket import Rocket
from KspCalc import astrodynamics

def yaml_file(fname):
    return yaml.load(open(fname))

def space_pos(txt):
    vals = {}
    for el in txt.split(':'):
        try:
            (name, value) = el.split('=')
        except:
             raise argparse.ArgumentTypeError("Unable to parse {!r} part of {!r}".format(el, txt))
        vals[name] = value

    planet = Kerbol.findOne(vals["planet"])
    alt = float(vals["alt"]) + planet.radius
    return astrodynamics.Point(planet, alt)

def get_parser():
    parser = argparse.ArgumentParser(description="Ksp calculator.")
    parser.add_argument("--rocket", type=yaml_file, required=True, help="Rocket design to be used.")
    parser.add_argument("--start", type=space_pos, required=False, default="planet=Kerbin:alt=0.0",
            help="Start position. You have to define planets' name and altitude (in metres).")
    return parser

if __name__ == "__main__":

    args = get_parser().parse_args()
    rocket = Rocket.fromDict(args.rocket)
    rocket.setPos(args.start)

    for el in rocket.fly():
        print(el.rocket.speed)