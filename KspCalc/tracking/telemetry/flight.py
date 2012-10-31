from .base import (TelemetryCollector, Telemetry)

class Flight(TelemetryCollector):
    """Flight telementry collector."""

    name = "FlightTelemetry"

    massDelta = Telemetry(lambda old, msg: old + msg.consumedKg)

    startTime = Telemetry(lambda old, msg: msg.absTime if old is None else old, init=None)
    time = Telemetry(lambda old, msg: max(old, msg.absTime))
    maxAlt = Telemetry(lambda old, msg: max(old, msg.rocket.position.surfaceAltitude))

    @Telemetry(init=None)
    def minTw(old, msg):
        new = msg.thrustToWeightRatio
        if old is None:
            rv = new
        else:
            rv = min(old, new)
        return rv

class StageSeparation(TelemetryCollector):
    
    name = "StageSeparation"

    time = Telemetry(lambda old, msg: msg.absTime)
    stageName = Telemetry(lambda old, msg: msg.stage.name)