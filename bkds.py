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
        self.switch_data = InputDevice(switch_data_pin)

        ## BKDS-8062 max clock speed is about 2MHz, 
        ## with about 200ns between operations
        ## We'll just set it to "fast enough for now"
        self.clock_time = 0.000001

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

    def update_buttons(self):
        '''
        Read the current state of the buttons into self.buttons
        '''
        self.latch.on()
        sleep(self.clock_time)
        self.latch.off()
        for i, button in enumerate(self.buttons):
            self.click()
            self.buttons[i] = not self.switch_data.is_active


    def update(self):
        '''
        Run both update functions
        '''
        self.update_leds()
        self.update_buttons()




if __name__ == '__main__':
    bkds = Bkds()
    buttons_held = [False] * 21
    print('Ready')
    while True:
        for i, val in enumerate(bkds.buttons):
            if val:
                if not buttons_held[i]:
                    print('button: {}'.format(i))
                    bkds.leds[i] = not bkds.leds[i]
                    buttons_held[i] = True
            else:
                buttons_held[i] = False

        bkds.update()


