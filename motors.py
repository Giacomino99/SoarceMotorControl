from dataclasses import dataclass, field
from collections import defaultdict

ARG_BYTES = 16
ARG_MAX = 2**(ARG_BYTES - 1) - 1
ARG_MIN = -1 * 2**(ARG_BYTES - 1)

@dataclass
class Operation:
    op: str
    code: int
    out: callable = lambda m, a: v
    updater: callable = lambda m, v: v

    def do_op(self, motor, arg = 0):
        info_s = self.out(motor, arg)
        self.updater(motor, arg)
        return info_s

OPS = {
    'on': Operation('on', 1, 
        lambda m, a = 0: f'Turning on {m.name}', 
        lambda m, v: m.set_state(True)),
    'off': Operation('off', 2, 
        lambda m, a = 0: f'Turning off {m.name}', 
        lambda m, v: m.set_state(False)),
    'sss': Operation('sss', 3, 
        lambda m, a = 0: f'Chaning speed of {m.name} to {a}', 
        lambda m, v: m.set_speed(v)),
    'fwd': Operation('fwd', 4, 
        lambda m, a = 0: f'Spinning {m.name} forward', 
        lambda m, v: m.set_direction(True)),
    'bkwd': Operation('bkwd', 5, 
        lambda m, a = 0: f'Spinning {m.name} backward', 
        lambda m, v: m.set_direction(False)),
    'line': Operation('line', 6, 
        lambda m, a = 0: f'{m.name} set to linear mode' if m.linear else f'{m.name} set to normal mode', 
        lambda m, v: m.set_linear(not m.linear)),
    'zero': Operation('zero', 7, 
        lambda m, a = 0: f'{m.name} zero position set'),
    'max': Operation('max', 8, 
        lambda m, a = 0: f'{m.name} maximum position set'),
    'step': Operation('step', 9, 
        lambda m, a = 0: f'{m.name} moving {a} steps'),
    'speed': Operation('speed', 10, 
        lambda m, a = 0: f'{m.name} maximum speed is now {a} steps/sec', 
        lambda m, v: m.set_max_speed(v)),
    'accel': Operation('accel', 11, 
        lambda m, a = 0: f'{m.name} acceleration set to {a}', 
        lambda m, v: m.set_accel(v)),
    'go': Operation('go', 12, 
        lambda m, a = 0: f'{m.name} linear motion toggled', 
        lambda m, v: m.set_go(not m.go)),
}

SPECIAL_OPS = {
    'state': Operation('state', 69),
    'disconnect': Operation('disconnect', 42)
}

@dataclass
class Motor:

    selected = 0
    motors = {}

    def __init__(self, name, symbol, internal,
        state = False, direction = True, speed = 0, accel = 2000, max_speed = 32000,
        linear = False, go = False, bindings = []):

        self.name = name
        self.symbol = symbol
        self.internal = internal

        self.state = state
        self.direction = direction
        self.speed = speed
        self.accel = accel
        self.max_speed = max_speed

        self.linear = linear
        self.go = go
        self.bindings = []

        Motor.motors[self.symbol] = self
        if not Motor.selected is Motor: Motor.selected = self

    def execute(self, cmd, arg = 0, safe = True):
        # Speed command without real command
        if cmd.isdigit():
            arg = int(cmd)
            cmd = 'sss'

        # Constrain arg to 16 bit
        arg = Motor.constrain(arg)

        # Not real op
        if cmd not in OPS:
            return b'', f'Command "{self.symbol} {cmd} {arg}" is not a valid command.'

        # Safe stoping for linear motors
        if safe and self.state and self.linear:
            if (self.go and cmd == 'off') or (not self.go and cmd == 'on'):
                cmd = 'go'

        info_s = OPS[cmd].do_op(self, arg)

        # Execute command for bindings
        m_num = self.internal
        for m in self.bindings:
            gbg, binfo_s = m.execute(cmd, arg, safe)
            m_num += m.internal
            info_s += '\n'
            info_s += binfo_s

        m_code = Motor.gen_control(m_num, OPS[cmd].code, arg)

        return m_code, info_s

    def serial_execute(self, serial, cmd, arg = 0, safe = True):
        m_code, info_s = self.execute(cmd, arg, safe)
        serial.write(m_code)
        return m_code, info_s

    def set_state(self, val):
        self.state = val
        if not self.state:
            self.go = False

    def set_direction(self, val):
        self.direction = val

    def set_speed(self, val):
        self.speed = val

    def set_linear(self, val):
        self.linear = val
        self.go = False

    def set_go(self, val):
        if self.linear and self.state:
            self.go = val
        else:
            self.go = False

    def set_accel(self, val):
        self.accel = val

    def set_max_speed(self, val):
        self.max_speed = val

    def bind(self, other):
        self.bindings.append(other)

    def unbind(self):
        self.bindings = []

    def to_dict(self):
        full = {}
        full['state'] = self.state
        full['direction'] = self.direction
        full['speed'] = self.speed
        full['accel'] = self.accel
        full['max_speed'] = self.max_speed
        full['linear'] = self.linear
        return full

    @classmethod
    def select(cls, m = 0):
        cls.selected = m

    @classmethod
    def motor_lines(self):
        return len(Motor.motors)*7

    @classmethod
    def execute_all(cls, cmd, arg = 0, safe = True):
        # Speed command without real command
        if cmd.isdigit():
            arg = int(cmd)
            cmd = 'sss'

        arg = Motor.constrain(arg)

        if cmd not in OPS:
            return b'', f'Command "all {cmd} {arg}" is not a valid command.'

        info_s = ''
        m_code = bytes(0)
        m_nums = 0
        for m in cls.motors:
            nm_code, ninfo_s = cls.motors[m].execute(cmd, arg, safe)
            if cls.motors[m].linear:
                m_code += nm_code
            else:
                m_nums += cls.motors[m].internal
            info_s += ninfo_s
            info_s += '\n'

        m_code += Motor.gen_control(m_nums, OPS[cmd].code, arg)
        return m_code, info_s[:-1]

    @classmethod
    def serial_execute_all(cls, serial, cmd, arg = 0, safe = True):
        arg = Motor.constrain(arg)
        m_code, info_s = cls.execute_all(cmd, arg, safe)
        serial.write(m_code)
        return m_code, info_s

    @classmethod
    def bind(cls, m1, m2):
        cls.motors[m2].unbind()
        cls.motors[m1].bind(cls.motors[m2])
        return f'{cls.motors[m1].name} bound to {cls.motors[m2].name}'

    @classmethod
    def special_serial_execute(cls, serial, cmd, arg = 0):
        arg = Motor.constrain(arg)
        if cmd not in SPECIAL_OPS:
            return b''

        m_code = m_code = Motor.gen_control(0, SPECIAL_OPS[cmd].code, arg)
        serial.write(m_code)
        return m_code

    @classmethod
    def constrain(cls, arg):
        return max(min(ARG_MAX, arg), ARG_MIN)

    @classmethod
    def gen_control(cls, m_num, op_code, arg):
        # Why cast to int? Because it is a float... Why is it a float? I don't know...
        m_code = int(m_num).to_bytes(2, 'little') + op_code.to_bytes(2, 'little') + arg.to_bytes(2, byteorder='little', signed=True)
        return m_code

    def __eq__(self, other):
        return self.name == other.name and self.symbol == other.symbol and self.internal == other.internal

    def __str__(self):
        s = f'{self.name}:' + (' *' if self == Motor.selected else '') + '\n'
        s += f'   Symbol: {self.symbol}\n'
        s += f'   Speed: {self.speed}\n'
        s += '   Direction: ' + ('Linear' if self.linear else ('Forward' if self.direction else 'Backward')) + '\n'
        s += f'   Acceleration: {self.accel}\n'
        s += f'   Max Speed: {self.max_speed}\n'
        return s

@dataclass
class Sensor:

    sensors = []

    def __init__(self, name, unit = '', value = 0, fmt = lambda s: s):
        self.name = name
        self.value = value
        self.unit = unit
        self.fmt = fmt

        Sensor.sensors.append(self)

    def get_value(self):
        return self.fmt(self.value)

    @classmethod
    def sensor_lines(self):
        return len(Sensor.sensors)*3

    def __str__(self):
        s = f'{self.name}:\n   {self.get_value()} {self.unit}'
        return s