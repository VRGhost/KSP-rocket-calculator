"""Dead weights library."""

from .base import Weight

class PodMk1(Weight):

    name = "Command Pod Mk1"
    mass = 0.8 * 1000

class Mk16Parachute(Weight):

    name = "Mk16 Parachute"
    mass = 0.1 * 1000

class Tr18A(Weight):

    name = "TR-18A Stack Decoupler"
    mass = 0.05 * 1000

class LT2_1(Weight):

    name = "LT-2(1) Landing Strut"
    mass = 0.005 * 1000

class TVR_1180C(Weight):

    name = "TVR-1180C Mk1 Stack Tri-Coupler"
    mass = 0.3 * 1000

class AdvSAS(Weight):

    name = "Advanced S.A.S. Module"
    mass = 0.8 * 1000

ALL = (PodMk1, Mk16Parachute, Tr18A, LT2_1, TVR_1180C, AdvSAS)
