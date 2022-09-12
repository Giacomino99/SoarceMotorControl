#!/usr/bin/python3
'''
TODO: less crashing
update info when data availibe and remove timer
'''
# Needed external libraries
import curses
from dataclasses import dataclass, field
from collections import defaultdict
import serial
import serial.tools.list_ports
import random
import time
import smtplib
import multiprocessing
import json

# Custom Libraries
from lib.motors import *
from lib.windows import *
from lib.dummy import *
from lib.logos import *

from config import *

f_key = lambda n: print_out(execute_motors(app.motors[n].symbol, 'off' \
            if (app.motors[n].state and not app.motors[n].linear) \
            or (app.motors[n].linear and app.motors[n].go) else 'on'))

KEY_BINDS = [ 
    Key_Binding(curses.KEY_F1, lambda: f_key(0)),
    Key_Binding(curses.KEY_F2, lambda: f_key(1)),
    Key_Binding(curses.KEY_F3, lambda: f_key(2)),
    Key_Binding(curses.KEY_F4, lambda: f_key(3)),
    Key_Binding(curses.KEY_F5, lambda: Motor.select(app.motors[0])),
    Key_Binding(curses.KEY_F6, lambda: Motor.select(app.motors[1])),
    Key_Binding(curses.KEY_F7, lambda: Motor.select(app.motors[2])),
    Key_Binding(curses.KEY_F8, lambda: Motor.select(app.motors[3])),
    Key_Binding(curses.KEY_F9, lambda: print_out(execute_motors('all', 'on'))),
    Key_Binding(curses.KEY_F10, lambda: print_out(execute_motors('all', 'off'))),
    Key_Binding(curses.KEY_F12, lambda: print_out(execute_motors('all', 'off', safe = False))),
    Key_Binding(ord(']'), lambda: print_out(execute_motors(Motor.selected.symbol, 
        str(Motor.selected.speed + 10)))),
    Key_Binding(ord('['), lambda: print_out(execute_motors(Motor.selected.symbol, 
        str(max(0, Motor.selected.speed - 10))))),
]

@dataclass
class APP:
    output_win: int
    info_win: int
    command_win: int
    stdscr: int
    motors: int = 0
    sensors: int = 0
    device: int = 0

app = APP(0, 0, 0, 0)
history = ['']
timer = time.time()
select = 0

# Eww yucky long bad
def setup():
    print_out('Welcome to the Soarce™ control software!\nAttempting to find controller...\n')
    curses.doupdate()
    spin_wait(0.2, lock = True)

    for device in AUTO_DEVICE:
        ports = list(serial.tools.list_ports.grep(device))
        if len(ports) == 1:
            break
    x = 0
    if len(ports) == 1:
        print_out(f'Found device: {ports[0]}\n')
        curses.doupdate()

    elif TEST_MODE:
        print_out('YOU ARE IN TEST MODE!!\nNO COMMANDS WILL BE SENT TO ANY CONTROLLER!!\n', color = 1)
        print_out('Creating a dummy serial device...')

    else:
        print_out('Controller could not be identified')
        ports = list(serial.tools.list_ports.comports())
        if len(ports) == 0:
            print_out('Could not find any devices (is it plugged in?)\n'
                +'Press any key to exit :(')
            curses.doupdate()
            spin_exit()

        print_out('\nPlease select the controller manually:')
        while True:
            for i in range(len(ports)):
                print_out(f'{i}: {ports[i]}', 4)
            while not handle_user():
                curses.doupdate()
                continue
            x = s_to_i(app.command_win.get_command())
            if x in range(len(ports)):
                break
            print_out('\nInvalid selection, please select the controler:')

    try:
        print_out('Connecting to controller...')
        
        if TEST_MODE:
            arduino = Dummy(PING, PONG, 5, 3)
        else:
            arduino = serial.Serial(port=ports[x].device, baudrate=115200, timeout = 0, parity = 'N', stopbits = 1, bytesize = 8)
    except Exception as e:
        print_out(''.join([
            'Could not establish connection...',
            'Is another program already using that port?\n',
            'The actual error was:',
            str(e),
            '\nPress any key to exit...'
        ]))
        curses.doupdate()
        spin_exit()

    app.device = arduino
    print_out('Conencted!\n')
    print_out('Attempting Handshake:\n')
    curses.doupdate()

    for i in range(10):
        arduino.write(PING.to_bytes(4, 'little'))
        print_out('Ping...', 3)
        curses.doupdate()

        spin_wait(0.1, lock = True)
        config = read_until()

        try:
            pong = int.from_bytes(config[:4], 'little')
        except Exception as e:
            pong = ''
            print_out('Invalid response...', 3)
            curses.doupdate()

        if pong == PONG:
            print_out('Pong...\n', 3)
            print_out('Connection established with controller')
            return config

        else:
            read_until()
            spin_wait(0.4, lock = True)

    print_out('Could not connect to controller (is it plugged in?)\nPress any key to exit :(')
    print_out('If it is plugged in: please unplug and replug the controller')
    spin_exit()

def intro_animation():
    print_out(' ')
    l_num = len(app.output_win.full_out)

    for l in LOGO.splitlines():
        print_out(['   ' + l], color = [2])

    print_out(' ')    

    for i in range(8):
        curses.init_pair(i+10, GRADIENT[i], -1)

    mat = TEXT.splitlines()

    x = len(LOGO.splitlines()[0]) + 6
    y = 2

    for i in range(l_num, l_num + len(mat)):
        app.output_win.full_out[i].append(' ')
        app.output_win.out_colors[i].append(10 + i - l_num)

    for i in range(len(mat[0])):
        for j in range(len(mat)):
            app.output_win.full_out[l_num + j][1] += mat[j][i]
            app.output_win.safty_check()
            app.output_win.draw()

        time.sleep(0.015)
        app.output_win.noutrefresh()
        curses.doupdate()

    if BOLBI_TIME:
        slap_and_clap()

# TODO: DON'T CRASH WITH RESIZE
def slap_and_clap():
    bolbis = BOLBI.splitlines()
    if curses.COLS - INFO_WIN_WIDTH - 3 < len(bolbis[0]):
        print_out('No room for Bolbi :(')
        return
    x_pos = (curses.COLS - INFO_WIN_WIDTH - len(bolbis[0]))//2
    bolbi_win = curses.newpad(len(bolbis)+3, len(bolbis[0])+1)
    bolbi_win.addstr(2, 0, BOLBI)
    for i in range(len(bolbis)):
        bolbi_win.refresh(0, 0, curses.LINES - COMMAND_WIN_HEIGHT - i - 2, x_pos, curses.LINES - COMMAND_WIN_HEIGHT - 2, x_pos + len(bolbis[0]))
        time.sleep(0.04)
    time.sleep(0.5)
    bolbi_win.addstr(0, 0, 'IT\'S ME BOLBI STROGANOVSKY!')
    bolbi_win.refresh(0, 0, curses.LINES - COMMAND_WIN_HEIGHT - i - 2, x_pos, curses.LINES - COMMAND_WIN_HEIGHT - 2, x_pos + len(bolbis[0]))
    time.sleep(1)
    bolbi_win.addstr(1, 0, 'SLAP SLAP SLAP! CLAP CLAP CLAP!')
    bolbi_win.refresh(0, 0, curses.LINES - COMMAND_WIN_HEIGHT - i - 2, x_pos, curses.LINES - COMMAND_WIN_HEIGHT - 2, x_pos + len(bolbis[0]))
    time.sleep(1)
    bolbi_win.move(0,0)
    bolbi_win.clrtoeol()
    bolbi_win.move(1,0)
    bolbi_win.clrtoeol()
    time.sleep(0.5)

    for i in range(len(bolbis) -1 , 0, -1):
        app.output_win.noutrefresh()
        curses.doupdate()
        bolbi_win.refresh(0, 0, curses.LINES - COMMAND_WIN_HEIGHT - i - 2, x_pos, curses.LINES - COMMAND_WIN_HEIGHT - 2, x_pos + len(bolbis[0]))
        time.sleep(0.04)

    app.output_win.noutrefresh()

def init_curses(stdscr):
    # Init Colors
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_YELLOW, -1)
    curses.init_pair(5, curses.COLOR_CYAN, -1)
    curses.init_pair(8, curses.COLOR_BLACK, -1)
    curses.init_pair(9, curses.COLOR_WHITE, -1)

    curses.init_pair(69, 202, -1)

    # Init app data sctucture
    app.stdscr = stdscr
    app.stdscr.attron(curses.color_pair(2))
    app.stdscr.encoding = 'utf_8'

    app.output_win = Output_Window(stdscr = stdscr, 
        p_height = curses.LINES + 100, p_width = curses.COLS + 100,
        resize_y = lambda std: 0, 
        resize_x = lambda std: 0,
        resize_height = lambda std: std.getmaxyx()[0] - COMMAND_WIN_HEIGHT, 
        resize_width = lambda std: std.getmaxyx()[1] - INFO_WIN_WIDTH,
        color = 2, pad = True, name = 'Y', margin = 1)
    app.output_win.init_out()

    app.info_win = Info_Window(stdscr = stdscr,
        resize_y = lambda std: 0, 
        resize_x = lambda std: std.getmaxyx()[1] - INFO_WIN_WIDTH,
        resize_height = lambda std: std.getmaxyx()[0], 
        resize_width = lambda std: INFO_WIN_WIDTH,
        color = 5, pad = False, name = 'X')
    app.info_win.init_info()
    app.info_win.set_timer(UPDATE_INTERVAL)
    app.info_win.border()

    app.command_win = Command_Window(stdscr = stdscr, 
        resize_y = lambda std: std.getmaxyx()[0] - 3, 
        resize_x = lambda std: 0,
        resize_height = lambda std: 3, 
        resize_width = lambda std: std.getmaxyx()[1] - INFO_WIN_WIDTH,
        color = 3, pad = False, name = 'Z')
    app.command_win.init_command(kb = KEY_BINDS)
    app.command_win.border()

    app.output_win.noutrefresh()
    app.info_win.noutrefresh()
    app.command_win.noutrefresh()

    curses.doupdate()
    return

def init_perif(config):
    motors = []
    sensors = []

    m_conf = []
    s_conf = []

    config = config[4:]
    d_max = int.from_bytes(config[0:2], 'little')
    d_accel = int.from_bytes(config[2:4], 'little')
    num_motor = config[4]
    num_sensor = config[5]
    config = config[6:]

    for m in range(num_motor):
        x = config.index(b'\x00')
        name = config[:x].decode('utf-8')
        motors.append(Motor(name = name, symbol = 'm'+str(m+1), internal = 2**(m)))
        config = config[x+1:]

    for s in range(num_sensor):
        x = config.index(b'\x00')
        name = config[:x].decode('utf-8')
        config = config[x+1:]
        x = config.index(b'\x00')
        unit = config[:x].decode('utf-8')
        sensors.append(Sensor(name = name, unit = unit))
        config = config[x+1:]

    if len(config) >= 4 and int.from_bytes(config, 'little'):
        while(read_until() == b''):
            continue
        Motor.special_serial_execute(app.device, 'state')
        print_out('Controller already running, getting config\n')
        curses.doupdate()
        time.sleep(0.4)
        live_state = read_until(b'')
        print_out(live_state)
        # [state - 1 byte][dir - 1 byte][linear - 1 byte][go - 1 byte]
        # [speed - 2bytes][accel - 2 bytes][max_speed - 2 bytes]
        for i, m in enumerate(motors):
            m.state = bool(live_state[0 + i*10])
            m.direction = bool(live_state[1 + i*10])
            m.linear = bool(live_state[2 + i*10])
            m.go = bool(live_state[3 + i*10])
            
            m.speed = int.from_bytes(live_state[4 + i*10:6 + i*10], 'little')
            m.accel = int.from_bytes(live_state[6 + i*10:8 + i*10], 'little')
            m.max_speed = int.from_bytes(live_state[8 + i*10:10 + i*10], 'little')

    app.motors = motors
    app.sensors = sensors

    app.info_win.init_info(motors, sensors)

    return motors, sensors

# Safe string to int, return -1 if operation failed
def s_to_i(s):
    try:
        return int(s)
    except:
        return -1

# Exit after key press
def spin_exit():
    curses.doupdate()
    while app.command_win.win.getch() == -1:
        pass
    nice_exit(-1)

def read_until(term = b''):
    msg = bytes(0)
    i = app.device.read()
    n = 0
    while i != term and i != b'' and n < 1000:
        msg += i
        i = app.device.read()
        n += 1
    app.device.reset_input_buffer()
    return msg + i

# Handle all user input, return True if command ready
def handle_user():
    return app.command_win.handle_user()

def print_out(msg, off = 0, color = 2):
    # log(msg)
    app.output_win.print_out(msg, off, color = color)
    return

def draw_info(now = False):
    if app.info_win.check_time(rst = False):
        update_sensor_data()
    app.info_win.draw(now)

def save_state(name):
    if '..' in name or '/' in name or '\\' in name:
        return 'How about we don\'t do that. Ok? Ok...'

    ss = {}
    for m in app.motors:
        ss[m.symbol] = m.to_dict()
    try:
        f = open('states/' + name, 'w')
        json.dump(ss, f)
        f.close()
        return f'State saved as "{name}"'
    except:
        return 'Failed to save state'

def load_state(name):
    try:
        f = open(f'states/{name}', 'r')
    except:
        return f'Unable to open state "{name}"'
    
    ss = json.load(f)

    for m in ss:
        mtr = Motor.motors[m]
        # Turn off linear first to stop on from toggling motiion
        # mtr.serial_execute(app.device, 'line' if  mtr.linear else '')

        mtr.serial_execute(app.device, 'on' if ss[m]['state'] and not mtr.state else '')
        mtr.serial_execute(app.device, 'off' if not ss[m]['state'] and mtr.state else '', safe = False)
        mtr.serial_execute(app.device, 'fwd' if ss[m]['direction'] else 'bkwd')
        mtr.serial_execute(app.device, 'sss', ss[m]['speed'])
        mtr.serial_execute(app.device, 'accel', ss[m]['accel'])
        mtr.serial_execute(app.device, 'speed', ss[m]['max_speed'])
        mtr.serial_execute(app.device, 'line' if (ss[m]['linear'] and not mtr.linear) or (not ss[m]['linear'] and mtr.linear) else '')
    return 'State Loaded'

def update_sensor_data():
    if app.device == 0 or app.sensors == 0:
        return

    Motor.special_serial_execute(app.device, 'sensor')
    stream = read_until()
    if stream != b'' and len(stream) == len(app.sensors)*4:
        for i in range(len(app.sensors)):
            app.sensors[i].value = int.from_bytes(stream[i*4:(i+1)*4], byteorder='little', signed=True)

def send_help():
    print_out('Enter the symbol of the motor, then the command you wish to execute')
    sym = ['all']
    for m in app.motors:
        sym.append(m.symbol)
    sym[0] = '['+sym[0]
    sym[-1] = sym[-1]+']'
    print_out('Availivle Motors:', color = 9)
    print_out(', '.join(sym), off = 4, color = 9)
    print_out(HELP, color = 9)

# runs async
def message(cmds):
    if cmds[1].lower() in NUMBERS:
        try:
            server = smtplib.SMTP(SMTP_ADDRESS, SMTP_PORT)
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, NUMBERS[cmds[1].lower()], ' '.join(cmds[2:]))
        except:
            return

def log(msg):
    f = open('log', 'a')
    f.write(str(msg) + '\n')
    f.close()

def run_script(file):
    try:
        f = open(file)
    except:
        print_out(f'Unable to open file "{file}"')
        return

    print_out(f'Running script {file}, Press any key to stop execution...', color = 69)
    for line in f.read().splitlines():
        s_line = line.split(' ')
        if s_line[0].lower() == 'wait':
            if len(s_line) < 2:
                continue
            print_out('<< ' + f'Waiting for {s_line[1]} seconds', color = 69)
            curses.doupdate()
            if not spin_wait(s_to_i(s_line[1])):
                break
        else:
            print_out('<< ' + execute_motors(*line.split(' ')).replace('\n', '\n<< '), color = 69)
        curses.doupdate()
    f.close()
    print_out('Execution finished')
    return

# TODO: DON'T CRASH WITH RESIZE
def spin_wait(dur, lock = False):
    t = time.time()
    while time.time() < t + dur:
        app.command_win.safty_check()
        if app.command_win.win.getch() != -1 and not lock:
            return False
        else:
            draw_info()
    return True

def execute_motors(m_sym, op, arg = 0, safe = True):
    if m_sym == 'all':
        arg = s_to_i(arg)
        m_code, info_s = Motor.serial_execute_all(app.device, op, arg, safe)
        if TEST_MODE: print_out(m_code) 
        return info_s

    if m_sym in Motor.motors:
        if op == 'bind' and arg in Motor.motors:
            return Motor.bind(m_sym, arg)
        elif op == 'unbind':
            Motor.motors[m_sym].unbind()
            return f'{Motor.motors[m_sym].name} bindings removed'
        else:
            arg = s_to_i(arg)
            m_code, info_s = Motor.motors[m_sym].serial_execute(app.device, op, arg, safe = safe)
            print_out(m_code)
            # time.sleep(.05)
            # msg = read_until()
            # print_out(msg)
            return info_s

    return f'Command "{m_sym} {op} {arg}" is not a valid command.'

def execute_command():
    cmd = app.command_win.get_command()
    print_out(MARKER + cmd)
    split_command = cmd.split(' ')
    split_command.extend(['\b', '\b', '\b'])
    a0, a1, a2, *_ = split_command
    if 'help' in a0:
        send_help()
    elif 'logo' in a0:
        print_out(LOGO, off = 3)
    elif 'crashcrashcrash' in a0:
        x = 1/0
    elif 'splash' in a0:
        intro_animation()
    elif 'bolbi' in a0:
        slap_and_clap()
    elif a0 == 'exec':
        try:
            run_script(a1)
        except:
            print_out('Bad script format')
    elif a0 == 'save':
        print_out(save_state(a1))
    elif a0 == 'load':
        print_out(load_state(a1))
    elif a0 == 'message':
        multiprocessing.active_children() # Joins all complete threads
        multiprocessing.Process(target = message, args = (split_command,)).start()
    else: 
        print_out(execute_motors(a0, a1, a2))
        draw_info(True)

def nice_exit(code = 0, qt = True):
    if app.device == 0:
        exit(code)
    Motor.special_serial_execute(app.device, 'disconnect')
    read_until()
    read_until() 
    read_until()
    print('Exited Safely')
    if qt:
        exit(code) 

# Main function
def main(stdscr):
    init_curses(stdscr)
    intro_animation()
    init_perif(setup())
    print_out('Start inputing commands:\n')
    draw_info(now = True),
    while True:
        draw_info()
        if handle_user():
            execute_command()
            draw_info(True)
        curses.doupdate()

if __name__ == '__main__':
    curses.wrapper(main)
    # try:
    #     curses.wrapper(main)
    # except Exception as e:
    #     if e == KeyboardInterrupt:
    #         nice_exit()
    #     else:
    #         nice_exit()
    #         raise(e)
    # finally:
    #     nice_exit(qt = False)