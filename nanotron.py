import nxt.locator
from nxt.motor import *
from nxt.sensor import *
import os
import display
import time

class Nanotron:
    play_port = PORT_A
    select_port = PORT_B
    menu_port = PORT_C
    play_force = 63
    select_force = 63
    menu_force = 63
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
        display.myprint("Disk mode combo down", 2)
        self.press_select()
        self.press_play()
        display.myprint("waiting %u seconds for disk mode" % seconds, 2)
        time.sleep(seconds)
        self.reset()
        display.myprint("Disk mode combo up", 2)
    def rebootcombo(self, seconds):
        display.myprint("Reboot combo down", 2)
        self.press_select()
        self.press_menu()
        display.myprint("unmounting before reboot", 1)
        if self.is_mounted(): os.system('umount /media/ipod')
        display.myprint("waiting %u seconds for reboot" % seconds, 2)
        time.sleep(seconds)
        self.reset()
        display.myprint("Reboot combo up", 2)
    def reboot(self, irc):
        display.myprint("Rebooting...", 1)
        self.rebootcombo(5.5)
        while self.is_mounted():
            display.myprint("Having trouble resetting the iPod!", 0, irc)
            self.rebootcombo(8)
            time.sleep(0.5)
    def disk_mode(self, irc):
        display.myprint("Trying to enter Disk mode...", 1)
        self.reboot(irc)
        time.sleep(.25)
        self.diskmodecombo(10)
        time.sleep(10)
        while not self.is_mounted():
            display.myprint("Having trouble putting the iPod into disk mode!", 0, irc)
            self.reboot(irc)
            time.sleep(.25)
            self.diskmodecombo(10)
            time.sleep(10)
        display.myprint("entered disk mode...", 1)
    def is_mounted(self):
        return os.path.exists(self.IPODPATH + "/Notes")
    def get_status(self):
        if self.is_mounted():
            display.myprint("WORKS", 1)
            return 1 #Works
        else:
            time.sleep(7)
            if self.is_mounted():
                display.myprint("CRASH", 1)
                return 0 #Crash
            else:
                display.myprint("FREEZE", 1)
                return 2 #Freeze