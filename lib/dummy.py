import random

class Dummy:
    '''A dummy class for representing a serial device'''
    def __init__(self, ping, pong, motors = 5, sensors = 3):
        self.ping = ping
        self.pong = pong
        self.config = b''
        self.motors = motors
        self.sensors = sensors
        self.output_buffer = b''

        self.config += self.pong.to_bytes(4, 'little')
        self.config += (32000).to_bytes(2, 'little')
        self.config += (2000).to_bytes(2, 'little')
        self.config += motors.to_bytes(1, 'little')
        self.config += sensors.to_bytes(1, 'little')
        for i in range(motors):
            self.config += f'Dummy Motor {i+1}\x00'.encode()
        
        for i in range(sensors):
            self.config += f'Dummy Sensor {i}\x00?\x00'.encode()

    def read(self):
        if len(self.output_buffer) > 0:
            msg = self.output_buffer[0:1]
            self.output_buffer = self.output_buffer[1:]
            return msg
        return b''

    def write(self, cmd):
        if int.from_bytes(cmd, 'little') == self.ping:
            self.output_buffer += self.config
        if int.from_bytes(cmd[2:4], 'little') == 77:
            self.output_buffer += self.gen_sensor_info()

    def reset_input_buffer(self):
        return

    def gen_sensor_info(self):
        msg = b''
        for s in range(self.sensors):
            msg += random.randint(-1000, 1000).to_bytes(4, 'little', signed = True)
        return msg