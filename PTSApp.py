#To run the application from VSCode, install the scripts below, and
#make sure to change your directory to the GitHub folder for this app before running otherwise the fonts won't be found

#macOS
#python3 -m pip install pygame==2.0.1
#python3 -m pip install pygame_gui==0.6.5
#python3 -m pip install pyserial

#Windows
#python -m pip install pygame==2.0.1
#python -m pip install pygame_gui==0.6.5
#python -m pip install pyserial

#To create an executable file:
#python3 -m pip install pyinstaller
#pyinstaller --additional-hooks-dir=. --onefile --windowed --icon PTSApp-Icon.icns --name PTSApp PTSApp.py

#python -m pip install pyinstaller
#pyinstaller --onefile --windowed --icon="PTSApp-Icon.ico" PTSApp.py

import pygame
from pygame.cursors import tri_left
import pygame_gui
import time
import serial.tools.list_ports
import os, sys

from collections import deque
from pygame_gui import UIManager
from pygame_gui.elements import UIButton
from pygame_gui.elements import UITextEntryLine
from pygame_gui.elements import UIDropDownMenu
from pygame_gui.elements import UILabel
from pygame_gui.elements.ui_text_box import UITextBox
from serial import *
from pathlib import Path

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

baudRate = 57600 #57600 or 38400

speedFastX = 's20'
speedFastY = 'S20'
speedFastZ = 'X60'

speedSlowX = 's10'
speedSlowY = 'S10'
speedSlowZ = 'X30'

def find_data_file(filename):
    if getattr(sys, "frozen", False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)
'''
try:
    base_path = Path(__file__).parent
    image_path = (base_path / "./PTSApp-Icon.png").resolve()
    gameIcon = pygame.image.load(image_path)
    pygame.display.set_icon(gameIcon)
except:
    imagefile = "PTSApp-Icon.png"
    imagefilepath = find_data_file(imagefile)
    gameIcon = pygame.image.load(imagefilepath)
    pygame.display.set_icon(gameIcon)
'''

pygame.font.init()
myfont = pygame.font.SysFont('Trebuchet MS', 30)
clk = pygame.time.Clock()

ser = ''
serBuffer = ''
serialText = ''
joystick = ''
joystick2 = ''
joystickName = ''
joystickName1 = ''
joystickName2 = ''
button0Pressed = False
button1Pressed = False
button2Pressed = False
button3Pressed = False
button4Pressed = False
button5Pressed = False
button6Pressed = False
button7Pressed = False
button8Pressed = False
button9Pressed = False
button10Pressed = False
button11Pressed = False
button12Pressed = False
button13Pressed = False
button14Pressed = False
textBoxJoystickNames = None
joy1Xmoving = False
joy1Ymoving = False
joy2Xmoving = False
joy2Ymoving = False
joy1sliding = False
joy2sliding = False
joyCircle_draging = False
sliderCircle_draging = False
offset_x = 0.0
sliderOffset_x = 0.0
offset_y = 0.0
sliderOffset_y = 0.0
textBoxSerial = None
arr = []
oldAxisX = 0
oldAxisY = 0
oldAxisZ = 0
axisX = 0
axisY = 0
axisZ = 0
data = bytearray(7)
hat = ()
oldHatX = 0
oldHatY = 0
previousTime = time.time()
RED = (255, 0, 0)
mouseBorder = 360
radius = 15
mouseMoving = False
joyXreadDOT = 0.0
joyYreadDOT = 0.0
joyZreadDOT = 0.0
panKeyPresseed = False
tiltKeyPresseed = False
sliderKeyPresseed = False

textsurfaceW = myfont.render('w', False, (89, 89, 89))
textsurfaceA = myfont.render('a', False, (89, 89, 89))
textsurfaceS = myfont.render('s', False, (89, 89, 89))
textsurfaceD = myfont.render('d', False, (89, 89, 89))
textsurfaceLeft = myfont.render(',', False, (89, 89, 89))
textsurfaceRight = myfont.render('.', False, (89, 89, 89))

resolution = (1200, 660)
fullscreen = False

pygame.init()
pygame.display.set_caption("PTSApp")

def sendClearArray():
    temp='C'
    sendSerial(temp)

def sendAddPos():
    temp='#'
    sendSerial(temp)

def sendEditPos():
    temp='E'
    sendSerial(temp)

def sendGOFirst():
    temp='['
    sendSerial(temp)

def sendGOBack():
    temp='<'
    sendSerial(temp)

def sendGOFwd():
    temp='>'
    sendSerial(temp)

def sendGOLast():
    temp=']'
    sendSerial(temp)

def sendExecMoves():
    temp=';1'
    sendSerial(temp)

def sendOrbitPoint():
    temp='@1'
    sendSerial(temp)

def sendTimelapse():
    temp='l'
    sendSerial(temp)

def sendPanoramicLapse():
    temp='L'
    sendSerial(temp)

def sendREPORTall():
    temp='R'
    sendSerial(temp)

def sendCLEARtext():
    global serialText
    serialText = ''
    textBoxSerial.kill()
    serialPortTextBox()

def sendFAST():
    sendSerial(speedFastX)
    clk.tick(10)
    sendSerial(speedFastY)
    clk.tick(10)
    sendSerial(speedFastZ)

def sendSLOW():
    sendSerial(speedSlowX)
    clk.tick(10)
    sendSerial(speedSlowY)
    clk.tick(10)
    sendSerial(speedSlowZ)

def serialPort_changed():
    global ser
    global baudRate
    global current_serialPort
    global serialText
    global drop_down_serial
    
    serialPortSelect = drop_down_serial.selected_option
    try:
        ser = Serial(serialPortSelect , baudRate, timeout=0, writeTimeout=0)
        readSerial()
    except:
        ser = ''
        serialNotSel = 'Serial port not available!<br>'
        current_serialPort = ['']
        textBoxSerial.kill()
        serialText = serialText + serialNotSel
        serialPortTextBox()
        drop_down_serial.kill()
        drop_down_serial = UIDropDownMenu(available_ports,                      # Recreate serial port drop down list
                                        available_ports[0],                  # Currently selected port
                                        pygame.Rect((620,95),
                                        (250, 30)),
                                        ui_manager)

def tohex(val, nbits):
    return hex((val + (1 << nbits)) % (1 << nbits))

def sendJoystick(arr):
    global ser
    global data
    
    sliderInt = int(arr[1], 16)
    panInt = int(arr[2], 16)
    tiltInt = int(arr[3], 16)

    data[0] = 4
    
    if ((sliderInt > 0) and (sliderInt < 256)):
        data[1] = 0
        data[2] = sliderInt
    elif sliderInt > 256:
        data[1] = 255
        data[2] = (sliderInt-65281)
    else:
        data[1] = 0
        data[2] = 0

    if ((panInt > 0) and (panInt < 256)):
        data[3] = 0
        data[4] = panInt
    elif panInt > 256:
        data[3] = 255
        data[4] = (panInt-65281)
    else:
        data[3] = 0
        data[4] = 0

    if ((tiltInt > 0) and (tiltInt < 256)):
        data[5] = 0
        data[6] = tiltInt
    elif tiltInt > 256:
        data[5] = 255
        data[6] = (tiltInt-65281)
    else:
        data[5] = 0
        data[6] = 0
    
    if ser == '':
        pass
    else:
        ser.write(data)
        #print(data)

def serialPortTextBox():
    global textBoxSerial
    textBoxSerial = UITextBox('<font face=roboto size=4 color=#F0F0F0>' + serialText + '</font>',
                                        pygame.Rect((620, 130), (560, 510)),
                                        ui_manager)
    if textBoxSerial.scroll_bar:
        scroll_bar = textBoxSerial.scroll_bar
        scroll_bar.scroll_position = (scroll_bar.bottom_limit - scroll_bar.sliding_button.rect.height)
        x_pos = scroll_bar.rect.x + scroll_bar.shadow_width + scroll_bar.border_width
        y_pos = scroll_bar.scroll_position + scroll_bar.rect.y + scroll_bar.shadow_width + \
                scroll_bar.border_width + scroll_bar.button_height
        scroll_bar.sliding_button.set_position(pygame.math.Vector2(x_pos, y_pos))

        scroll_bar.start_percentage = scroll_bar.scroll_position / scroll_bar.scrollable_height
        if not scroll_bar.has_moved_recently:
            scroll_bar.has_moved_recently = True
    
def textBoxJoystickName():
    global joystickName
    global textBoxJoystickNames
    textBoxJoystickNames = UITextBox(joystickName,
                                        pygame.Rect((620, 30), (560, 35)),
                                        ui_manager)

def readSerial():
    global ser
    global serBuffer
    global serialText

    if (ser == ''):
        return
    else:
        while True:
            c = ser.read()

            if len(c) == 0:
                break

            if (c == b'\x04'):                                          # Ignore received joystick commands from other remote
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ser.read()
                c = ''
            elif (c == b'\xb0'):                                        # Change / remove characters that cause error
                c = '°'
            elif (c == b'\xb2'):
                c = '²'
            elif (c == b'\xba') or (c == b'\xc2') or (c == b'\xc9'):
                c = ''
            else:
                c = c.decode('ascii') 

            if (c == '\r'):                                             # check if character is a delimeter
                c = ''                                                  # don't want returns. chuck it

            if (c == '\t'):                                             # check if character is a tab
                c = '<br>'#' - '                                        # adjust
                
            if c == '\n':
                serBuffer += '<br>'                                     # replace \n with HTML <br>
                textBoxSerial.kill()
                serialText = serialText + serBuffer
                serialPortTextBox()
                serBuffer = ''                                          # empty the buffer
            else:
                serBuffer += c                                          # add to the buffer

def sendSerial(sendValue):
    global ser
    global serialText
    if (ser == ''):                                             # Checks to see if com port has been selected
        serialNotSel = 'Serial port not selected!<br>'
        textBoxSerial.kill()
        serialText = serialText + serialNotSel
        serialPortTextBox()
    else:
        ser.write(sendValue.encode())                           # Send button value to coneected com port
        
def scale(val, src, dst):
    # Scale the given value from the scale of src to the scale of dst.
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]
    
def initialiseJoysticks():
    global joystick
    global joystick2
    global joystickName
    global joystickName1
    global joystickName2

    available_joysticks = []                                            # for returning
    pygame.joystick.init()                                              # Initialise the Joystick sub-module
    joystick_count = pygame.joystick.get_count()                        # Get count of joysticks
    #print(joystick_count)

    #for i in range( joystick_count ):                                   # For each joystick:
    if joystick_count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        available_joysticks.append(joystick)
        if joystick_count > 1:
            joystick2 = pygame.joystick.Joystick(1)
            joystick2.init()
            available_joysticks.append(joystick2)

    if ( len( available_joysticks ) == 0 ):
        joystickName =  "No joystick found."
    else:
        #for i,joystk in enumerate( available_joysticks ):

        joystickName1 = joystick.get_name()

        if joystick_count > 1:
            joystickName2 = joystick2.get_name()

            #joystickNameID = joystk.get_instance_id()
            joystickName = joystickName1 + " & " + joystickName2

        else:
            joystickName = joystickName1

    return available_joysticks

def int_to_bytes(number: int) -> bytes:
    return number.to_bytes(length=(8 + (number + (number < 0)).bit_length()) // 8, byteorder='big', signed=True)

def doRefresh():
    global drop_down_serial
    global ser
    global current_serialPort
    global baudRate
    drop_down_serial.kill()                                             # Clear serial port drop down box
    ports = serial.tools.list_ports.comports()                          # Search for attached serial ports
    available_ports = []
    for p in ports:
        available_ports.append(p.device)                                # Append each found serial port to array available_ports

    current_serialPort = ['']

    drop_down_serial = UIDropDownMenu(available_ports,                  # Recreate serial port drop down list
                                available_ports[0],                  # Currently selected port
                                pygame.Rect((620,95),
                                (250, 30)),
                                ui_manager)
    
    initialiseJoysticks()
    textBoxJoystickName()

initialiseJoysticks()

if fullscreen:
    window_surface = pygame.display.set_mode(resolution,
                                                    pygame.FULLSCREEN)
else:
    window_surface = pygame.display.set_mode(resolution)

background_surface = None

try:
    themefile = "theme.json"
    full_path = find_data_file(themefile)
    ui_manager = UIManager(resolution, full_path)
except:
    base_path = Path(__file__).parent
    file_path = (base_path / "./theme.json").resolve()
    ui_manager = UIManager(resolution, file_path)

running = True

clock = pygame.time.Clock()
time_delta_stack = deque([])

button_response_timer = pygame.time.Clock()

ui_manager.set_window_resolution(resolution)
ui_manager.clear_and_reset()

background_surface = pygame.Surface(resolution)
background_surface.fill(ui_manager.get_theme().get_colour('dark_bg'))

rel_button_Clear = UIButton(pygame.Rect((110, 500), (60, 60)), 'Clear', ui_manager, object_id='#everything_button')
rel_button_AddPos = UIButton(pygame.Rect((180, 500), (60, 60)), 'ADD', ui_manager, object_id='#everything_button')
rel_button_EditPos = UIButton(pygame.Rect((250, 500), (60, 60)), 'EDIT', ui_manager, object_id='#everything_button')
rel_button_GOFirst = UIButton(pygame.Rect((85, 560), (60, 60)), '< <', ui_manager, object_id='#everything_button')
rel_button_GOBack = UIButton(pygame.Rect((145, 560), (60, 60)), '<', ui_manager, object_id='#everything_button')
rel_button_GOFwd = UIButton(pygame.Rect((215, 560), (60, 60)), '>', ui_manager, object_id='#everything_button')
rel_button_GOLast = UIButton(pygame.Rect((275, 560), (60, 60)), '> >', ui_manager, object_id='#everything_button')
rel_button_Refresh = UIButton(pygame.Rect((430, 35), (160, 35)), 'Refresh Ports', ui_manager, object_id='#everything_button')
rel_button_ExecMoves = UIButton(pygame.Rect((430, 180), (160, 60)), 'Exec. Moves', ui_manager, object_id='#everything_button')
rel_button_OrbitPoint = UIButton(pygame.Rect((430, 240), (160, 60)), 'Orbit Point', ui_manager, object_id='#everything_button')
rel_button_Timelapse = UIButton(pygame.Rect((430, 300), (160, 60)), 'Timelapse', ui_manager, object_id='#everything_button')
rel_button_PANORAMICLAPSE = UIButton(pygame.Rect((430, 360), (160, 60)), 'Panoramiclapse', ui_manager, object_id='#everything_button')
rel_button_REPORT = UIButton(pygame.Rect((460, 500), (100, 60)), 'Report', ui_manager, object_id='#everything_button')
rel_button_CLEARtext = UIButton(pygame.Rect((460, 570), (100, 40)), 'Clear Text', ui_manager, object_id='#everything_button')
joystick_label = UILabel(pygame.Rect(540, 10, 230, 24), "Joystick", ui_manager)
serial_text_entry = UITextEntryLine(pygame.Rect((930, 95), (250, 35)), ui_manager, object_id='#main_text_entry')
serial_port_label = UILabel(pygame.Rect(550, 70, 230, 24), "Serial Port", ui_manager)
serial_command_label = UILabel(pygame.Rect(870, 70, 230, 24), "Serial Command", ui_manager)

current_serialPort = '-'
ports = serial.tools.list_ports.comports()
available_ports = []
for p in ports:
    available_ports.append(p.device)                        # Append each found serial port to array available_ports

if available_ports == []:
    available_ports.append("No ports available")

drop_down_serial = UIDropDownMenu(available_ports, available_ports[0], pygame.Rect((620,95), (250, 30)), ui_manager)


serialPortTextBox()
textBoxJoystickName()

joyCircle = pygame.draw.circle(window_surface, pygame.Color("blue"), (225,225), radius)
joyCircle_draging = False
joyCircle.x = 195
joyCircle.y = 195
crosshair = pygame.surface.Surface((30, 30))
crosshair.fill(pygame.Color("magenta"))
pygame.draw.circle(crosshair, pygame.Color("blue"), (radius,radius), radius)
crosshair.set_colorkey(pygame.Color("magenta"))#, pygame.RLEACCEL)
#crosshair = crosshair.convert()

sliderCircle = pygame.draw.circle(window_surface, pygame.Color("blue"), (225,415), radius)
sliderCircle_draging = False
sliderCircle.x = 195
sliderCircle.y = 415
crosshairSlider = pygame.surface.Surface((30, 30))
crosshairSlider.fill(pygame.Color("magenta"))
pygame.draw.circle(crosshairSlider, pygame.Color("blue"), (radius,radius), radius)
crosshairSlider.set_colorkey(pygame.Color("magenta"))#, pygame.RLEACCEL)
#crosshairSlider = crosshairSlider.convert()

def process_events():
    global arr
    global joystick
    global joystick2
    global joystickName
    global joystickName1
    global joystickName2
    global button0Pressed
    global button1Pressed
    global button2Pressed
    global button3Pressed
    global button4Pressed
    global button5Pressed
    global button6Pressed
    global button7Pressed
    global button8Pressed
    global button9Pressed
    global button10Pressed
    global button11Pressed
    global button12Pressed
    global button13Pressed
    global button14Pressed
    global oldAxisX
    global oldAxisY
    global oldAxisZ
    global oldHatX
    global oldHatY
    global axisX
    global axisY
    global axisZ
    global previousTime
    global mouseMoving
    global joy1Xmoving
    global joy1Ymoving
    global joy2Xmoving
    global joy2Ymoving
    global joy1sliding
    global joy2sliding
    global joyCircle_draging
    global sliderCircle_draging
    global offset_x
    global offset_y
    global sliderOffset_x
    global sliderOffset_y
    global running
    global joyXreadDOT
    global joyYreadDOT
    global joyZreadDOT
    global panKeyPresseed
    global tiltKeyPresseed
    global sliderKeyPresseed
    global drop_down_serial

    joyPS4 = "Sony"
    joyPS4BT = "DUALSHOCK"
    joyPS4Win = "PS4"
    joy360 = "360"
    joyNimbus = "Nimbus"
    joySN30 = "SN30"
    joySN30BT = "Unknown Wireless Controller"

    UITextEntry = "UITextEntryLine"
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        ui_manager.process_events(event)
        deadRangeLow = -0.2
        deadRangeHigh = 0.2

        #print(event)

        whereIsFocus = str(ui_manager.get_focus_set())
        if (event.type == pygame.KEYDOWN) and not (UITextEntry in whereIsFocus):
            if event.key == ord('a'):
                axisX = int(-255)
                panKeyPresseed = True
                #print('Left')
            if event.key == ord('d'):
                axisX = int(255)
                panKeyPresseed = True
                #print('Right')
            if event.key == ord('w'):
                axisY = int(-255)
                tiltKeyPresseed = True
                #print('Up')
            if event.key == ord('s'):
                axisY = int(255)
                tiltKeyPresseed = True
                #print('Down')
            if event.key == ord(','):
                axisZ = int(-255)
                sliderKeyPresseed = True
                #print('Slider Left')
            if event.key == ord('.'):
                axisZ = int(255)
                sliderKeyPresseed = True
                #print('Slider Right')

        if (event.type == pygame.KEYUP) and not (UITextEntry in whereIsFocus):
            if event.key == ord('a'):
                axisX = int(0)
                panKeyPresseed = False
                #print('Left stop')
            if event.key == ord('d'):
                axisX = int(0)
                panKeyPresseed = False
                #print('Right stop')
            if event.key == ord('w'):
                axisY = int(0)
                tiltKeyPresseed = False
                #print('Up stop')
            if event.key == ord('s'):
                axisY = int(0)
                tiltKeyPresseed = False
                #print('Down stop')
            if event.key == ord(','):
                axisZ = int(0)
                sliderKeyPresseed = False
                #print('Slider Left stop')
            if event.key == ord('.'):
                axisZ = int(0)
                sliderKeyPresseed = False
                #print('Slider Right stop')

        # left 1
        # right 2
        # down 3
        # up 4

        if joystick == '':
            pass
        else:
            if (joyPS4 in joystickName1) or (joyPS4BT in joystickName1) or (joyPS4Win in joystickName1):
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # PS4 - Cross
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick.get_button(1) and not button1Pressed):               # PS4 - Circle
                        button1Pressed = True
                        sendAddPos()
                    elif (joystick.get_button(2) and not button2Pressed):               # PS4 - Square
                        button2Pressed = True
                        sendExecMoves()
                    elif (joystick.get_button(3) and not button3Pressed):               # PS4 - Triangle
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick.get_button(4) and not button4Pressed):               # PS4 - Share
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick.get_button(5) and not button5Pressed):               # PS4 - PS
                        button5Pressed = True
                        sendFAST()
                    elif (joystick.get_button(6) and not button6Pressed):               # PS4 - Option
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(7) and not button7Pressed):               # PS4 - L3
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(8) and not button8Pressed):               # PS4 - R3
                        button8Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(9) and not button9Pressed):               # PS4 - L1
                        button9Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(10) and not button10Pressed):             # PS4 - R1
                        button10Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(11) and not button11Pressed):             # PS4 - UP
                        button11Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(12) and not button12Pressed):             # PS4 - DOWN
                        button12Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(13) and not button13Pressed):             # PS4 - LEFT
                        button13Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(14) and not button14Pressed):             # PS4 - RIGHT
                        button14Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(15) and not button15Pressed):             # PS4 - Pad
                        button15Pressed = True
                        sendREPORTall()

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging and not joy2Xmoving and not joy2Ymoving:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                        joy1Xmoving = True
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                        joy1Xmoving = True
                    else:
                        axisX = 0
                        joy1Xmoving = False

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                        joy1Ymoving = True
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                        joy1Ymoving = True
                    else:
                        axisY = 0
                        joy1Ymoving = False

                if not sliderKeyPresseed and not sliderCircle_draging and not joy2sliding:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                        joy1sliding = True
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                        joy1sliding = True
                    else:
                        axisZ = 0
                        joy1sliding = False

            elif joy360 in joystickName1:
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # 360 - A
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick.get_button(1) and not button1Pressed):               # 360 - B
                        button1Pressed = True
                        sendAddPos()
                    elif (joystick.get_button(2) and not button2Pressed):               # 360 - X
                        button2Pressed = True
                        sendExecMoves()
                    elif (joystick.get_button(3) and not button3Pressed):               # 360 - Y
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick.get_button(4) and not button4Pressed):               # 360 - L1
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick.get_button(5) and not button5Pressed):               # 360 - R1
                        button5Pressed = True
                        sendFAST()
                    elif (joystick.get_button(6) and not button6Pressed):               # 360 - L3
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(7) and not button7Pressed):               # 360 - R3
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(8) and not button8Pressed):               # 360 - Start
                        button8Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(9) and not button9Pressed):               # 360 - Back
                        button9Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(10) and not button10Pressed):             # 360 - XBOX
                        button10Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(11) and not button11Pressed):             # 360 - Up
                        button11Pressed = True
                        sendGOFirst()
                    elif (joystick.get_button(12) and not button12Pressed):             # 360 - Down
                        button12Pressed = True
                        sendGOLast()
                    elif (joystick.get_button(13) and not button13Pressed):             # 360 - Left
                        button13Pressed = True
                        sendGOBack()
                    elif (joystick.get_button(14) and not button14Pressed):             # 360 - Right
                        button14Pressed = True
                        sendGOFwd()

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging and not joy2Xmoving and not joy2Ymoving:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                        joy1Xmoving = True
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                        joy1Xmoving = True
                    else:
                        axisX = 0
                        joy1Xmoving = False

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0))) *-1
                        joy1Ymoving = True
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255))) *-1
                        joy1Ymoving = True
                    else:
                        #axisY = 0
                        joy1Ymoving = False

                if not sliderKeyPresseed and not sliderCircle_draging and not joy2sliding:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                        joy1sliding = True
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                        joy1sliding = True
                    else:
                        axisZ = 0
                        joy1sliding = False

                        '''
            elif joyNimbus in joystickName:
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # Nimbus - A
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick.get_button(1) and not button1Pressed):               # Nimbus - B
                        button1Pressed = True
                        sendAddPos()               
                    elif (joystick.get_button(2) and not button2Pressed):               # Nimbus - X
                        button2Pressed = True
                        sendExecMoves()
                    elif (joystick.get_button(3) and not button3Pressed):               # Nimbus - Y
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick.get_button(4) and not button4Pressed):               # Nimbus - L1
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick.get_button(5) and not button5Pressed):               # Nimbus - R1
                        button5Pressed = True
                        sendFAST()
                    elif (joystick.get_button(6) and not button6Pressed):               # Nimbus - L3
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(7) and not button7Pressed):               # Nimbus - R3
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(8) and not button8Pressed):               # Nimbus - Start
                        button8Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(9) and not button9Pressed):               # Nimbus - Back
                        button9Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(10) and not button10Pressed):             # Nimbus - XBOX
                        button10Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(11) and not button11Pressed):             # Nimbus - Up
                        button11Pressed = True
                        sendGOFirst()
                    elif (joystick.get_button(12) and not button12Pressed):             # Nimbus - Down
                        button12Pressed = True
                        sendGOLast()
                    elif (joystick.get_button(13) and not button13Pressed):             # Nimbus - Left
                        button13Pressed = True
                        sendGOBack()
                    elif (joystick.get_button(14) and not button14Pressed):             # Nimbus - Right
                        button14Pressed = True
                        sendGOFwd()

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = -(joystick.get_axis(1))

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0

            elif (joySN30 in joystickName) or (joySN30BT in joystickName):

                hat = joystick.get_hat(0)
                hatX = hat[0]
                hatY = hat[1]
                if (hatX != oldHatX):
                    oldHatX = hatX
                    if hatX == 1:                                                       # RIGHT
                        sendGOFwd()
                    if hatX == -1:                                                      # LEFT
                        sendGOBack()

                if (hatY != oldHatY):
                    oldHatY = hatY
                    if hatY == 1:                                                       # UP
                        sendGOFirst()
                    if hatY == -1:                                                      # DOWN
                        sendGOLast()

                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # SN30 - B
                        button0Pressed = True
                        sendEditPos()
                        #print("0 - B") 
                    elif (joystick.get_button(1) and not button1Pressed):               # SN30 - A
                        button1Pressed = True
                        sendAddPos()
                        #print("1 - A")
                    elif (joystick.get_button(2) and not button2Pressed):               # SN30 - Heart
                        button2Pressed = True
                        sendExecMoves()
                        #print("2 - Heart")
                    elif (joystick.get_button(3) and not button3Pressed):               # SN30 - X
                        button3Pressed = True
                        sendClearArray()
                        #print("3 - X")
                    elif (joystick.get_button(4) and not button4Pressed):               # SN30 - Y
                        button4Pressed = True
                        sendREPORTall()
                        #print("4 - Y")
                    #elif (joystick.get_button(5) and not button5Pressed):               # SN30 - None
                    #    button5Pressed = True
                    #    sendREPORTall()
                        #print("5 - None")
                    elif (joystick.get_button(6) and not button6Pressed):               # SN30 - L1
                        button6Pressed = True
                        sendSLOW()
                        #print("6 - L1")
                    elif (joystick.get_button(7) and not button7Pressed):               # SN30 - R1
                        button7Pressed = True
                        sendFAST()
                        #print("7 - R1")
                    elif (joystick.get_button(8) and not button8Pressed):               # SN30 - L2
                        button8Pressed = True
                        sendREPORTall()
                        #print("8 - L2")
                    elif (joystick.get_button(9) and not button9Pressed):               # SN30 - R2
                        button9Pressed = True
                        sendREPORTall()
                        #print("9 - R2")
                    elif (joystick.get_button(10) and not button10Pressed):             # SN30 - Select
                        button10Pressed = True
                        sendREPORTall()
                        #print("10 - Select")
                    elif (joystick.get_button(11) and not button11Pressed):             # SN30 - Start
                        button11Pressed = True
                        sendREPORTall()
                        #print("11 - Start")
                    #elif (joystick.get_button(12) and not button12Pressed):             # SN30 - None
                    #    button10Pressed = True
                    #    sendREPORTall()
                        #print("12 - None")
                    elif (joystick.get_button(13) and not button13Pressed):             # SN30 - L3
                        button13Pressed = True
                        sendREPORTall()
                        #print("13 - L3")
                    elif (joystick.get_button(14) and not button14Pressed):             # SN30 - R3
                        button14Pressed = True
                        sendREPORTall()
                        #print("14 - R3")

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisX = 0

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisY = 0

                if not sliderKeyPresseed and not sliderCircle_draging:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                    else:
                        axisZ = 0
            else:
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                 # A
                        button0Pressed = True
                        sendEditPos()
                    if (joystick2.get_button(0) and not button0Pressed):                 # A
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick.get_button(1) and not button1Pressed):               # B
                        button1Pressed = True
                        sendAddPos()        
                    elif (joystick2.get_button(1) and not button1Pressed):               # B
                        button1Pressed = True
                        sendAddPos()              
                    elif (joystick.get_button(2) and not button2Pressed):               # X
                        button2Pressed = True
                        sendExecMoves()  
                    elif (joystick2.get_button(2) and not button2Pressed):               # X
                        button2Pressed = True
                        sendExecMoves()
                    elif (joystick.get_button(3) and not button3Pressed):               # Y
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick2.get_button(3) and not button3Pressed):               # Y
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick.get_button(4) and not button4Pressed):               # L1
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick2.get_button(4) and not button4Pressed):               # L1
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick.get_button(5) and not button5Pressed):               # R1
                        button5Pressed = True
                        sendFAST()
                    elif (joystick2.get_button(5) and not button5Pressed):               # R1
                        button5Pressed = True
                        sendFAST()
                    elif (joystick.get_button(6) and not button6Pressed):               # L2
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(6) and not button6Pressed):               # L2
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(7) and not button7Pressed):               # R2
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(7) and not button7Pressed):               # R2
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick.get_button(8) and not button8Pressed):               # Up
                        button8Pressed = True
                        sendGOFirst()
                    elif (joystick2.get_button(8) and not button8Pressed):               # Up
                        button8Pressed = True
                        sendGOFirst()
                    elif (joystick.get_button(9) and not button9Pressed):               # Down
                        button9Pressed = True
                        sendGOLast()
                    elif (joystick2.get_button(9) and not button9Pressed):               # Down
                        button9Pressed = True
                        sendGOLast()
                    elif (joystick.get_button(10) and not button10Pressed):             # Right
                        button10Pressed = True
                        sendGOFwd()
                    elif (joystick2.get_button(10) and not button10Pressed):             # Right
                        button10Pressed = True
                        sendGOFwd()
                    elif (joystick.get_button(11) and not button11Pressed):             # Left
                        button11Pressed = True
                        sendGOBack()
                    elif (joystick2.get_button(11) and not button11Pressed):             # Left
                        button11Pressed = True
                        sendGOBack()
                    elif (joystick.get_button(12) and not button12Pressed):             # Menu
                        button12Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(12) and not button12Pressed):             # Menu
                        button12Pressed = True
                        sendREPORTall()

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging and not joy2moving:
                    joyXread = joystick.get_axis(0)
                    joyYread = joystick.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                        joy1moving = True
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                        joy1moving = True
                    else:
                        axisX = 0
                        joy1moving = False

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                        joy1moving = True
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                        joy1moving = True
                    else:
                        axisY = 0
                        joy1moving = False

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging and not joy1moving and (joystickName2 != ''):
                    joyXread = joystick2.get_axis(0)
                    joyYread = joystick2.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                        joy2moving = True
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                        joy2moving = True
                    else:
                        axisX = 0
                        joy2moving = False

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                        joy2moving = True
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                        joy2moving = True
                    else:
                        axisY = 0
                        joy2moving = False

                if not sliderKeyPresseed and not sliderCircle_draging and not joy2sliding:
                    joyZread = joystick.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                        joy1sliding = True
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                        joy1sliding = True
                    else:
                        axisZ = 0
                        joy1sliding = False

                if not sliderKeyPresseed and not sliderCircle_draging and not joy1sliding and (joystickName2 != ''):
                    joyZread = joystick2.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                        joy2sliding = True
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                        joy2sliding = True
                    else:
                        axisZ = 0
                        joy2sliding = False
            '''
            

        if joystick2 == '':
            pass
        else:
            if (joyPS4 in joystickName2) or (joyPS4BT in joystickName2) or (joyPS4Win in joystickName2):
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick.get_button(0) and not button0Pressed):                  # PS4 - Cross
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick2.get_button(0) and not button0Pressed):               # PS4 - Cross
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick2.get_button(1) and not button1Pressed):               # PS4 - Circle
                        button1Pressed = True
                        sendAddPos()
                    elif (joystick2.get_button(2) and not button2Pressed):               # PS4 - Square
                        button2Pressed = True
                        sendExecMoves()
                    elif (joystick2.get_button(3) and not button3Pressed):               # PS4 - Triangle
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick2.get_button(4) and not button4Pressed):               # PS4 - Share
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick2.get_button(5) and not button5Pressed):               # PS4 - PS
                        button5Pressed = True
                        sendFAST()
                    elif (joystick2.get_button(6) and not button6Pressed):               # PS4 - Option
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(7) and not button7Pressed):               # PS4 - L3
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(8) and not button8Pressed):               # PS4 - R3
                        button8Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(9) and not button9Pressed):               # PS4 - L1
                        button9Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(10) and not button10Pressed):             # PS4 - R1
                        button10Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(11) and not button11Pressed):             # PS4 - UP
                        button11Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(12) and not button12Pressed):             # PS4 - DOWN
                        button12Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(13) and not button13Pressed):             # PS4 - LEFT
                        button13Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(14) and not button14Pressed):             # PS4 - RIGHT
                        button14Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(15) and not button15Pressed):             # PS4 - Pad
                        button15Pressed = True
                        sendREPORTall()

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging and not joy1Xmoving and not joy1Ymoving:
                    joyXread = joystick2.get_axis(0)
                    joyYread = joystick2.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                        joy2Xmoving = True
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                        joy2Xmoving = True
                    else:
                        axisX = 0
                        joy2Xmoving = False

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0)))
                        joy2Ymoving = True
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255)))
                        joy2Ymoving = True
                    else:
                        axisY = 0
                        joy2Ymoving = False

                if not sliderKeyPresseed and not sliderCircle_draging and not joy1sliding:
                    joyZread = joystick2.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                        joy2sliding = True
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                        joy2sliding = True
                    else:
                        axisZ = 0
                        joy2sliding = False

            elif joy360 in joystickName2:
                if event.type == pygame.JOYBUTTONDOWN:
                    if (joystick2.get_button(0) and not button0Pressed):              # 360 - A
                        button0Pressed = True
                        sendEditPos()
                    elif (joystick2.get_button(1) and not button1Pressed):               # 360 - B
                        button1Pressed = True
                        sendAddPos()
                    elif (joystick2.get_button(2) and not button2Pressed):               # 360 - X
                        button2Pressed = True
                        sendExecMoves()
                    elif (joystick2.get_button(3) and not button3Pressed):               # 360 - Y
                        button3Pressed = True
                        sendClearArray()
                    elif (joystick2.get_button(4) and not button4Pressed):               # 360 - L1
                        button4Pressed = True
                        sendSLOW()
                    elif (joystick2.get_button(5) and not button5Pressed):               # 360 - R1
                        button5Pressed = True
                        sendFAST()
                    elif (joystick2.get_button(6) and not button6Pressed):               # 360 - L3
                        button6Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(7) and not button7Pressed):               # 360 - R3
                        button7Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(8) and not button8Pressed):               # 360 - Start
                        button8Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(9) and not button9Pressed):               # 360 - Back
                        button9Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(10) and not button10Pressed):             # 360 - XBOX
                        button10Pressed = True
                        sendREPORTall()
                    elif (joystick2.get_button(11) and not button11Pressed):             # 360 - Up
                        button11Pressed = True
                        sendGOFirst()
                    elif (joystick2.get_button(12) and not button12Pressed):             # 360 - Down
                        button12Pressed = True
                        sendGOLast()
                    elif (joystick2.get_button(13) and not button13Pressed):             # 360 - Left
                        button13Pressed = True
                        sendGOBack()
                    elif (joystick2.get_button(14) and not button14Pressed):             # 360 - Right
                        button14Pressed = True
                        sendGOFwd()

                if not panKeyPresseed and not tiltKeyPresseed and not joyCircle_draging and not joy1Xmoving and not joy1Ymoving:
                    joyXread = joystick2.get_axis(0)
                    joyYread = joystick2.get_axis(1)

                    if (joyXread < deadRangeLow):
                        axisX = int(scale(joyXread, (-1.0,deadRangeLow), (-255,0)))
                        joy2Xmoving = True
                    elif (joyXread > deadRangeHigh):
                        axisX = int(scale(joyXread, (deadRangeHigh,1.0), (0,255)))
                        joy2Xmoving = True
                    else:
                        axisX = 0
                        joy2Xmoving = False

                    if (joyYread < deadRangeLow):
                        axisY = int(scale(joyYread, (-1.0,deadRangeLow), (-255,0))) *-1
                        joy2Ymoving = True
                    elif (joyYread > deadRangeHigh):
                        axisY = int(scale(joyYread, (deadRangeHigh,1.0), (0,255))) *-1
                        joy2Ymoving = True
                    else:
                        axisY = 0
                        joy2Ymoving = False

                if not sliderKeyPresseed and not sliderCircle_draging and not joy1sliding:
                    joyZread = joystick2.get_axis(2)

                    if (joyZread < deadRangeLow):
                        axisZ = int(scale(joyZread, (-1.0,deadRangeLow), (-255,0)))
                        joy2sliding = True
                    elif (joyZread > deadRangeHigh):
                        axisZ = int(scale(joyZread, (deadRangeHigh,1.0), (0,255)))
                        joy2sliding = True
                    else:
                        axisZ = 0
                        joy2sliding = False

            

        if event.type == pygame.JOYBUTTONUP:
            if (button0Pressed and not joystick.get_button(0)):
                button0Pressed = False
            elif (button1Pressed and not joystick.get_button(1)):
                button1Pressed = False
            elif (button2Pressed and not joystick.get_button(2)):
                button2Pressed = False
            elif (button3Pressed and not joystick.get_button(3)):
                button3Pressed = False
            elif (button4Pressed and not joystick.get_button(4)):
                button4Pressed = False
            elif (button5Pressed and not joystick.get_button(5)):
                button5Pressed = False
            elif (button6Pressed and not joystick.get_button(6)):
                button6Pressed = False
            elif (button7Pressed and not joystick.get_button(7)):
                button7Pressed = False
            elif (button8Pressed and not joystick.get_button(8)):
                button8Pressed = False
            elif (button9Pressed and not joystick.get_button(9)):
                button9Pressed = False
            elif (button10Pressed and not joystick.get_button(10)):
                button10Pressed = False
            elif (button11Pressed and not joystick.get_button(11)):
                button11Pressed = False
            elif (button12Pressed and not joystick.get_button(12)):
                button12Pressed = False
            elif (button13Pressed and not joystick.get_button(13)):
                button13Pressed = False
            elif (button14Pressed and not joystick.get_button(14)):
                button14Pressed = False
            elif (button15Pressed and not joystick.get_button(15)):
                button15Pressed = False
            elif (button0Pressed and not joystick2.get_button(0)):
                button0Pressed = False
            elif (button1Pressed and not joystick2.get_button(1)):
                button1Pressed = False
            elif (button2Pressed and not joystick2.get_button(2)):
                button2Pressed = False
            elif (button3Pressed and not joystick2.get_button(3)):
                button3Pressed = False
            elif (button4Pressed and not joystick2.get_button(4)):
                button4Pressed = False
            elif (button5Pressed and not joystick2.get_button(5)):
                button5Pressed = False
            elif (button6Pressed and not joystick2.get_button(6)):
                button6Pressed = False
            elif (button7Pressed and not joystick2.get_button(7)):
                button7Pressed = False
            elif (button8Pressed and not joystick2.get_button(8)):
                button8Pressed = False
            elif (button9Pressed and not joystick2.get_button(9)):
                button9Pressed = False
            elif (button10Pressed and not joystick2.get_button(10)):
                button10Pressed = False
            elif (button11Pressed and not joystick2.get_button(11)):
                button11Pressed = False
            elif (button12Pressed and not joystick2.get_button(12)):
                button12Pressed = False
            elif (button13Pressed and not joystick2.get_button(13)):
                button13Pressed = False
            elif (button14Pressed and not joystick2.get_button(14)):
                button14Pressed = False
            elif (button15Pressed and not joystick2.get_button(15)):
                button15Pressed = False

        if event.type == pygame.USEREVENT:
            if (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED):
                sendSerial(event.text)
                serial_text_entry.set_text('')

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == rel_button_Clear:
                    sendClearArray()
                elif event.ui_element == rel_button_AddPos:
                    sendAddPos()
                elif event.ui_element == rel_button_EditPos:
                    sendEditPos()
                elif event.ui_element == rel_button_GOFirst:
                    sendGOFirst()
                elif event.ui_element == rel_button_GOBack:
                    sendGOBack()
                elif event.ui_element == rel_button_GOFwd:
                    sendGOFwd()
                elif event.ui_element == rel_button_GOLast:
                    sendGOLast()
                elif event.ui_element == rel_button_Refresh:
                    doRefresh()
                elif event.ui_element == rel_button_ExecMoves:
                    sendExecMoves()
                elif event.ui_element == rel_button_OrbitPoint:
                    sendOrbitPoint()
                elif event.ui_element == rel_button_Timelapse:
                    sendTimelapse()
                elif event.ui_element == rel_button_PANORAMICLAPSE:
                    sendPanoramicLapse()
                elif event.ui_element == rel_button_REPORT:
                    sendREPORTall()
                elif event.ui_element == rel_button_CLEARtext:
                    sendCLEARtext()

            if (event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == drop_down_serial):
                serialPort_changed()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:            
                if joyCircle.collidepoint(event.pos):
                    joyCircle_draging = True
                    mouse_x, mouse_y = event.pos
                    offset_x = joyCircle.x - mouse_x
                    offset_y = joyCircle.y - mouse_y

                if sliderCircle.collidepoint(event.pos):
                    sliderCircle_draging = True
                    mouse_x, mouse_y = event.pos
                    sliderOffset_x = sliderCircle.x - mouse_x
                    sliderOffset_y = sliderCircle.y - mouse_y

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if joyCircle_draging:
                    joyCircle_draging = False
                    joyCircle.x = 195
                    joyCircle.y = 195
                    axisX = int(0)
                    axisY = int(0)

                if sliderCircle_draging:
                    sliderCircle_draging = False
                    sliderCircle.x = 195
                    sliderCircle.y = 415
                    axisZ = int(0)

                mouseMoving = False

        if event.type == pygame.MOUSEMOTION:
            if joyCircle_draging:
                mouseMoving = True
                mouse_x, mouse_y = event.pos
                joyCircle.x = mouse_x
                joyCircle.y = mouse_y
                if ((mouse_x + offset_x) > mouseBorder) and ((mouse_y + offset_y) > mouseBorder):
                    joyCircle.x = mouseBorder
                    joyCircle.y = mouseBorder

                elif (((mouse_x + offset_x) > mouseBorder) and ((mouse_y + offset_y) < 30)):
                    joyCircle.x = mouseBorder
                    joyCircle.y = 30

                elif (((mouse_x + offset_x) < 30) and ((mouse_y + offset_y) > mouseBorder)):
                    joyCircle.x = 30
                    joyCircle.y = mouseBorder

                elif (((mouse_x + offset_x) < 30) and ((mouse_y + offset_y) < 30)):
                    joyCircle.x = 30
                    joyCircle.y = 30

                elif ((mouse_x + offset_x) > (mouseBorder)):
                    joyCircle.x = mouseBorder
                    joyCircle.y = mouse_y + offset_y

                elif ((mouse_x + offset_x) < 30):
                    joyCircle.x = 30
                    joyCircle.y = mouse_y + offset_y

                elif ((mouse_y + offset_y) > (mouseBorder)):
                    joyCircle.y = mouseBorder
                    joyCircle.x = mouse_x + offset_x

                elif ((mouse_y + offset_y) < 30):
                    joyCircle.y = 30
                    joyCircle.x = mouse_x + offset_x

                else:
                    joyCircle.x = mouse_x + offset_x
                    joyCircle.y = mouse_y + offset_y

                axisX = int(scale((joyCircle.x), (30,mouseBorder), (-255,255)))
                axisY = int(scale((joyCircle.y), (30,mouseBorder), (-255,255)))

            if sliderCircle_draging:
                mouseMoving = True
                mouse_x, mouse_y = event.pos
                sliderCircle.x = mouse_x
                sliderCircle.y = 420
                if ((mouse_x + sliderOffset_x) > mouseBorder):
                    sliderCircle.x = mouseBorder

                elif ((mouse_x + sliderOffset_x) < 30):
                    sliderCircle.x = 30

                else:
                    sliderCircle.x = mouse_x + sliderOffset_x

                axisZ = int(scale((sliderCircle.x), (30,mouseBorder), (-255,255)))

        axisXDOT = scale(axisX, (-255,255), (-1.0,1.0))
        axisYDOT = scale(axisY, (-255,255), (-1.0,1.0))
        axisZDOT = scale(axisZ, (-255,255), (-1.0,1.0))

        joyCircle.x = (axisXDOT*165)+210-radius
        joyCircle.y = (axisYDOT*165)+210-radius
        sliderCircle.x = (axisZDOT*165)+210-radius

ui_manager.set_focus_set(textBoxSerial)

while running:
    time_delta = clock.tick() / 1000.0
    time_delta_stack.append(time_delta)
    
    process_events()                                               # check for input

    if (((axisX != oldAxisX) or (axisY != oldAxisY) or (axisZ != oldAxisZ)) and ((time.time() - previousTime) > 0.1)):
        previousTime = time.time()
        oldAxisX = axisX
        oldAxisY = axisY
        oldAxisZ = axisZ
        axisXh = tohex(axisX, 16)
        axisYh = tohex(-axisY, 16)
        axisZh = tohex(axisZ, 16)

        arr = [4, axisZh, axisXh, axisYh]
        sendJoystick(arr)
        #print(4,' - ', axisZh, ' - ', axisXh, ' - ', axisYh)

    try:
        readSerial()
    except:
        ser=''
        current_serialPort = ['']
        serialNotSel = 'Serial port disconnected.<br>'
        textBoxSerial.kill()
        serialText = serialText + serialNotSel
        serialPortTextBox()   
        ports = serial.tools.list_ports.comports()                              # Search for attached serial ports
        available_ports = []
        for p in ports:
            available_ports.append(p.device)                                    # Append each found serial port to array available_ports

        drop_down_serial.kill()
        drop_down_serial = UIDropDownMenu(available_ports,                      # Recreate serial port drop down list
                                        available_ports[0],                  # Currently selected port
                                        pygame.Rect((620,95),
                                        (250, 30)),
                                        ui_manager)

    ui_manager.update(time_delta)                                               # respond to input

    window_surface.blit(background_surface, (0, 0))                             # draw graphics

    ui_manager.draw_ui(window_surface)                                          # draw UI

    window_surface.blit(textsurfaceW,(198,28))                                  # W
    window_surface.blit(textsurfaceA,(35,190))                                  # A
    window_surface.blit(textsurfaceS,(205,355))                                 # S
    window_surface.blit(textsurfaceD,(365,190))                                 # D
    window_surface.blit(textsurfaceLeft,(35,415))                               # ,
    window_surface.blit(textsurfaceRight,(375,415))                             # .
    
    pygame.draw.circle(window_surface, RED, (joyCircle.x+radius,joyCircle.y+radius), radius)
    pygame.draw.circle(window_surface, RED, (sliderCircle.x+radius,430), radius)

    pygame.draw.rect(window_surface, [125,0,0], [30,30,360,360],width=3)
    pygame.draw.rect(window_surface, [125,0,0], [30,400,360,60],width=3)

    pygame.display.update()

    clk.tick(40)