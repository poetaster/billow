# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import pwmio
import simpleio
import busio

from adafruit_motor import motor
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from neopixel import NeoPixel
from random import randint

# from neopixel foo
#pin = Pin(16, Pin.OUT)   # set GPI=16 to output to drive NeoPixels
#pin = board.GP16 #on the zero
np = NeoPixel(board.GP16, 1)   # create NeoPixel driver on GPIO16 for 1 pixel

def neo_pixel (valore):
    try:
        # se valore è una tupla/lista di 3 termini:
        if len(valore)==3:
            if 0<=valore[0]<=255 and 0<=valore[1]<=255 and 0<=valore[2]<=255:
                np[0] = valore
                np.write()
                return 1
            else:
                return 0
    except:
        try:
            if valore==0:
                np[0] = (0,0,0)
                np.write()
                return 1
            elif valore==1:
                np[0] = (255,255,255)
                np.write()
                return 1
        except:
            return 0

neo_pixel (0)

# from MIDI to cv skull mappings approx
volts = {
    72:0.000,
    73:.083,
    74:.167,
    75:.250,
    76:.333,
    77:.417,
    78:.500,
    79:.583,
    80:.667,
    81:.750,
    82:.833,
    83:.917,
    84:1.000,
}
    

# from walkmellotron
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

volts_per_note = 0.00833  # 1/12th V for 1V/Oct

def midi_to_mv(note):
    #notemv = 1000 * (note * volts_per_note)
    notemv = (note * volts_per_note)
    return int(notemv)

uart = busio.UART(board.TX, board.RX, baudrate=31250, timeout=0.001)  # init UART
midi_in_channel = 2
midi_out_channel = 1
midi = adafruit_midi.MIDI(
    midi_in=uart,
    midi_out=uart,
    in_channel=(0,1,2),
    out_channel=(midi_out_channel - 1),
    debug=False,
)

# end from walkmelotron

#  button setup
#warble_switch = DigitalInOut(board.A0)
#warble_switch.direction = Direction.INPUT
#warble_switch.pull = Pull.UP
#  potentiometer setup
pot = AnalogIn(board.A0)

#  PWM pins for L9110
PWM_PIN_A = board.A2  # pick any pwm pins on their own channels
PWM_PIN_B = board.A1
#  PWM setup
pwm_a = pwmio.PWMOut(PWM_PIN_A, frequency=50)
pwm_b = pwmio.PWMOut(PWM_PIN_B, frequency=50)
#  motor setup
cassette = motor.DCMotor(pwm_a, pwm_b)

#  variables for warble switch
i = 0.0
last_i = 0.0
pos = False
neg = False
notesOn = 0
while True:

    # from walkmellotron
    msg = midi.receive()
    # end from walkmellotron
    #  map range of pot to range of motor speed
    #  all the way to the left will run the motor in reverse full speed
    #  all the way to the right will run the motor forward full speed
    mapped_speed = simpleio.map_range(pot.value, 0, 65535, 0.0, 1.0)
    #  if you press the button...
    #  creates a ramping effect
    #print(mapped_speed)

    # if we're in midi mode
    
    if msg is not None:
        if isinstance(msg, NoteOn):
            notesOn += 1
            string_msg = 'NoteOn'
            #  get note number
            string_val = str(msg.note)
            print("\nnote:",string_val)
            if msg.note < 75:
                neo_pixel ((0,randint(msg.note,255),255))
                note = msg.note - 48
                #mv = midi_to_mv(msg.note)
                mv = (note * 0.03) + 0.2
                print(mv, "V")
                #mv = volts[note]
                #print(mv)
                #mcp4728.channel_a.raw_value = (mv)
                cassette.throttle = (mv)
                mapped_speed = mv
                time.sleep(0.1)
            if msg.note > 74 and msg.note < 86:
                neo_pixel ((randint(msg.note,255),0,randint(msg.note,255)))
                #mv = midi_to_mv(msg.note)
                mv = volts[msg.note]
                print(mv, msg.note)
                #mcp4728.channel_a.raw_value = (mv)
                cassette.throttle = (mv)
                mapped_speed = mv
        if isinstance(msg, NoteOff):
            if notesOn > 0 :
                notesOn -= 1
            if notesOn is 0:
                neo_pixel (0)
                cassette.throttle = (0)
            #mapped_speed = 0
            #time.sleep(0.1)
'''
    if mapped_speed > 0.1:
        #  checks current pot reading
        #  if it's positive...
        #neo_pixel (1)]

        if mapped_speed > 0:
            #  sets starting speed
            i = 0.0
            #  sets last value to loop
            last_i = i
            #  notes that it's positive
            pos = True
        #  if it's negative...
        else:
            #  sets starting speed
            i = -0.4
            #  sets last value to loop
            last_i = i
            #  notes that it's negative
            neg = True
        #  loop 8 times
        for z in range(8):
            #  if it's positive...
            if pos:
                #  increase speed
                i += 0.06
            #  if it's negative
            else:
                #  decrease speed
                i -= 0.06
            #  send value to motor
            neo_pixel (1)
            cassette.throttle = i
            time.sleep(0.1)
        #  loop the value while button is held down
        i = last_i
        pos = False
        neg = False
    #  run motor at mapped speed from the pot
        print(mapped_speed)
        cassette.throttle = mapped_speed
 
 '''
    
