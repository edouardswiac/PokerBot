# coding: utf-8

# %load ImageProcessor.py
# %load ImageProcessor.py
#%save ImageProcessor.py 12

from scipy import ndimage
from deuces.card import Card
from scipy import misc
from scipy import ndimage
import matplotlib.pyplot as plt
import numpy as np
from pytesser import *
import os
import PIL
import time
import pyautogui as gui
import re
import time
get_ipython().magic(u'matplotlib inline')

class Frame(): 
    def __init__(self, blinds = .05):
        '''Locate the Bovada window and initialize variables '''
    
        ## initialize the bovada logo reference image
        ## Everytime the bovada frame moves, we must relocate the Bovada logo as a reference point
        self.BOVADA_REF_IMG = PIL.Image.open("reference_images/BOVADA.png")
        
        self.blinds = blinds
        
        ## These are the coordinates of where the important values
        ## exist in the frame, relative to the bovada logo
        ## top left and bottom right coords of bounding box
        self.LOCATIONS = {
                'hole1' : ((353, 428),(401, 496)), 
                'hole2' : ((403, 428),(451, 496)), 
                'board1' : ((269,242), (317, 310)),
                'board2' : ((323,242), (371, 310)), 
                'board3' : ((377,242), (425, 310)),
                'board4' : ((431,242), (479, 310)), 
                'board5' : ((485,242), (533, 310)),
                'pot'    : ((350, 312), (470, 330)),
                'blinds' : ((0, 35), (150, 50)),
                'textBar': ((670, 590),(750, 605)),
                'fold'   : ((420, 560), (520, 580)),
                'call'   : ((530, 560), (630, 580)),
                'check'   : ((530, 560), (630, 580)),
                'stack0' : ((380, 470), (480, 495)),
                'stack1' : ((70, 395), (170, 420)),
                'stack2' : ((70, 180), (170, 205)),
                'stack3' : ((330, 105), (430, 130)),
                'stack4' : ((630, 180), (730, 205)),
                'stack5' : ((630, 395), (730, 420)),
                'bet0'   : ((390, 410),(490, 425)),
                'bet1'   : ((190, 355), (300, 370)),
                'bet2'   : ((190, 230), (300, 245)),
                'bet3'   : ((400, 172), (500, 185)),
                'bet4'   : ((560, 232), (680, 245)),
                'bet5'   : ((580, 347), (680, 360))
        }                  
        
        
        
        ## Coordinates of where dealer button can exist
        self.DEALER_LOC = [(264, 422),(137,302),(220, 165),(530, 150),(660, 275),(570, 408)]
        
        ## save a screen shot   
        os.system("screencapture screenshots/test.jpg")
        
        ## locate the bovada symbol on screen to find the bovada window
        try:
            self.x,self.y,width,height = gui.locate(self.BOVADA_REF_IMG, PIL.Image.open("screenshots/test.jpg"))
        except TypeError:
            raise Exception("Can't locate frame")

             
        ## save the bovada application window (as an image)
        img = misc.imread('screenshots/test.jpg', flatten = True)
        self.frame = img[self.y:self.y + 650, self.x:self.x + 750]  
        
        
        ## load the suit reference functions used to identify card suits
        self.SUIT_REF_FUNCTIONS = []
        heart = misc.imread("reference_images/suits/HEART.jpg", flatten = True)
        diamond = misc.imread("reference_images/suits/DIAMOND.jpg", flatten = True)
        spade = misc.imread("reference_images/suits/SPADE.jpg", flatten = True)
        club = misc.imread("reference_images/suits/CLUB.jpg", flatten = True) 
        self.SUIT_REF_FUNCTIONS.append(('h', heart.sum(axis = 1)))
        self.SUIT_REF_FUNCTIONS.append(('c', club.sum(axis = 1)))
        self.SUIT_REF_FUNCTIONS.append(('d', diamond.sum(axis = 1)))
        self.SUIT_REF_FUNCTIONS.append(('s', spade.sum(axis = 1)))
        
        
    def update(self, sound = False):
        #Takes a picture of the frame, assuming the frame has not moved from previous position
        if sound:
            os.system("screencapture screenshots/test.jpg")
        else:
             os.system("screencapture -x screenshots/test.jpg")
            
        img = misc.imread('screenshots/test.jpg', flatten = True)
        self.frame = img[self.y:self.y + 650, self.x:self.x + 750]  
        
    
    
    def identify_card(self, card_str):
        '''Locates card on screen given by card_str parameter and returns a string identifying the card.
           As is Ace of spades, Tc is ten of clubs, etc.
           
           params : hole1, hole2, board1, board2, ect...'''
              
        v = self.LOCATIONS[card_str]
        card_img = self.frame[v[0][1]:v[1][1], v[0][0]:v[1][0]] 
        num_img = card_img[2:19, 0:19]
        suit_img = card_img[19:35, :17]
         
        
        ## identify the number
        blank = np.ones((num_img.shape[0] * 2, num_img.shape[1] * 7))*245
        for i in range(0, 20*6, 20):
            blank[:num_img.shape[0], i :num_img.shape[1] + i] = num_img
               
        num_img = PIL.Image.fromarray(np.uint8(blank))
        num_str =  image_to_string(num_img)
        
        ## tesseract reads 10 as 1 because it's just grabbing the first digit    
        try:
            num_str = num_str[0]
            if num_str == '1':
                num_str = 'T'
        except IndexError:
            return None
        
        
    
        f = suit_img.sum(axis = 1)
        diff = lambda x : abs((f**2 - x[1]**2).sum())
        suit_str = min(self.SUIT_REF_FUNCTIONS, key = diff)[0]
                
        
        return num_str + suit_str
    
    
    def read_value(self, loc):
        pos = self.LOCATIONS[loc]
        v = self.frame[pos[0][1]:pos[1][1], pos[0][0]:pos[1][0]]
        x,y = v.shape
        f = PIL.Image.fromarray(np.uint8(v))
        #f.show()
        basewidth = 300
        wpercent = (basewidth/float(f.size[0]))
        hsize = int((float(f.size[1])*float(wpercent)))
        img = f.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
        #img.show()
        s = image_to_string(img)
        #print s
        
        
        if loc is 'blinds':
            non_decimal = re.compile(r'[^\d,]+')
            s = non_decimal.sub(' ', s)
            s = s.replace(',', '')
            s = s.split(' ')[1]
            
        else:
            non_decimal = re.compile(r'[^\d.]+')
            s = non_decimal.sub('', s)
        
        try:
            return float(s)
        except ValueError:
            return None
                 
    def bet(self, n):
        if self.read_value('stack0') > n:
            v = self.LOCATIONS['textBar']
            gui.moveTo(np.random.randint(v[0][0] + self.x, v[1][0] + self.x),
                       np.random.randint(v[0][1] + self.y, v[1][1] + self.y), 
                       duration = .5)
            gui.click()
            gui.typewrite(str(n), interval=0.25)
            gui.press('enter')
        else:
            v = self.LOCATIONS['textBar']
            gui.moveTo(v[0][0] + self.x + 10, v[1][1] + self.y + 10)
            gui.click()
        
    
    def fold(self):
        if self.user_position() is 'BB' and self.bets().max() == self.blinds:
            v = self.LOCATIONS['call']      
        else:  
            v = self.LOCATIONS['fold']
            
        gui.moveTo(v[0][0] + self.x + 50, v[0][1] + self.y + 10, duration = .3) 
        time.sleep(.3)
        gui.mouseDown()
        time.sleep(.2)
        gui.mouseUp()
        
    def call(self):
        v = self.LOCATIONS['call']
        gui.moveTo(v[0][0] + self.x + 50, v[0][1] + self.y + 10, duration = .3) 
        time.sleep(.3)
        gui.mouseDown()
        time.sleep(.2)
        gui.mouseUp()
        
        


    def user_position(self):
        positions = ['BTN', 'SB', 'BB','UTG', 'MP', 'CO']
        color = lambda x : self.frame[x[1], x[0]]
        button = self.DEALER_LOC.index(max(self.DEALER_LOC, key = color))
        return positions[(6 - button) % 6]
    
    def in_hand(self):
        in_hand = np.empty(6, dtype='bool')
        for i in range(6):
            pos = self.LOCATIONS['stack%s'%i]
            slice = self.frame[pos[0][1]:pos[1][1], pos[0][0]:pos[1][0]]
            in_hand[i] = len(slice[slice > 200]) > 50
        return in_hand
    
    def bets(self):
        bets = np.zeros(5)
        for i in range(1, 6):
            bet = self.read_value('bet%s'%i)
            if bet is None:
                bet = 0.0
            bets[i - 1] = bet
            
        return bets
   
            
    
    def is_user_turn(self):
        img = misc.imread('screenshots/test.jpg', flatten = False)
        img = img[self.y:self.y + 650, self.x:self.x + 750]  
        
        slice = img[500:515, 330:450]
        slice = slice.reshape(slice.shape[0]*slice.shape[1], 4)
        yellow_mask = (slice[:,0] > 200) & (slice[:,1] > 200) & (slice[:,2] == 0)
        
        return len(slice[yellow_mask]) > 0
    
   
    
    
    
    
                
