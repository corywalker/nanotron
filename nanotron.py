import nxt.locator
from nxt.motor import *
from nxt.sensor import *
import os
import display

class Nanotron:
    play_port = PORT_A
    select_port = PORT_B
    menu_port = PORT_C
    play_force = 65
    select_force = 65
    menu_force = 65
    touch_port = PORT_1
    light_port = PORT_3
    IPODPATH = '/media/ipod'
    def __init__(self):
        #self.myprint = myprint
        try:
            self.sock = nxt.locator.find_one_brick()
        except nxt.locator.BrickNotFoundError:
            display.myprint("FATAL: No NXT was found")
            quit()
        self.brick = self.sock.connect()
        self.play_motor = Motor(self.brick, self.play_port)
        self.select_motor = Motor(self.brick, self.select_port)
        self.menu_motor = Motor(self.brick, self.menu_port)
        self.touch_sensor = TouchSensor(self.brick, self.touch_port)
        self.light_sensor = LightSensor(self.brick, self.light_port)
    def close(self):
        self.sock.close()
    def press_play(self): self.play_motor.run(self.play_force, False)
    def press_select(self): self.select_motor.run(self.select_force, False)
    def press_menu(self): self.menu_motor.run(self.menu_force, False)
    def release_play(self): self.play_motor.stop(False)
    def release_select(self): self.select_motor.stop(False)
    def release_menu(self): self.menu_motor.stop(False)
    def get_touch(self): return self.touch_sensor.get_sample()
    def get_light(self): return self.light_sensor.get_sample()
    def reset(self):
        self.release_play()
        self.release_select()
        self.release_menu()
    def diskmodecombo(self, seconds):
        self.press_select()
        self.press_play()
        time.sleep(seconds)
        self.reset()
    def rebootcombo(self, seconds):
        self.press_select()
        self.press_menu()
        time.sleep(seconds)
        self.reset()
    def reboot(self, irc):
        self.rebootcombo(5.5)
        while self.is_mounted():
            display.myprint("Having trouble resetting the iPod!", irc)
            self.rebootcombo(8)
            time.sleep(0.5)
    def disk_mode(self, irc):
        self.reboot(irc)
        time.sleep(.25)
        self.diskmodecombo(3)
        time.sleep(5)
        while not self.is_mounted():
            display.myprint("Having trouble putting the iPod into disk mode!", irc)
            self.reboot(irc)
            time.sleep(.25)
            self.diskmodecombo(4)
            time.sleep(5)
    def is_mounted(self):
        return os.path.exists(self.IPODPATH + "/Notes")
    def get_status(self):
        if self.is_mounted():
            return 0 #Crash
        else:
            time.sleep(8)
            if self.is_mounted():
                return 1 #Works
            else:
                return 2 #Freeze