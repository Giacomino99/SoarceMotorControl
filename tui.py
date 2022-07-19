#!/usr/bin/python3

import curses
# from curses.textpad import Textbox, rectangle
from dataclasses import dataclass
import serial
import serial.tools.list_ports
import random
import time
import smtplib
import multiprocessing
# from playsound import playsound

from logos import *
from dummy import Dummy
from config import *


'''
app: Input, Output, Info, std

Functions: print_out, draw_info, user_input
'''
TEST_MODE = True
BOLBI_TIME = False

INFO_WIN_WIDTH = 30
COMMAND_WIN_HEIGHT = 3
EDGE = 1
PING = 0XABADBABE
PONG = 0XB16B00B5
AUTO_DEVICE = 'arduino'
MARKER = '>> '
UPDATE_INTERVAL = 0.5

GRADIENT = [39, 38, 45, 44, 43, 42, 41, 40]

@dataclass
class APP:
    output_win: int
    info_win: int
    command_win: int
    stdscr: int
    motors: int
    sensors: int
    device: int

@dataclass
class motor:
    name: str
    symbol: str
    internal: str
    speed: float
    direction: bool
    state: bool

@dataclass
class sensor:
    name: str
    internal: str
    value: float
    unit: str

app = APP(0, 0, 0, 0, 0, 0, 0)
history = ['']
idx = 0
cmd = ''
timer = time.time

# Eww yucky long bad
def setup():
    print_out('Welcome to the Soarce™ control software!\n'+ 
        'Attempting to find controller...\n')
    curses.doupdate()
    time.sleep(0.2)

    ports = list(serial.tools.list_ports.grep(AUTO_DEVICE))

    global cmd
    x = 0
    if len(ports) == 1:
        print_out(f'Found device: {ports[0]}\n')
        curses.doupdate()
    elif TEST_MODE:
        app.output_win.attron(curses.color_pair(1))
        print_out('YOU ARE IN TEST MODE!!\nNO COMMANDS WILL BE SENT TO ANY CONTROLLER!!\n')
        app.output_win.attron(curses.color_pair(2))
        print_out('Creating a dummy serial device...')
    else:
        print_out('Controller could not be identified')
        ports = list(serial.tools.list_ports.comports())
        curses.doupdate()
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
            x = s_to_i(cmd)
            cmd = ''
            if x in range(len(ports)):
                break
            print_out('\nInvalid selection, please select the controler:')

    try:
        print_out('Connecting to controller...')
        curses.doupdate()
        if TEST_MODE:
            arduino = Dummy(PING, PONG, 5, 1)
        else:
            arduino = serial.Serial(port=ports[x].device, baudrate=19200, timeout = 0, parity = 'N', stopbits = 1, bytesize = 8)
        app.device = arduino
        print_out('Attempting Handshake:\n')
        curses.doupdate()
        for i in range(10):
            arduino.write(str(PING).encode() + b'\n')
            print_out('Ping...', 3)
            curses.doupdate()
            time.sleep(0.5)
            try:
                pong = read_until().decode('utf-8')
            except Exception as e:
                # raise(e)
                pong = ''
                print_out('Invalid response...', 3)
                curses.doupdate()
            if s_to_i(pong.split(';')[0]) == PONG:
                print_out('Pong...\n', 3)
                break

            if i == 9:
                print_out('Could not connect to controller (is it plugged in?)\nPress any key to exit :(')
                spin_exit()

        print_out('Connection established with controller')
        print_out('Start inputing commands:\n')
        return pong

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

def read_until(term = b'\n'):
    msg = b''
    i = app.device.read()
    n = 0
    while i != term and i != b'' and n < 1000:
        msg += i
        i = app.device.read()
        n += 1
    app.device.reset_input_buffer()
    return msg + i

def intro_animation():
    print_out(' ')
    print_out(LOGO, 3)
    for i in range(8):
        curses.init_pair(i+10, GRADIENT[i], -1)
    mat = TEXT.splitlines()
    x = len(LOGO.splitlines()[0]) + 6
    y = 2
    for i in range(-4, len(mat[0])):
        for j in range(len(mat)):
            if j < len(mat) and i+j < len(mat[0]) and x+i+j < app.output_win.getmaxyx()[1] - 1:
                app.output_win.addch(y+j, x+i+j, mat[j][i+j], curses.color_pair(j+10))
        time.sleep(0.01)
        app.output_win.noutrefresh(1, 1, 1, 1, curses.LINES - COMMAND_WIN_HEIGHT - 2, curses.COLS - INFO_WIN_WIDTH - 2)
        curses.doupdate()
    app.output_win.move(len(mat) + 3, EDGE)

    if BOLBI_TIME:
        slap_and_clap()

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
    # playsound('slapclap.wav')
    time.sleep(1)
    bolbi_win.move(0,0)
    bolbi_win.clrtoeol()
    bolbi_win.move(1,0)
    bolbi_win.clrtoeol()
    time.sleep(0.5)

    for i in range(len(bolbis) -1 , 0, -1):
        app.output_win.noutrefresh(1, 1, 1, 1, curses.LINES - COMMAND_WIN_HEIGHT - 2, curses.COLS - INFO_WIN_WIDTH - 2)
        curses.doupdate()
        bolbi_win.refresh(0, 0, curses.LINES - COMMAND_WIN_HEIGHT - i - 2, x_pos, curses.LINES - COMMAND_WIN_HEIGHT - 2, x_pos + len(bolbis[0]))
        time.sleep(0.04)

    rectangle(app.stdscr, 0, 0, curses.LINES - COMMAND_WIN_HEIGHT - 1, curses.COLS - INFO_WIN_WIDTH - 1)
    app.output_win.noutrefresh(1, 1, 1, 1, curses.LINES - COMMAND_WIN_HEIGHT - 2, curses.COLS - INFO_WIN_WIDTH - 2)

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

    # Init app
    app.stdscr = stdscr
    app.stdscr.attron(curses.color_pair(2))
    app.stdscr.encoding = 'utf_8'

    app.output_win = curses.newpad(curses.LINES, max(curses.COLS, 128))
    app.output_win.attron(curses.color_pair(2))
    app.output_win.encoding = 'utf-8'
    rectangle(app.stdscr, 0, 0, curses.LINES - COMMAND_WIN_HEIGHT - 1, curses.COLS - INFO_WIN_WIDTH - 1)
    app.output_win.leaveok(True)

    app.info_win = curses.newwin(curses.LINES, INFO_WIN_WIDTH, 0, curses.COLS - INFO_WIN_WIDTH)
    app.info_win.attron(curses.color_pair(5))
    app.info_win.encoding = 'utf-8'
    app.info_win.border()
    app.info_win.leaveok(True)

    app.command_win = curses.newwin(COMMAND_WIN_HEIGHT, curses.COLS - INFO_WIN_WIDTH, curses.LINES - COMMAND_WIN_HEIGHT, 0)
    app.command_win.attron(curses.color_pair(3))
    app.command_win.encoding = 'utf-8'
    app.command_win.border()
    app.command_win.nodelay(True)
    app.command_win.keypad(True)

    app.output_win.move(1,1)
    app.command_win.move(1,1)

    app.output_win.noutrefresh(1, 1, 1, 1, curses.LINES - COMMAND_WIN_HEIGHT - 2, curses.COLS - INFO_WIN_WIDTH - 2)
    app.info_win.noutrefresh()
    app.command_win.noutrefresh()

    curses.doupdate()
    return

def init_perif(config):
    motors = []
    sensors = []

    m_conf = []
    s_conf = []

    config = config.split('\n')[0].split('&')
    if len(config) >= 2:
        m_conf = config[0].split(';')
        s_conf = config[1].split(';')

    for m in range(1,len(m_conf)):
        info = m_conf[m].split(',')
        motors.append(motor(info[1], 'm'+str(m), info[0], 0, True, False))

    for s in range(1,len(s_conf)):
        info = s_conf[s].split(',')
        sensors.append(sensor(info[2], info[0], 0, info[1]))

    app.motors = motors
    app.sensors = sensors

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
    while app.command_win.getch() == -1:
        pass
    exit(-1)

# Handle all user input, return True if command ready
def handle_user():
    y, x = app.command_win.getyx()
    app.command_win.move(y, x)

    c = app.command_win.getch()
    if c == -1:
        return False

    global idx
    global cmd
    
    if c == curses.KEY_ENTER or c == 10 or c == 13:
        history.insert(0, cmd)
        app.command_win.move(1,1)
        app.command_win.clrtoeol()
        app.command_win.border()
        idx = -1
        if cmd == 'exit':
            exit(0)
        return True

    elif c == curses.KEY_BACKSPACE or c == 8 or c == 127:
        cmd = cmd[:-1]

    elif c == curses.KEY_UP:
        if idx < len(history) - 1:
            idx += 1
        cmd = history[idx]

    elif c == curses.KEY_DOWN:
        if idx >= 0:
            idx -= 1

        if idx == -1:
            cmd = ''
        else:
            cmd = history[idx]

    elif c == curses.KEY_F1:
        exit(0)

    elif c == curses.KEY_RESIZE:
        handle_resize()

    elif c < 255:
        cmd += chr(c)

    # Inefficient but... meh... (it is clean :])
    app.command_win.move(1, 1)
    app.command_win.clrtoeol()
    app.command_win.addnstr(cmd, app.command_win.getmaxyx()[1] - 3, curses.color_pair(9))
    app.command_win.border()
    app.command_win.noutrefresh()
    return False

def handle_resize():
    dont_crash()
    new_y, new_x = app.stdscr.getmaxyx()
    curses.resize_term(new_y, new_x)

    out_y, out_x = app.output_win.getmaxyx()
    if new_y > out_y or new_x > out_x:
        app.output_win.resize(curses.LINES, curses.COLS)

    app.info_win.resize(curses.LINES, INFO_WIN_WIDTH)
    app.info_win.mvwin(0, curses.COLS - INFO_WIN_WIDTH)
    app.command_win.resize(COMMAND_WIN_HEIGHT, curses.COLS - INFO_WIN_WIDTH)
    app.command_win.mvwin(curses.LINES - COMMAND_WIN_HEIGHT, 0)

    app.stdscr.clear()
    rectangle(app.stdscr, 0, 0, curses.LINES - COMMAND_WIN_HEIGHT - 1, curses.COLS - INFO_WIN_WIDTH - 1)
   
    if type(app.motors) != type(0):
        draw_info(True)

    app.output_win.noutrefresh(1, 1, 1, 1, curses.LINES - COMMAND_WIN_HEIGHT - 2, curses.COLS - INFO_WIN_WIDTH - 2)
    app.info_win.noutrefresh()
    app.command_win.noutrefresh()
    app.stdscr.noutrefresh()

def print_out(msg, off = 0):
    if type(msg) == type([]):
        msg = ' '.join(msg)
    else:
        msg = str(msg)

    lines = msg.splitlines()
    if len(msg) > 0 and msg[-1] == '\n':
        lines.append('')
    y, x = app.output_win.getyx()
    if len(lines) == 0:
        app.output_win.move(y+1, EDGE)
        return
    max_x = app.output_win.getmaxyx()[1]
    max_y = curses.LINES - COMMAND_WIN_HEIGHT 
    for line in lines:
        if y >= max_y - 1:
            app.output_win.move(1, 1)
            app.output_win.deleteln()
            app.output_win.move(max_y - 2, EDGE)
            app.output_win.clrtoeol()
            app.output_win.move(max_y - 2, x)
            app.output_win.addnstr(max_y - 2, x + off, line, max_x - 2)
        else:
            app.output_win.addnstr(y, x + off, line, max_x - 2)
            y += 1
            app.output_win.move(y, x + off)

    rectangle(app.stdscr, 0, 0, curses.LINES - COMMAND_WIN_HEIGHT - 1, curses.COLS - INFO_WIN_WIDTH - 1)
    app.output_win.move(y, EDGE)
    app.output_win.noutrefresh(1, 1, 1, 1, curses.LINES - COMMAND_WIN_HEIGHT - 2, curses.COLS - INFO_WIN_WIDTH - 2)
    return

def draw_info(now = False):
    global timer
    if not (now or time.time() - timer > UPDATE_INTERVAL):
        return

    app.info_win.erase()
    app.info_win.move(1,1)
    y = 1
    for m in app.motors:
        if y + 5 >= app.info_win.getmaxyx()[0] - len(app.sensors) * 3 + 1:
            break
        app.info_win.attron(curses.color_pair(2)) if m.state else app.info_win.attron(curses.color_pair(1))
        app.info_win.addnstr(y, 1, f'{m.name}:', INFO_WIN_WIDTH - 2)
        app.info_win.addnstr(y+1, 4, f'Symbol: {m.symbol}', INFO_WIN_WIDTH - 2)
        app.info_win.addnstr(y+2, 4, f'Speed: {m.speed}', INFO_WIN_WIDTH - 2)
        app.info_win.addnstr(y+3, 4, f'Direction: ' + ('Forward' if m.direction else 'Backward'), INFO_WIN_WIDTH - 2)
        # app.info_win.addnstr(y+4, 4, f'Enabled: {m.state}', INFO_WIN_WIDTH - 2)
        app.info_win.attron(curses.color_pair(5))
        app.info_win.hline(y+4, 1, curses.ACS_HLINE, INFO_WIN_WIDTH - 2)
        y += 5

    if curses.LINES - (len(app.motors)*5 + len(app.sensors)*3 + 4) > 8:
        app.info_win.attron(curses.color_pair(2))
        for i, l in enumerate(LOGO.splitlines()):
            app.info_win.addstr((len(app.motors)*5) + ((curses.LINES - (len(app.sensors)*3) - (len(app.motors)*5) - 8)//2) + i, (INFO_WIN_WIDTH - 2 - 18)//2, l)
        app.info_win.attron(curses.color_pair(5))

    y = curses.LINES - 1 - len(app.sensors)*3
    app.info_win.move(max(0, curses.LINES - 1 - len(app.sensors)*3), 1)
    for s in app.sensors:
        if y + 3 >= app.info_win.getmaxyx()[0]:
            break
        update_sensor_data()
        app.info_win.hline(y, 1, curses.ACS_HLINE, INFO_WIN_WIDTH - 2)
        app.info_win.attron(curses.color_pair(4))
        app.info_win.addnstr(y+1, 1, f'{s.name}:', INFO_WIN_WIDTH)
        app.info_win.addnstr(y+2, 4, f'{s.value} {s.unit}', INFO_WIN_WIDTH)
        app.info_win.attron(curses.color_pair(5))
        y += 3

    timer = time.time()
    app.info_win.border()
    app.info_win.noutrefresh()

def update_sensor_data():
    stream = read_until()

    if stream != b'':
        stream = stream.decode().split(';')
        for data in stream:
            for i, s in enumerate(app.sensors):
                if len(data) > 0 and data[0] == s.internal:
                    try:
                        app.sensors[i].value = float(data[1:])
                    except Exception:
                        app.sensors[i].value = -1

def send_help():
    print_out('Enter the symbol of the motor, then the command you wish to execute')
    sym = ['all']
    for m in app.motors:
        sym.append(m.symbol)
    sym[0] = '['+sym[0]
    sym[-1] = sym[-1]+']'
    print_out('Availivle Motors:')
    print_out(', '.join(sym), 5)
    print_out(HELP)

# runs async
def message(cmds):
    if cmds[1].lower() in NUMBERS:
        try:
            server = smtplib.SMTP('mail.supremecluster.com', 25)
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, NUMBERS[cmds[1].lower()], ' '.join(cmds[2:]))
        except:
            return

def run_script(file):
    try:
        f = open(file)
    except:
        print_out(f'Unable to open file "{file}"')
        return

    app.output_win.attron(curses.color_pair(69))
    print_out(f'Running script {file}, Press any key to stop execution...')
    for line in f.read().splitlines():
        s_line = line.split(' ')
        if s_line[0].lower() == 'wait':
            if len(s_line) < 2:
                continue
            print_out('<< ' + f'Waiting for {s_line[1]} seconds')
            curses.doupdate()
            if not spin_wait(s_to_i(s_line[1])):
                break
        else:
            print_out('<< ' + execute_motors(line.split(' ')).replace('\n', '\n<< '))
        curses.doupdate()
    f.close()
    app.output_win.attron(curses.color_pair(2))
    print_out('Execution finished')
    return

def spin_wait(dur):
    t = time.time()
    while time.time() < t + dur:
        if app.command_win.getch() != -1:
            return False
        else:
            draw_info()
    return True

def execute_motors(split_command):
    if split_command[0] == 'all':
        out = []
        for m in app.motors:
            split_command[0] = m.symbol
            out.extend(execute_motors(split_command))
            out.append('\n')
        return ''.join(out[:-1])

    for i, m in enumerate(app.motors):
        if m.symbol == split_command[0]:
            cmd = b''
            if split_command[1] == 'off':
                cmd = bytes(m.internal + '-4\n', 'utf-8')
                app.motors[i].state = False
                app.device.write(cmd)
                return f'Turning off {m.name}'

            elif split_command[1] == 'on':
                cmd = bytes(m.internal + '-1\n', 'utf-8')
                app.motors[i].state = True
                app.device.write(cmd)
                return f'Turning on {m.name}'

            elif split_command[1] == 'fwd':
                cmd = bytes(m.internal + '-2\n', 'utf-8')
                app.motors[i].direction = True
                app.device.write(cmd)
                return f'Spinning {m.name} forward'

            elif split_command[1] == 'bkwd':
                cmd = bytes(m.internal + '-3\n', 'utf-8')
                app.motors[i].direction = False
                app.device.write(cmd)
                return f'Spinning {m.name} backward'

            elif split_command[1].isdigit():
                cmd = bytes(m.internal+split_command[1]+'\n', 'utf-8')
                app.motors[i].speed = s_to_i(split_command[1])
                app.device.write(cmd)
                return f'Changing speed of {m.name} to {split_command[1]}'
    split_command = ' '.join(split_command)
    return f'Command "{split_command}" is not a valid command.'

def execute_command():
    global cmd
    print_out(MARKER + cmd)
    split_command = cmd.split(' ')
    if 'help' in split_command:
        send_help()
    elif 'logo' in split_command:
        print_out(LOGO)
    elif 'splash' in split_command:
        print_out(SPLASH)
    elif 'bolbi' in split_command:
        slap_and_clap()
    elif len(split_command) >= 2:
        if split_command[0] == 'exec':
            run_script(split_command[1])
        elif len(split_command) >= 3 and split_command[0] == 'message':
            multiprocessing.active_children() # Joins all complete threads
            multiprocessing.Process(target = message, args = (split_command,)).start()
        else: 
            print_out(execute_motors(split_command))
            draw_info(True)
    else:
        print_out(f'Command "{cmd}" is not a valid command.')
    cmd = ''
    return

def dont_crash():
    y, x = app.stdscr.getmaxyx()
    while x < INFO_WIN_WIDTH + 3 or y < len(app.sensors)*3+1:
        y, x = app.stdscr.getmaxyx()
        app.stdscr.erase()
        app.stdscr.addnstr(0, 0, f'WINDOW TOO SMALL {x}, {y} :(', x - 1)
        app.stdscr.noutrefresh()
        curses.doupdate()
        if app.command_win.getch() == curses.KEY_F1:
            exit(0)

def rectangle(win, uly, ulx, lry, lrx, ch = None):
    if ch == None:
        win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
        win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
        win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
        win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
        win.addch(uly, ulx, curses.ACS_ULCORNER)
        win.addch(uly, lrx, curses.ACS_URCORNER)
        win.addch(lry, lrx, curses.ACS_LRCORNER)
        win.addch(lry, ulx, curses.ACS_LLCORNER)
    else:
        win.vline(uly+1, ulx, ch, lry - uly - 1)
        win.hline(uly, ulx+1, ch, lrx - ulx - 1)
        win.hline(lry, ulx+1, ch, lrx - ulx - 1)
        win.vline(uly+1, lrx, ch, lry - uly - 1)
        win.addch(uly, ulx, ch)
        win.addch(uly, lrx, ch)
        win.addch(lry, lrx, ch)
        win.addch(lry, ulx, ch)
    win.noutrefresh()

def main(stdscr):
    init_curses(stdscr)
    intro_animation()
    init_perif(setup())

    draw_info(now = True),
    while True:
        if handle_user():
            draw_info(True)
            execute_command()
        draw_info()
        curses.doupdate()

if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        exit(0)