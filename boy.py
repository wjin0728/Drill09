from pico2d import load_image, get_time
import math

from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDLK_LEFT, SDL_KEYUP, SDLK_a


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE


def autokey_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a


def time_out(e):
    return e[0] == 'TIME_OUT'


class Idle:

    @staticmethod
    def enter(boy, e):
        boy.frame = 0
        boy.time = get_time()

    @staticmethod
    def exit(boy, e):
        print('Idle Exit')

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.time >= 3.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, 200 + 100 * boy.action, 100, 100, boy.x, boy.y,boy.size,boy.size)
        pass


class Sleep:
    @staticmethod
    def enter(boy, e):
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        print('Sleep Exit')
        boy.time = 0.0

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100, math.pi / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        pass


class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.dir, boy.action = 1, 1
        elif right_up(e) or left_down(e):
            boy.dir, boy.action = -1, 0
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        boy.dir = 0

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.velocity * boy.dir

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y, boy.size, boy.size)
        pass


class AutoRun:

    @staticmethod
    def enter(boy, e):
        if boy.action == 0:
            boy.dir = -1
        elif boy.action == 1:
            boy.dir = 1
        boy.frame = 0
        boy.velocity = 10
        boy.time = get_time()
        boy.size = 200


    @staticmethod
    def exit(boy, e):
        boy.velocity = 5
        boy.time = 0
        boy.size = 100
        boy.dir = 0
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.velocity * boy.dir
        if boy.x + boy.velocity * boy.dir > 800:
            boy.x = 800
            boy.dir *= -1
            boy.action = 0
        elif boy.x + boy.velocity * boy.dir < 0:
            boy.x = 0
            boy.dir *= -1
            boy.action = 1
        else:
            boy.x += boy.velocity * boy.dir
        if get_time() - boy.time >= 5.0:
            boy.state_machine.handle_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, 100 * boy.action, 100, 100, boy.x, boy.y+40, boy.size, boy.size)
        pass


class StateMachine:
    def __init__(self, boy):
        self.cur_state = Idle
        self.boy = boy
        self.transitions = {Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, autokey_down: AutoRun},
                            Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, autokey_down: AutoRun},
                            Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle, autokey_down: AutoRun},
                            AutoRun: {right_down: Run, left_down: Run,  space_down: Idle, time_out: Idle}
                            }

    def start(self):
        self.cur_state.enter(self.boy, ('START', 0))

    def update(self):
        self.cur_state.do(self.boy)

    def draw(self):
        self.cur_state.draw(self.boy)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boy, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boy, e)
                return True
        return False


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.action = 0
        self.dir = 0
        self.velocity = 5
        self.time = 0.0
        self.size = 100
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
