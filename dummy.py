import random

class Dummy:
    '''A dummy class for representing a serial device'''
    def __init__(self, ping, pong, motors = 5, sensors = 3):
        self.ping = (str(ping).encode() + b'\n')
        self.pong = pong
        self.last_in = b''
        self.config = str(self.pong).encode()
        self.motors = motors
        self.sensors = sensors
        self.output_buffer = b''
        for i in range(motors):
            self.config += f';DM{i},Dummy Motor {i+1}'.encode()
        self.config += b'&'
        for i in range(sensors):
            self.config += f';{i},?,Dummy Sensor {i}'.encode()
        self.config += b'\n'

    def read(self):
        if len(self.output_buffer) > 0:
            msg = self.output_buffer[0:1]
            self.output_buffer = self.output_buffer[1:]
            return msg
        else:
            self.output_buffer = self.gen_sensor_info()
            return b''

    def write(self, cmd):
        if cmd == self.ping:
            self.output_buffer += self.config

    def reset_input_buffer(self):
        return

    def gen_sensor_info(self):
        msg = b''
        for s in range(self.sensors):
            msg += f';{s}{random.randint(0, 1000)}'.encode()
        msg += b'\n'
        return msg