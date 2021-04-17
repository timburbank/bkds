#!/usr/bin/python
'''
Talk to BKDS-8062 with Raspberry Pi GPIO pins
'''
import argparse
from time import sleep
from datetime import datetime
from datetime import timedelta
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
        switch_data_pin=21,
        num_buttons=21):
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
        
        self.num_buttons = num_buttons ## not tested with other than 21
        self.leds = [False] * self.num_buttons
        
        ## LED red/orange color can be set for the first, last, or all middle
        self.colors = [False] * 3 

        self.buttons = [False] * self.num_buttons


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


def toggle():
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


def xmas():
    '''
    Light up all LEDs in sequence
    '''
    bkds = Bkds()
    anim_time = 0.02

    bkds.leds = [False] * bkds.num_buttons
    bkds.update_leds()
   
    try:
        while True:
            bkds.colors = [False] * 3
            for i in range(0, bkds.num_buttons):
                bkds.leds = [False] * bkds.num_buttons
                bkds.leds[i] = True
                bkds.update_leds()
                sleep(anim_time)
         
            bkds.leds = [False] * bkds.num_buttons
            bkds.update_leds()

            bkds.colors = [True] * 3
            for i in reversed(range(0, bkds.num_buttons)):
                bkds.leds = [False] * bkds.num_buttons
                bkds.leds[i] = True
                bkds.update_leds()        
                sleep(anim_time)

    except KeyboardInterrupt:
        bkds.leds = [False] * bkds.num_buttons
        bkds.colors = [False] * 3
        bkds.update_leds()
        exit()

def clear_leds():
    bkds = Bkds()
    bkds.update_leds()


def countdown_timer(func, duration):
    time_format = '%Y-%m-%d %H:%M:%S'
    bkds = Bkds()
    bkds.colors = [False, False, True]
    target_seconds = duration * 60
    start_time = datetime.now()
    target_time = start_time + timedelta(seconds = target_seconds)
    last_displayed_time = timedelta()

    print('{} timer started'.format(start_time.strftime(time_format)))

    while datetime.now() < target_time:
        elapsed = datetime.now() - start_time
        progress = (float(elapsed.total_seconds()) / target_seconds)
        progress_led = int(progress * (bkds.num_buttons - 1))

        bkds.leds = [False] * bkds.num_buttons
        bkds.leds[progress_led] = True
        bkds.update_leds()

        if elapsed >= last_displayed_time + timedelta(seconds=60):
            last_displayed_time = elapsed
            print('{} {:.0f}/{:.0f}'.format(
                datetime.now().strftime(time_format),
                elapsed.total_seconds() / 60,
                duration))

        if duration > 1:
            ## Use less CPU if we don't need fast updates
            sleep(1)

    ## When finished
    bkds.leds = [False] * bkds.num_buttons
    bkds.leds[-1] = True
    bkds.update_leds()

    print('{} timer finished'.format(datetime.now().strftime(time_format)))


def cli_args():
    '''
    Define command line options for testing
    '''
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers()
    
    parser_toggle = subparsers.add_parser(
        'toggle',
        help='Toggle lights and show button inputs')
    parser_toggle.set_defaults(func=toggle)

    parser_xmas = subparsers.add_parser(
        'xmas',
        help='Light up everything in sequence')
    parser_xmas.set_defaults(func=xmas)
    
    clear_parser = subparsers.add_parser(
        'clear',
        help='Turn off all LEDs')
    clear_parser.set_defaults(func=clear_leds)

    timer_parser = subparsers.add_parser(
        'timer',
        help='Show timer progress')
    timer_parser.add_argument(
        'duration',
        type=float,
        help='Timer duration in minutes')
    timer_parser.set_defaults(func=countdown_timer)
    
    return parser.parse_args()

if __name__ == '__main__':
    args = cli_args()
    if len(vars(args)) > 1:
        args.func(**vars(args))
    else:
        args.func()
