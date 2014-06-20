#!/usr/bin/python
  
import RPi.GPIO as GPIO
import time
 
class keypad():
    def __init__(self, callback):
        GPIO.setmode(GPIO.BCM)
        self._count = 0
        self._inInterrupt = False
        self._callback = callback
 
        # CONSTANTS 
        self.KEYPAD = [
            [1,2,3],
            [4,5,6],
            [7,8,9],
            ["*",0,"#"]
        ]
 
        #hook the rows (1,4,7,*) to these GPIO pins
        self.ROW         = [18,23,24,25]
        #hook the columns (1,2,3) to these GPIO pins
        self.COLUMN      = [4,17,22]
 
        self.__setInterruptMode()
 
    def __colInt(self, channel):
        time.sleep(0.05) #give it a moment to settle
        if GPIO.input(channel) > 0:
            return
 
        #remove interrupts temporarily
        for c in range(len(self.COLUMN)):
            GPIO.remove_event_detect(self.COLUMN)
 
        #get column number
        colVal = -1
        for c in range(len(self.COLUMN)):
            if channel == self.COLUMN:
                colVal = c
 
        #continue if valid column (it should always be)
        if colVal >=0 and colVal < len(self.COLUMN):
 
            #set rows as intputs
            for r in range(len(self.ROW)):
                GPIO.setup(self.ROW[r], GPIO.IN, pull_up_down=GPIO.PUD_UP)
 
            #set triggered column as low output
            GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)
 
            # Scan rows for pushed key/button
            rowVal = -1
            for r in range(len(self.ROW)):
                tmpRead = GPIO.input(self.ROW[r])
                if tmpRead == 0:
                    rowVal = r
                    break
 
            #continue if row is valid (possible that it might not be if the key was very quickly released)
            if rowVal >= 0 and rowVal < len(self.ROW):
                #send key info right away
                self._callback(self.KEYPAD[rowVal][colVal])
                #This avoids nasty boucning errors when the key is released
                #By waiting for the rising edge before re-enabling interrupts it 
                #avoids interrupts fired due to bouncing on key release and 
                #any repeated interrupts that would otherwise fire.
                try:
                    GPIO.wait_for_edge(self.ROW[rowVal], GPIO.RISING)
                    self.__setInterruptMode()
                except RuntimeError:
                    pass
                 
                return
 
            else:
                print "Invalid Row!"
        else:
            print "Invalid Col!"
 
        #re-enable interrupts
        self.__setInterruptMode()
 
    def __changeWrapper(self, channel):
        #if there is already another interrupt going on (multiple key press or something)
        #return right away to avoid collisions
        if self._inInterrupt:
            return;
 
        self._inInterrupt = True
        self.__colInt(channel) #handle the actual interrupt
        self._inInterrupt = False
 
    def __setInterruptMode(self):
        #set the first row as output low
        #only first one needed as it will ground to all columns
        for r in range(len(self.ROW)):
            GPIO.setup(self.ROW[r], GPIO.OUT, initial=GPIO.LOW)
 
        #set columns as inputs and attach interrupt handlers on rising edge
        for c in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[c], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self.COLUMN[c], GPIO.FALLING, bouncetime=250, callback=self.__changeWrapper)
      
 
    def cleanup(self):
        GPIO.cleanup()
        print "Cleanup done!"
		
import time     
if __name__ == '__main__':
    def keypadCallback(value):
        print "Keypad: " + value

    key = keypad(keypadCallback)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        key.cleanup()