class Telemetry(object):
    """Abstract telemetry field."""

    rv = None
    _func = None
    _activated = False
    fields = {
        "init": 0,
        "rv": None,
    }

    def __init__(self, *args, **kwargs):
        super(Telemetry, self).__init__()
        self.fields = self.fields.copy()
        self._setProps(args, kwargs)
        
    def __call__(self, *args, **kwargs):
        """Invoked When using extended decorator syntax."""
        self._setProps(args, kwargs)
        return self

    def _setProps(self, args, kwargs):
        assert not self._activated
        if args:
            assert len(args) == 1
            assert callable(args[0])
            assert not self._func
            self._func = args[0]
        for (name, value) in kwargs.items():
            if name not in self.fields:
                raise Exception("Unknown field {!r}. Known fields are: {}".format(name, tuple(self.fields.keys())))
            self.fields[name] = value

    def collect(self, data):
        assert self._func
        if not self._activated:
            self.activate()
        self.rv = self._func(self.rv, data)

    def getValue(self):
        rvFn = self.fields["rv"]
        rv = self.rv
        if callable(rvFn):
            rv = rvFn(rv)
        return rv

    def activate(self):
        self._activated = True
        init = self.fields["init"]
        if callable(init):
            init = init()
        self.rv = init

    def copy(self):
        cls = type(self)
        return cls(self._func, **self.fields)

class TelemetryCollector(object):
    """An object that collects telemetry of a rocket."""

    _fields = _fieldDict = None
    name = "UNNAMED TELEMETRY"

    def __init__(self, rocket):
        super(TelemetryCollector, self).__init__()
        self.rocket = rocket
        _fields = {}
        for name, value in self.__class__.__dict__.items():
            if isinstance(value, Telemetry):
                # Copy telemetry object to prevent taining it with current data
                _fields[name] = value.copy()


        self._fields = tuple(_fields.values())
        self._fieldPairs = tuple(_fields.items())

    def accumulate(self, data):
        for field in self._fields:
            field.collect(data)

    def getData(self):
        rv = dict((name, fld.getValue()) for (name, fld) in self._fieldPairs)
        rv["telemetryType"] = self.name
        return rv