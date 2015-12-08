import SocketServer
import time
import mraa
import os
from subprocess import Popen

"""
THIS IS THE DIRTY SCRIPT USED IN HITCON CTF FINAL 2015 TO CONTROL THE LIGHT SABER
"""

light_on = 0

def LightOff():
    for led in leds:
        led.write(1)

def Light(level, sound):
    global light_on
    light_on += 1
    if level &gt; len(leds):
        level = len(leds)

    if sound:
        p = Popen(['madplay', '-S', '/root/fx4.mp3'])

    time.sleep(0.2)

    for i in range(level):
        time.sleep(0.05)
        leds[i].write(0)
        light_on -= 1

    time.sleep(1.0)

    if sound:
        p.terminate()
        p = Popen(['madplay', '-S', '/root/fx5.mp3'])

    time.sleep(0.8)

    if light_on == 0:
        for i in range(level)[::-1]:
            time.sleep(0.05)
            leds[i].write(1)

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        if data == "PING":
            self.request.sendall("PONG\n")
        else:
            level = int(data)
            if level == 0:
                # turn off all the leds
                global light_on
                light_on = 0
                LightOff()
            elif level == 100:
                # turn on all the les
                for led in leds:
                    led.dir(mraa.DIR_OUT)
                    led.write(0)
            elif level &gt;= 10:
                # Light up the saber without sound
                # level = 11 ~ 16
                Light(level - 10, False);
            else:
                # Light up the saber with sound
                # level = 1 ~ 6
                Light(level, True)

            self.request.sendall("OK\n")

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999

    print "Initializing GPIO ..."
    global leds
    leds = [mraa.Gpio(i) for i in range(14, 20)]

    # Turn off all the leds
    for led in leds:
        led.dir(mraa.DIR_OUT)
        led.write(1)

    # Show that leds are initialized
    for i in range(3):
        for led in leds:
            led.write(0)
            time.sleep(0.1)
            led.write(1)

    print "Initializing Server ... "
    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)

    print "Server Started!"
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

