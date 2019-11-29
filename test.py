'''
Run basic functions and see if the hardware responds
'''

from bkds import Bkds

b = Bkds()

b.leds[20] = True
b.leds[19] = True
b.leds[0] = True
b.colors[1] = True
b.update_leds()

b.update_buttons()
print(b.buttons)
