'''
Talk to BKDS-8062 with Raspberry Pi GPIO pins
'''

from time import sleep
from gpiozero import OutputDevice
from gpiozero import InputDevice

class Bkds(object):
    '''
    Keep track of keypanel state, and read/write data
    '''

    def __init__(
        self,
        clock_pin=25,
        latch_pin=12,
        reset_pin=16,
        led_data_pin=20,
        switch_data_pin=21):
        '''
        Setup GPIO pins, defaulting to the pin numbers on what will probably
        the only hardware this ever runs on
        '''

        ## The BKDS-8062 uses negative logic for all pins, so all of these
        ## are set to active low to make code more straightforward
        self.clock = OutputDevice(clock_pin, active_high=False)
        self.latch = OutputDevice(latch_pin, active_high=False) 
        self.reset = OutputDevice(reset_pin, active_high=False)
        self.led_data = OutputDevice(led_data_pin, active_high=False)
        self.switch_data = OutputDevice(switch_data_pin, active_high=False)

        ## BKDS-8062 max clock speed is about 2MHz, 
        ## with about 200ns between operations
        ## We'll just set it to "fast enough for now"
        self.clock_time = 0.00001

        self.leds = [False] * 21
        
        ## LED red/orange color can be set for the first, last, or all middle
        self.colors = [False] * 3 

        self.buttons = [False] * 21


    def click(self):
        '''
        Send clock pulse
        '''
        self.clock.off()
        sleep(self.clock_time)
        self.clock.on()
        sleep(self.clock_time)


    def update_leds(self):
        '''
        Send values of self.leds to keypanel
        '''
        self.latch.off() ## latch off hides changes

        for value in reversed(self.leds + self.colors):
            self.led_data.value = value
            self.click()

        self.latch.on()


