import os
import sys
import yaml
import argparse

# Add local package to the path
sys.path.append(os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..")))

from KspCalc import (
    stars, flight, tracking
)

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

    planet = stars.Kerbol.findOne(vals["planet"])
    alt = float(vals["alt"]) + planet.radius
    return flight.Point(planet, alt)

def get_parser():
    parser = argparse.ArgumentParser(description="Ksp calculator.")
    parser.add_argument("--rocket", type=yaml_file, required=True, help="Rocket design to be used.")
    parser.add_argument("--start", type=space_pos, required=False, default="planet=Kerbin:alt=68.41",
            help="Start position. You have to define planets' name and altitude (in metres).")
    subp = parser.add_subparsers(help="Run mode")
    drag = subp.add_parser("guess_drag", help="Guess drag coefficient for the rocket")
    drag.add_argument("--terminal_altitude", type=float, required=True, help="Terminal altitude rocket had")
    drag.add_argument("--terminal_time", type=float, required=True, help="Time (seconds) at which given measurements were made")
    drag.set_defaults(mode="guessDrag")
    return parser

def guess_drag(rocket, time, alt):
    maxFound = False
    minDrag = 0
    maxDrag = 100.0
    dragEpsilon = 0.005

    getMiddle = lambda: ((maxDrag - minDrag) / 2.0) + minDrag

    while (maxDrag - minDrag) > dragEpsilon:
        toTest = getMiddle()
        iterRocket = rocket.copy()
        iterRocket.drag = toTest
        tracker = tracking.Tracker(
            iterRocket, reportFreq=0.2, reportWindows=[(time, time + 1)])
        tracker.launch()
        alts = [msg["maxAlt"] for msg in tracker.track()]
        iterAlt = sum(alts) / (1.0 * len(alts))
        
        if iterAlt > alt:
            minDrag = toTest
            if not maxFound:
                maxDrag *= 2
        elif iterAlt < alt:
            maxDrag = toTest
            maxFound = True
        print(minDrag, maxDrag)

    print("Estimated drag: {}".format(getMiddle()))
    return getMiddle()


if __name__ == "__main__":

    args = get_parser().parse_args()
    rocket = flight.Rocket.fromDict(args.rocket)
    rocket.setPos(args.start)

    mode = getattr(args, "mode", None)
    if mode == "guessDrag":
        guess_drag(rocket, args.terminal_time, args.terminal_altitude)
    else:
        tracker = tracking.Tracker(rocket, reportFreq=10, dt=0.01)
        tracker.launch()

        for log in tracker.track():
            print(log)
