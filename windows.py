import curses
from dataclasses import dataclass, field
import time
import random

from motors import *
from logos import *

@dataclass
class Key_Binding:
    key: int
    command: callable

@dataclass
class Window:
    
    windows = {}
    win_count = 0
    crash = False

    def __init__(self, stdscr, p_height = None, p_width = None, 
        resize_y = lambda std: 0, 
        resize_x = lambda std: 0, 
        resize_height = lambda std: std.getmaxyx()[0], 
        resize_width = lambda std: std.getmaxyx()[1], 
        pad = False, border_win = None, margin = 1, name = None, color = 0):

        # If: pad, auto borderwin :)

        self.stdscr = stdscr
        self.pad = pad
        self.y = resize_y(stdscr)
        self.x = resize_x(stdscr)
        self.height = resize_height(stdscr)
        self.width = resize_width(stdscr)
        self.color = color
        self.name = name if name else f'Win{Window.win_count}'

        if pad:
            self.win = curses.newpad(p_height, p_width)
            border_win = Border_Window(stdscr = stdscr, 
                resize_y = lambda std: 0, 
                resize_x = lambda std: 0,
                resize_height = lambda std: std.getmaxyx()[0] - 3, 
                resize_width = lambda std: std.getmaxyx()[1] - 30,
                color = 2, pad = False, name = 'Bw' + self.name)
        else:
            self.win = curses.newwin(self.height, self.width, self.y, self.x)

        self.win.attron(curses.color_pair(color))
        self.win.encoding = 'utf-8'
        self.win.leaveok(True)
        self.win.nodelay(True)
        self.win.keypad(True)

        self.border_win = border_win if border_win != None else self
        self.p_height = p_height if p_height else self.height 
        self.p_width = p_width if p_width else self.width
        self.margin = margin

        self.resize_height = resize_height
        self.resize_width = resize_width
        self.resize_y = resize_y
        self.resize_x = resize_x

        Window.windows[self.name] = self
        Window.win_count += 1

    def draw(self, now = True):
        return

    def border(self):
        if self.border_win != self:
            self.rectangle(self.border_win.win, 0, 0, self.height - 1, self.width - 1)
        else:
            self.win.border()

    def rectangle(self, win, uly, ulx, lry, lrx, ch = None):
        win.attron(curses.color_pair(self.color))
        if ch == None:
            win.vline(uly+1, ulx, curses.ACS_VLINE, lry - uly - 1)
            win.hline(uly, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
            win.hline(lry, ulx+1, curses.ACS_HLINE, lrx - ulx - 1)
            win.vline(uly+1, lrx, curses.ACS_VLINE, lry - uly - 1)
            win.addch(uly, ulx, curses.ACS_ULCORNER)
            win.addch(uly, lrx, curses.ACS_URCORNER)
            # addch bottom right corner raises error but actually works...?
            try:
                win.addch(lry, lrx, curses.ACS_LRCORNER)
            except:
                pass
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
        self.noutrefresh()

    def noutrefresh(self):
        if isinstance(self, Border_Window):
            return

        if self.pad:
            if self != self.border_win:
                self.border_win.win.noutrefresh()
                self.win.noutrefresh(0 + self.margin, 0 + self.margin, self.y + self.margin, self.x + self.margin, self.y + self.height - 1 - self.margin, self.x + self.width - 1 - self.margin)
            else:
                self.win.noutrefresh(0, 0, self.y, self.x, self.y + self.height - 1, self.x + self.width - 1)
        else:
            self.win.noutrefresh()

    def resize(self):
        self.dont_crash()

        self.y, self.x, self.height, self.width = self.get_new_yxhw()
        if not self.pad:
            self.win.resize(self.height, self.width)
            self.p_height, self.p_width = self.height, self.width
            self.win.mvwin(self.y, self.x)
        else:
            max_y, max_x = self.stdscr.getmaxyx()
            if self.p_height < max_y or self.p_width < max_x:
                self.win.resize(max_y + 10, max_x + 10)
                self.p_height, self.p_width = max_y + 10, max_x + 10

        self.draw(now = True)
        self.noutrefresh()

    def dont_crash(self):
        max_y, max_x = self.stdscr.getmaxyx()
        curses.resize_term(max_y, max_x)
        new_y, new_x, new_h, new_w = self.get_new_yxhw()

        while ((new_x > max_x or new_x < 0) or (new_y > max_y or new_y < 0) or 
            (new_w + new_x > max_x or new_w < 3) or (new_h + new_y > max_y or new_h < 3)):

            Window.crash = True
            max_y, max_x = self.stdscr.getmaxyx()
            curses.resize_term(max_y, max_x)
            new_y, new_x, new_h, new_w = self.get_new_yxhw()
            # self.stdscr.erase()
            self.stdscr.addnstr(0, 0, f'WINDOW {self.name} TOO SMALL {max_x}, {max_y} :(', max_x - 1)
            self.stdscr.addnstr(1, 0, f'x:{new_x}, y:{new_y}, w:{new_w}, h:{new_h}', max_x - 1)
            self.stdscr.noutrefresh()
            curses.doupdate()

    @classmethod
    def resize_all(cls, x = 0, y = 0, z = 0):
        for w in cls.windows:
            cls.windows[w].resize()
        if cls.crash:
            cls.crash = False
            cls.resize_all()
        curses.doupdate()

    @classmethod
    def draw_all(cls, now = True):
        for w in cls.windows:
            cls.windows[w].draw(now = now)
        curses.doupdate()

    def get_new_yxhw(self):
        new_y = self.resize_y(self.stdscr)
        new_x = self.resize_x(self.stdscr)
        new_h = self.resize_height(self.stdscr)
        new_w = self.resize_width(self.stdscr)

        return new_y, new_x, new_h, new_w

    def leaveok(self, val):
        self.win.leaveok(val)

    def keypad(self, val):
        self.keypad(val)

    def nodelay(self, val):
        self.nodelay(val)

    def reset_pos(self):
        self.win.move(self.margin, self.margin)

    def addnstrnl(self, s, x_off = 0, color = None, nl = True):
        cy, cx = self.win.getyx()
        if not color: color = self.color
        for l in s.splitlines():
            if cy >= self.height - 1:
                return
            self.win.addnstr(cy, max(cx, self.margin) + x_off, l, self.width - self.margin - cx, curses.color_pair(color))
            cy += 1

        if nl:
            self.win.move(cy, self.margin)

    def hlinenl(self, ch, n):
        cy, cx = self.win.getyx()
        if cy >= self.height - 1:
            return
        self.win.hline(cy, self.margin, ch, n)
        self.win.move(cy+1, self.margin)

    def safty_check(self):
        c = self.win.getch()
        if c == curses.KEY_RESIZE:
            Window.resize_all()
        elif c != -1:
            curses.ungetch(c)

class Info_Window(Window):

    def init_info(self, motors = [], sensors = [], off = 1, on = 2, s = 4):
        self.motors = motors
        self.sensors = sensors
        self.on_color = on
        self.off_color = off
        self.sensor_color = s

    def set_timer(self, interval):
        self.timer = time.time()
        self.interval = interval

    def check_time(self):
        if time.time() - self.timer > self.interval:
            self.timer = time.time()
            return True
        return False

    def draw(self, now = False):
        if not self.check_time() and not now:
            return

        self.win.erase()
        self.reset_pos()

        for m in self.motors:
            if self.win.getyx()[0] + 5 + len(self.sensors)*3 + self.margin > self.height:
                break 
            color = (self.off_color if not m.state else (self.sensor_color if (m.linear and not m.go) else self.on_color))
            self.addnstrnl(str(m), color = color)
            self.hlinenl(curses.ACS_HLINE, self.width - self.margin*2)

        if self.height - (Motor.motor_lines() + Sensor.sensor_lines() + 4) > 8:
            self.win.move(Motor.motor_lines() + (self.height - Sensor.sensor_lines() - Motor.motor_lines() - len(LOGO.splitlines()))//2, self.margin)
            for l in LOGO.splitlines():
                self.addnstrnl(l, (self.width - len(l) - self.margin*2) // 2, self.on_color)

        try:
            self.win.move(self.height - len(self.sensors)*3 - self.margin, self.margin)
        except:
            self.border()
            return

        for s in self.sensors:
            if self.win.getyx()[0] + 3 + self.margin > self.height:
                break 
            self.hlinenl(curses.ACS_HLINE, self.width - self.margin*2)
            self.addnstrnl(str(s), color = self.sensor_color)

        self.border()
        self.noutrefresh()

class Command_Window(Window):

    def init_command(self, text = 9, kb = []):
        self.cmd = ''
        self.idx = 0
        self.history = ['']
        self.text_color = text
        self.win.leaveok(False)
        self.win.move(self.margin, self.margin)
        self.key_bindings = kb

    def handle_user(self):

        c = self.win.getch()
        if c == -1:
            self.noutrefresh()
            return False

        if c == curses.KEY_ENTER or c == 10 or c == 13:
            self.history.insert(0, self.cmd)
            self.win.move(self.margin,self.margin)
            self.win.clrtoeol()
            self.border()
            self.idx = -1
            if self.cmd == 'exit':
                exit(0)
            return True

        elif c == curses.KEY_BACKSPACE or c == 8 or c == 127:
            self.cmd = self.cmd[:-1]

        elif c == curses.KEY_UP:
            if self.idx < len(self.history) - 1:
                self.idx += 1
            self.cmd = self.history[self.idx]

        elif c == curses.KEY_DOWN:
            if self.idx >= 0:
                self.idx -= 1

            if self.idx == -1:
                self.cmd = ''
            else:
                self.cmd = self.history[self.idx]

        elif c == curses.KEY_RESIZE:
            Window.resize_all()

        elif not self.check_key(c) and c < 255:
            self.cmd += chr(c)

        self.draw()
        return False

    def draw(self, now = True):
        self.win.move(self.margin, self.margin)
        self.win.clrtoeol()
        self.border()
        self.win.addnstr(self.margin, self.margin, self.cmd, self.width - (2 * self.margin), curses.color_pair(self.text_color))
        self.noutrefresh()

    def check_key(self, key):
        for kb in self.key_bindings:
            if key == kb.key:
                kb.command()
                Window.draw_all(now = True)
                return True
        return False

    def get_command(self):
        s = self.cmd
        self.cmd = ''
        return s

class Output_Window(Window):

    def init_out(self, marker = '>> ', max_history = 9001):
        self.marker = marker
        self.max_history = max_history
        self.reset_pos()
        self.full_out = []
        self.out_colors = []

    def print_out(self, msg, off = 0, color = None):

        if type(msg) == type(color) and type(color) == type([]):
            self.full_out.append(msg)
            self.out_colors.append(color)
            self.draw()
            return

        if color == None: color = self.color
        if type(msg) == type([]):
            msg = ' '.join(msg)
        else:
            msg = str(msg)

        lines = msg.splitlines()
        if (len(msg) > 0 and msg[-1] == '\n') or len(lines) == 0:
            lines.append(' ')

        for i in range(len(lines)):
            lines[i] = (' '*off) + lines[i]

        self.out_colors.extend([color]*len(lines))
        self.full_out.extend(lines)
        self.draw()

    def draw(self, now = True):
        self.win.erase()
        self.reset_pos()

        for i in range(max(len(self.full_out) - (self.height - self.margin*2), 0), len(self.full_out)):
            if type(self.full_out[i]) == type([]):
                for j in range(len(self.full_out[i])):
                    self.addnstrnl(self.full_out[i][j], color = self.out_colors[i][j], nl = False)
                self.addnstrnl(' ')
            else:
                self.addnstrnl(self.full_out[i], color = self.out_colors[i])
                
        self.border()
        self.noutrefresh()

class Border_Window(Window):

    def __init__(self, stdscr, p_height = None, p_width = None, 
        resize_y = lambda std: 0, 
        resize_x = lambda std: 0, 
        resize_height = lambda std: std.getmaxyx()[0], 
        resize_width = lambda std: std.getmaxyx()[1], 
        pad = False, border_win = None, margin = 1, name = None, color = 0):

        # If: pad, auto borderwin :)

        self.stdscr = stdscr
        self.pad = False
        self.y = resize_y(stdscr)
        self.x = resize_x(stdscr)
        self.height = resize_height(stdscr)
        self.width = resize_width(stdscr)
        self.color = color
        self.name = name if name else f'BwWin{Window.win_count}'

        self.win = curses.newwin(self.height, self.width, self.y, self.x)

        self.win.attron(curses.color_pair(color))
        self.win.encoding = 'utf-8'
        self.win.leaveok(True)
        self.win.nodelay(True)
        self.win.keypad(True)

        self.border_win = self.win
        self.p_height = p_height if p_height else self.height 
        self.p_width = p_width if p_width else self.width
        self.margin = margin

        self.resize_height = resize_height
        self.resize_width = resize_width
        self.resize_y = resize_y
        self.resize_x = resize_x

        Window.windows[self.name] = self
        Window.win_count += 1

    def border(self):
        pass

def make_motors(n = 5):
    motors = []
    for i in range(n):  
        motors.append(Motor(name = f'Motor {i}', symbol = 'm'+str(i), internal = chr(65+i)))
    return motors

def make_sensors(n = 5):
    sensors = []
    for i in range(n):  
        sensors.append(Sensor(name = f'Sensor {i}', internal = chr(65+i), value = i, unit = '??'))
    return sensors

# def main2(stdscr):
#     curses.use_default_colors()
#     curses.init_pair(1, curses.COLOR_RED, -1)
#     curses.init_pair(2, curses.COLOR_GREEN, -1)
#     curses.init_pair(3, curses.COLOR_BLUE, -1)
#     curses.init_pair(4, curses.COLOR_YELLOW, -1)
#     curses.init_pair(5, curses.COLOR_CYAN, -1)
#     curses.init_pair(8, curses.COLOR_BLACK, -1)
#     curses.init_pair(9, curses.COLOR_WHITE, -1)
#     stdscr.encoding = 'utf_8'

#     x = Info_Window(stdscr = stdscr,
#         resize_y = lambda std: 0, 
#         resize_x = lambda std: std.getmaxyx()[1] - 30,
#         resize_height = lambda std: std.getmaxyx()[0], 
#         resize_width = lambda std: 30,
#         color = 5, pad = False, name = 'X')
#     x.add_perif(motors = make_motors(), sensors = make_sensors(3))
#     x.set_timer(0.5)

#     y = Output_Window(stdscr = stdscr, p_height = curses.LINES + 100, p_width = curses.COLS + 100,
#         resize_y = lambda std: 0, 
#         resize_x = lambda std: 0,
#         resize_height = lambda std: std.getmaxyx()[0] - 3, 
#         resize_width = lambda std: std.getmaxyx()[1] - 30,
#         color = 2, pad = True, name = 'Y', margin = 1)
#     y.init_out()

#     z = Command_Window(stdscr = stdscr, 
#         resize_y = lambda std: std.getmaxyx()[0] - 3, 
#         resize_x = lambda std: 0,
#         resize_height = lambda std: 3, 
#         resize_width = lambda std: std.getmaxyx()[1] - 30,
#         color = 3, pad = False, name = 'Z')
#     z.init_command()

#     x.border()
#     y.border()
#     z.border()
#     curses.doupdate()
#     i = z.win.getch()
#     x.draw(now = True)

#     while True:
#         if z.handle_user():
#             s = z.get_command()
#             if s == 'test':
#                 y.print_out(s, color = [[0,2,4],[1,3]])
#             else:
#                 y.print_out(s)
#             x.draw(True)
#         x.draw() 
#         curses.doupdate()
#     return

# if __name__ == '__main__':
#     curses.wrapper(main2)