#!/usr/bin/python
from Adafruit_Thermal import *
import os
import PIL
import pprint
from PIL import Image
import RPi.GPIO as GPIO
from time import sleep
import sys

print("Init printer\n")
printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)
printer.boldOn()

GPIO.setmode(GPIO.BOARD)

GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18,True)

if( len(sys.argv) > 1 and sys.argv[1] == 'launch'):
  GPIO.output(18,False)
  printer.feed(1)
  printer.justify('C')
  printer.println("............................\nRaspberry Pi bitcoin wallet\ngenerator is ready.\n\nPress button to create a wallet.\n\nHold button for shut down\n................................\n")
  printer.feed(3)
  GPIO.output(18,True)

while(GPIO.input(23) == 1):
  sleep(.05)

sleep(1)

if(GPIO.input(23) != 1):
  printer.justify('C')
  printer.println("Shutting system down, do not\nunplug until button light goes\n out.");  
  printer.feed(3)
  printer.setDefault()
  printer.sleep()
  print "Shutting down\n"
  os.popen('/sbin/shutdown -h 0')
  print "Shutdown signal sent";
  while True:
    print "Tick\n";
    sleep(1)

GPIO.output(18,False)

keydata = os.popen('/home/pi/vanitygen-master/vanitygen -s /dev/random 1').read().split("\n")
address = keydata[1].split(": ")[1]
privkey = keydata[2].split(": ")[1]

n = 3
addressPrint = ' '.join( [address[i:i+n] for i in range(0, len(address), n)] )
privkeyPrint = ' '.join( [privkey[i:i+n] for i in range(0, len(privkey), n)] )

os.popen('qrencode -lH -o /dev/shm/address.png "'+address+'"').read();
os.popen('qrencode -lH -o /dev/shm/privkey.png "'+privkey+'"').read();                    

basewidth = 300

img = Image.open("/dev/shm/address.png")
if img.size[1] < img.size[0]:
  img2 = img.rotate(270)
else:
  img2 = img

wpercent = (basewidth/float(img2.size[0]))
hsize = int((float(img2.size[1])*float(wpercent)))
img2 = img2.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
img2 = img2.convert('1')
img2.save("/dev/shm/address.bmp")

img = Image.open("/dev/shm/privkey.png")
if img.size[1] < img.size[0]:
  img2 = img.rotate(270)
else:
  img2 = img

wpercent = (basewidth/float(img2.size[0]))
hsize = int((float(img2.size[1])*float(wpercent)))
img2 = img2.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
img2 = img2.convert('1')
img2.save("/dev/shm/privkey.bmp")

printer.justify('L')
printer.feed(1)
printer.println( "Address:\n\n", addressPrint )
printer.printImage(Image.open("/dev/shm/address.bmp"))
printer.feed(2)
printer.println('_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ ');
printer.feed(2)
printer.println( "PrivKey:\n\n", privkeyPrint )
printer.printImage(Image.open("/dev/shm/privkey.bmp"))
printer.justify('C')
printer.println(addressPrint);
printer.feed(3)
printer.setDefault()
printer.sleep()

GPIO.cleanup()

os.unlink('/dev/shm/address.png');
os.unlink('/dev/shm/address.bmp');
os.unlink('/dev/shm/privkey.png');
os.unlink('/dev/shm/privkey.bmp');
