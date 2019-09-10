#!/usr/bin/env python3
import sys
import MySQLdb
from threading import Thread
import threading
import time
import RPi.GPIO as GPIO
import json
import serial
from random import randint
from evdev import InputDevice
from select import select
#from twilio.rest import Client

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4,GPIO.OUT)

try:
	# python 2
	import Tkinter as tk
	import ttk
except ImportError:
	# python 3
	import tkinter as tk
	from tkinter import ttk
	
class Fullscreen_Window:

    global dbHost
    global dbName
    global dbUser
    global dbPass
    
    dbHost = 'localhost'
    dbName = 'door_lock'
    dbUser = 'root'
    dbPass = 'Darph303!'

    def __init__(self):
        self.tk = tk.Tk()
        self.tk.title("Three-Factor Authentication Security Door Lock")
        self.frame = tk.Frame(self.tk)
	self.frame.grid()
        self.tk.columnconfigure(0, weight=1)
        
        self.tk.attributes('-zoomed', True)
        self.tk.attributes('-fullscreen', True)
        self.state = True
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.tk.config(cursor="none")
	self.tk.config(background='black')
        
        self.show_idle()
        
        t = Thread(target=self.listen_rfid)
        t.daemon = True
        t.start()
        
    def show_idle(self):
       	self.image = tk.PhotoImage(file="nsticon2.png")
	self.photoLabel = ttk.Label(self.tk, image=self.image)
	self.photoLabel.place(x=-1, y=-1, anchor='nw')
	self.welcomeLabel = ttk.Label(self.tk, text="Please Present Your Badge", background='black', foreground='white')
        self.welcomeLabel.config(font='size, 40', justify='center', anchor='center',) 
        self.welcomeLabel.grid(sticky=tk.W+tk.E, pady='200') 
    
    def pin_entry_forget(self):
        self.validUser.grid_forget()
        self.photoLabel.grid_forget()
        self.enterPINlabel.grid_forget()
        count = 0
        while (count < 12):
            self.btn[count].grid_forget()
            count += 1
            
    def returnToIdle_fromPINentry(self):
        self.pin_entry_forget()
        self.show_idle()
    
    def returnToIdle_fromPINentered(self):
        self.PINresultLabel.grid_forget()
        self.show_idle()
    
    def returnToIdle_fromAccessGranted(self):
        GPIO.output(4,GPIO.LOW)
	self.SMSresultLabel.grid_forget()
	self.show_idle()
    
    def returnToIdle_fromSMSentry(self):
        
	self.PINresultLabel.grid_forget()	
	self.smsDigitsLabel.grid_forget()
        count = 0
        while (count < 12):
            self.btn[count].grid_forget()
            count += 1
        self.show_idle()
        
    def	returnToIdle_fromSMSentered(self):
        self.SMSresultLabel.grid_forget()
	self.show_idle()
        
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"
        
    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"
        
    def listen_rfid(self):
        global pin
        global accessLogId
        
	keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
        s = serial.Serial('/dev/ttyS0',9600,bytesize=8,parity='N',stopbits=1)
	rfid_presented = ""
	data = ""

        while (True):
            
            r,w,x = select([s], [], [])
            if s.inWaiting() > 0:
               	#reads 16 bytes of data then closes session 
		data = s.read(16)
		#reads line, requires timeout to work. Not preferred 
		#data = s.readline().decode().strip()
                print(data)
		#s.close()
                if data!='':
                    dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
                    cur = dbConnection.cursor(MySQLdb.cursors.DictCursor)
                    cur.execute("SELECT * FROM access_list WHERE rfid_code = '%s'" % (data))
                    
                    if cur.rowcount != 1:
                        self.welcomeLabel.config(text="ACCESS DENIED", foreground='red')
                        
                        # Log access attempt
                        cur.execute("INSERT INTO access_log SET rfid_presented = '%s', rfid_presented_datetime = NOW(), rfid_granted = 0" % (data))
                        dbConnection.commit()
                        
			time.sleep(1)
                        self.welcomeLabel.grid_forget()
                        #self.pin_entry_forget() 
			#self.PINresultLabel.grid_forget() 
			self.show_idle()
                    else:
                        user_info = cur.fetchone()
                        userPin = user_info['pin']
                        self.welcomeLabel.grid_forget()
                        self.validUser = ttk.Label(self.tk, text="Welcome\n %s!" % (user_info['name']), font='size, 15', justify='center', anchor='center', background='black', foreground='white')
                        self.validUser.grid(columnspan=3)
                        
                        self.image = tk.PhotoImage(file=user_info['image'] + ".gif")
                        self.photoLabel = ttk.Label(self.tk, image=self.image)
                        self.photoLabel.grid(columnspan=3)
                        
                        self.enterPINlabel = ttk.Label(self.tk, text="Please enter your PIN:", font='size, 18', justify='center', anchor='center', background='black', foreground='white')
                        self.enterPINlabel.grid(columnspan=3)
                        pin = ''
                        
                        keypad = [
                            '1', '2', '3',
                            '4', '5', '6',
                            '7', '8', '9',
                            '*', '0', '#',
                            ]
								
                        # create and position all buttons with a for-loop
                        # r, c used for row, column grid values
                        r = 4 
                        c = 0
                        n = 0
                        # list(range()) needed for Python3
                        self.btn = list(range(len(keypad)))
                        for label in keypad:
                            # partial takes care of function and argument
                            #cmd = partial(click, label)
                            # create the button
                            self.btn[n] = tk.Button(self.tk, text=label, font='size, 18', width=16, height=2, background='black', foreground='white', command=lambda digitPressed=label:self.codeInput(digitPressed, userPin, user_info['sms_number']))
                            # position the button
                            self.btn[n].grid(row=r, column=c)
                            # increment button index
                            n += 1
                            # update row/column position
                            c += 1
                            if c > 2:
                                c = 0
                                r += 1
                        
                        
                        # Log access attempt
                        cur.execute("INSERT INTO access_log SET rfid_presented = '%s', rfid_presented_datetime = NOW(), rfid_granted = 1" % (data))
                        dbConnection.commit()
                        accessLogId = cur.lastrowid
                        

                        self.PINentrytimeout = threading.Timer(5, self.returnToIdle_fromPINentry)
                        self.PINentrytimeout.start()
                        
                        self.PINenteredtimeout = threading.Timer(5, self.returnToIdle_fromPINentered)
                        
                rfid_presented = ""
		data = ""
                dbConnection.close()
            else:
                #s = serial.Serial('/dev/ttyUSB0',9600)
                #data = s.readline()
                #keys = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"
                #rfid_presented = ""
                rfid_presented += keys[ data ]
		data = ""
                
    def codeInput(self, value, userPin, mobileNumber):
        global accessLogId
        global pin
        global smsCodeEntered
        pin += value
        pinLength = len(pin)
        
        self.enterPINlabel.config(background='black', foreground='white', text="Digits Entered: %d" % pinLength)
        
        if pinLength == 6:
			self.PINentrytimeout.cancel()
			self.pin_entry_forget()
			
			if pin == userPin:
				pin_granted = 1
			else:
				pin_granted = 0
			
			# Log access attempt
			dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
			cur = dbConnection.cursor()
			cur.execute("UPDATE access_log SET pin_entered = '%s', pin_entered_datetime = NOW(), pin_granted = %s, mobile_number = '%s' WHERE access_id = %s" % (pin, pin_granted, mobileNumber, accessLogId))
			dbConnection.commit()
			
			#if pin == userPin:
				#self.PINresultLabel = ttk.Label(self.tk, text="Thank You, Now\nPlease Enter Code\nfrom SMS\n")
				#self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				#self.PINresultLabel.grid(columnspan=3, sticky=tk.W+tk.E, pady=20)
				
				#self.smsDigitsLabel = ttk.Label(self.tk, text="Digits Entered: 0", font='size, 18', justify='center', anchor='center')
				#self.smsDigitsLabel.grid(columnspan=3, sticky=tk.W+tk.E)
				
				#smsCode = self.sendSMScode(mobileNumber)
				#smsCodeEntered = ''
				
				#keypad = [
				#	'1', '2', '3',
				#	'4', '5', '6',
				#	'7', '8', '9',
				#	'', '0', '',
				#]
								
				# create and position all buttons with a for-loop
				# r, c used for row, column grid values
				#r = 4
				#c = 0
				#n = 0
				# list(range()) needed for Python3
				#self.btn = list(range(len(keypad)))
				#for label in keypad:
					# partial takes care of function and argument
					#cmd = partial(click, label)
					# create the button
					#self.btn[n] = tk.Button(self.tk, text=label, font='size, 18', width=4, height=1, command=lambda digitPressed=label:self.smsCodeEnteredInput(digitPressed, smsCode))
					# position the button
					#self.btn[n].grid(row=r, column=c, ipadx=10, ipady=10)
					# increment button index
					#n += 1
					# update row/column position
					#c += 1
					#if c > 2:
						#c = 0
                        #r += 1
				
				#self.SMSentrytimeout = threading.Timer(60, self.returnToIdle_fromSMSentry)
				#self.SMSentrytimeout.start()
				
			#else:
				#self.PINresultLabel = ttk.Label(self.tk, text="Incorrect PIN Entered!", background='black', foreground='red')
				#self.PINresultLabel.config(font='size, 20', justify='center', anchor='center')
				#self.PINresultLabel.grid(sticky=tk.W+tk.E, pady=210)
				#self.PINenteredtimeout.start()
				
	#def smsCodeEnteredInput(self, value, smsCode):
		#global smsCodeEntered
		#global accessLogId
		#smsCodeEntered += value
		#smsCodeEnteredLength = len(smsCodeEntered)
		
		#self.smsDigitsLabel.config(text="Digits Entered: %d" % smsCodeEnteredLength)
		
		#if smsCodeEnteredLength == 6:
			#self.SMSentrytimeout.cancel()
			#self.pin_entry_forget()
			
			#if smsCodeEntered == smsCode:
				#smscode_granted = 1
			#else:
				#smscode_granted = 0
			
			# Log access attempt
			#dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
			#cur = dbConnection.cursor()
			#cur.execute("UPDATE access_log SET smscode_entered = '%s', smscode_entered_datetime = NOW(), smscode_granted = %s WHERE access_id = %s" % (smsCodeEntered, smscode_granted, accessLogId))
			#dbConnection.commit()
			
			if pin_granted == 1:
                		self.SMSresultLabel = ttk.Label(self.tk, text="Thank You, Access Granted", background='black', foreground='green')
                		self.SMSresultLabel.config(font='size, 40', justify='center', anchor='center')
                		self.SMSresultLabel.grid(columnspan=10, sticky=tk.W+tk.E+tk.N+tk.S, pady='200')
                
                		#self.enterPINlabel.grid_forget()
                		#self.enterPINlabel_forget()
				#self.smsDigitsLabel.grid_forget()
				GPIO.output(4,GPIO.HIGH)
				
				self.doorOpenTimeout = threading.Timer(5, self.returnToIdle_fromAccessGranted)
				self.doorOpenTimeout.start()
			else:
                		#self.enterPINlabel.grid_forget()
                		#self.enterPINlabel_forget()
				#self.smsDigitsLabel.grid_forget()
				
				self.SMSresultLabel = ttk.Label(self.tk, text="Incorrect PIN Code Entered!", background='black', foreground='red')
				self.SMSresultLabel.config(font='size, 40', justify='center', anchor='center')
				self.SMSresultLabel.grid(sticky=tk.W+tk.E+tk.N+tk.S, pady='200')
				
				self.SMSenteredtimeout = threading.Timer(1, self.returnToIdle_fromSMSentered)
				self.SMSenteredtimeout.start()
				
	#def sendSMScode(self, mobileNumber):
	
		# Retreive our Twilio access credentials and "from" number
		#dbConnection = MySQLdb.connect(host=dbHost, user=dbUser, passwd=dbPass, db=dbName)
		#cur = dbConnection.cursor(MySQLdb.cursors.DictCursor)
		#cur.execute("SELECT account_sid, auth_token, twilio_sms_number FROM twilio_api_credentials WHERE id = 1")
		#credentials = cur.fetchone()
		#account_sid = credentials['account_sid']
		#auth_token = credentials['auth_token']
		#twilio_sms_number = credentials['twilio_sms_number']
		#dbConnection.close()
				
		#smsCode = str(randint(100000, 999999))
		#messageText = "Your access code is %s. Please enter this on the touchscreen to continue." % smsCode

		#client = Client(account_sid, auth_token)
		#message = client.messages.create(
		#	to=mobileNumber, 
		#	from_=twilio_sms_number,
		#	body=messageText)
		
		#return smsCode

if __name__ == '__main__':
	w = Fullscreen_Window()
	w.tk.mainloop()
