
import threading as th
import cv2 ,time, clipboard,sys, os, math as m
import pygame as pg 
import random as r
import pyautogui as p
from pynput.mouse import Controller as M, Button as B
from pynput.keyboard import Listener, Controller as K
from cvzone.HandTrackingModule import HandDetector
from cvzone.FaceMeshModule import FaceMeshDetector

os.environ['SDL_VIDEO_CENTERED'] = '1'
pg.init()
pg.display.set_caption("avatar")
WIDTH, HEIGHT = 500, 500
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
font = None
particles = []
colors = []
color = [250, 10, 150]
num = [-1, 1, -1]
cap = cv2.VideoCapture(0)

class Particle():
    def __init__(self, pos, velocity, shape, color,time):
        self.pos = pg.Vector2()
        self.velocity = pg.Vector2()
        self.pos.x, self.pos.y = pos
        self.velocity.x, self.velocity.y = velocity
        self.r = shape[0]
        self.shape = shape[1]
        self.color = color
        self.grav_scale = time[2]
        self.time = r.randrange(time[0], time[1])
        self.grav = r.randrange(5, 10)
        particles.append(self)
    def draw(self, screen):
        screens = pg.Surface((screen.get_size()), pg.SRCALPHA)
        self.time -= 1
        if self.grav_scale != None:
            self.grav -= self.grav_scale
            self.pos.x += self.velocity.x 
            self.pos.y += self.velocity.y + self.grav
        else:
            self.pos.x += self.velocity.x
            self.pos.y += self.velocity.y
        p = (self.pos[0] + r.randrange(self.r * -1, self.r), self.pos[1] + r.randrange(self.r * -1, self.r))
        a = (self.pos[0] + r.randrange(self.r * -1, self.r), self.pos[1] + r.randrange(self.r * -1, self.r))
        b =(self.pos[0] + r.randrange(self.r * -1, self.r), self.pos[1] + r.randrange(self.r * -1, self.r))
        self.points = [(self.pos[0], self.pos[1]), p,b, a]
        if self.shape == 'c':
            pg.draw.circle(screen, self.color, (self.pos), self.r)
            pg.draw.circle(screens, (self.color[0], self.color[1], self.color[2], 50), (self.pos), self.r + 5)
        elif self.shape == 'r':
            pg.draw.rect(screen, self.color, (self.pos[0], self.pos[1], self.r, self.r))
            pg.draw.rect(screens, (self.color[0], self.color[1], self.color[2], 50), (self.pos[0], self.pos[1], self.r + 5, self.r + 5))
        elif self.shape == 'p':
            pg.draw.polygon(screen, self.color,self.points, 3)
            pg.draw.polygon(screens, (self.color[0], self.color[1], self.color[2], 50),self.points,8)
        screen.blit(screens, (0,0))
        if self.time <= 0:
            particles.remove(self)
class Label():
    def __init__(self, text, pos, color = 'Black',shade=['Gray','Gray'], rotate = 0, size = 20, bg = 'White', outline='Black', side = 'center'):
        self.font = pg.font.Font(font,size)
        self.font_size = size
        self.display = self.font.render(str(text), True, color)
        self.rect_new = self.display.get_rect()
        self.side = 'self.rect_new.' + side + ' = (pos)'
        exec(self.side)
        self.rect_new.w += self.font_size
        self.rect_new.h += self.font_size
        self.display = pg.transform.rotate(self.display, rotate)
        if bg != None:
            if rotate == 90 or rotate == 270:
                if shade[1] != None:
                    pg.draw.rect(screen, (shade[1]), (self.rect_new.x - self.font_size/2+5, self.rect_new.y - self.font_size/2+5, self.rect_new.h, self.rect_new.w), 0, 10)
                pg.draw.rect(screen, (bg), (self.rect_new.x - self.font_size/2, self.rect_new.y - self.font_size/2, self.rect_new.h, self.rect_new.w), 0, 10)
                if outline != None:
                    pg.draw.rect(screen, (outline), (self.rect_new.x - self.font_size/2, self.rect_new.y - self.font_size/2, self.rect_new.h, self.rect_new.w), 3, 10)
            else:
                if shade[1] != None:
                    pg.draw.rect(screen, (shade[1]), (self.rect_new.x - self.font_size/2+5, self.rect_new.y - self.font_size/2+5, self.rect_new.w, self.rect_new.h), 0, 10)
                pg.draw.rect(screen, (bg), (self.rect_new.x - self.font_size/2, self.rect_new.y - self.font_size/2, self.rect_new.w, self.rect_new.h), 0, 10)
                if outline != None:
                    pg.draw.rect(screen, (outline), (self.rect_new.x - self.font_size/2, self.rect_new.y - self.font_size/2, self.rect_new.w, self.rect_new.h), 3, 10)
        if shade[0] != None:
            self.shade = self.font.render(str(text), True, shade[0])
            self.shade = pg.transform.rotate(self.shade, rotate)
            screen.blit(self.shade, (self.rect_new.x + 4, self.rect_new.y + 4))
        screen.blit(self.display, (self.rect_new))
        self.rect = pg.Rect(self.rect_new.x - self.font_size/2, self.rect_new.y - self.font_size/2, self.rect_new.w, self.rect_new.h)
class Button():
    def __init__(self, text, pos, group,  size = 20, shade = ['Gray', 'Gray'], color='Black', bg='White', outline = 'Black', side = 'center'):
        self.clicked = False
        self.bg = bg
        self.outline = outline
        self.shade = shade
        self.side = side
        self.font = pg.font.Font(font,size)
        self.display = self.font.render(str(text), True, color)
        if shade[0] != None:
            self.shade_display = self.font.render(str(text), True, shade[0])
        self.font_size = size
        self.rect_new = self.display.get_rect()
        self.side = 'self.rect_new.' + side + ' = (pos)'
        exec(self.side)
        self.rect_new.w += self.font_size
        self.rect_new.h += self.font_size
        self.offset = 0
        self.rect = pg.Rect(-720, -720, 0, 0)
        group.append(self)
    def draw(self):
        if self.shade[1] != None:
            pg.draw.rect(screen,(self.shade[1]), (self.rect_new.x - self.font_size/2, self.rect_new.y-self.font_size/2, self.rect_new.w + 5, self.rect_new.h + 5), 0, 10)
        if self.bg != None:
            pg.draw.rect(screen,(self.bg), (self.rect_new.x - self.font_size/2 + self.offset , self.rect_new.y-self.font_size/2 + self.offset, self.rect_new.w, self.rect_new.h), 0, 10)
        if self.outline != None:
            pg.draw.rect(screen,(self.outline), (self.rect_new.x - self.font_size/2 + self.offset, self.rect_new.y-self.font_size/2 + self.offset, self.rect_new.w , self.rect_new.h), 3, 10)
        if self.shade[0] != None:
            screen.blit(self.shade_display, (self.rect_new.x + self.offset + 5, self.rect_new.y + self.offset + 5))
        screen.blit(self.display, (self.rect_new.x + self.offset , self.rect_new.y + self.offset))
        self.rect = pg.Rect(self.rect_new.x - self.font_size/2 + self.offset, self.rect_new.y-self.font_size/2 + self.offset, self.rect_new.w, self.rect_new.h)
    def choice(self, pos):
        mouse = pg.mouse.get_pos()
        action = False
        try:
            if self.rect.collidepoint(pos):
                self.clicked = True
                action = True
                return action
        except:
            pass
        if self.rect.collidepoint(mouse) and pg.mouse.get_pressed()[0] == 1:
            self.clicked = True
            action = True
            return action
class Input():
    def __init__(self, text, pos, num, size = 20, color='Black',bg='White', shade=['Gray', "Gray"], type=str, sides=['center', 'center'], outline = 'black'):
        self.num = num + 1
        self.outline = outline
        self.text = text[0]
        self.rect_new = pg.Rect(0,0,0,0)
        self.rect_new.center = (pos)
        self.clicked = False
        self.output = text[1]
        self.type = type       
        self.offset = 0
        self.size = size
        self.output_rect = None
        self.shade = shade
        self.bg = bg
        self.color = color
        self.sides = sides
    def draw(self,event, single = False):
        pos = pg.mouse.get_pos()
        if pg.mouse.get_pressed()[0] ==1 and self.output_rect != None:
            if self.output_rect.rect.collidepoint(pos):
                self.clicked = True
        if pg.mouse.get_pressed()[0] == 1 and self.clicked:
            if not self.output_rect.rect.collidepoint(pos):
                self.clicked = False
        if self.clicked:
            for event in event:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        self.output = self.output[:-1]
                    elif len(self.output) + 1 < self.num and not single:
                        if self.type == str:
                            self.output += event.unicode
                        elif event.key != 1073742051:
                            try:
                                send = event.unicode
                                send = int(send)
                                self.output += str(send)
                            except:
                                pass
                        if event.key == pg.K_v and pg.key.get_mods() & pg.KMOD_CTRL:
                            self.output = self.output[:-1]
                            text = clipboard.paste()
                            self.output += text
                    elif len(self.output) + 1 < self.num and single:
                        self.output = event.key
                    else:
                        self.clicked = False
        if self.text != '':
            Label(self.text, (self.rect_new.center),shade=self.shade, bg=self.bg, color=self.color, size = self.size, side=self.sides[0])
            if self.clicked:
                self.output_rect = Label(self.output + '|', (self.rect_new.centerx, self.rect_new.bottom +self.rect_new.h*2 + self.size*2 + 20),shade=self.shade, bg=self.bg, color=self.color, size = self.size, side=self.sides[1], outline=self.outline)
            else:
                self.output_rect = Label(self.output, (self.rect_new.centerx, self.rect_new.bottom + self.rect_new.h*2 + self.size*2 + 20),shade=self.shade, bg=self.bg, color=self.color, size = self.size, side=self.sides[1], outline=self.outline)
        else:
            if self.clicked:
                self.output_rect = Label(self.output + '|', (self.rect_new.center),shade=self.shade, bg=self.bg, color=self.color, size = self.size, side=self.sides[1], outline=self.outline)
            else:
                self.output_rect = Label(self.output, (self.rect_new.center),shade=self.shade, bg=self.bg, color=self.color, size = self.size, side=self.sides[1], outline=self.outline)
    def choice(self):
        if not self.clicked:
            return self.output
class Switch():
    def __init__(self,text, pos, turn, color = 'Black', shade = ['Gray', 'Gray'], size = 20, bg = 'White', outline= 'Black', sides='center'):
        self.font_size = size 
        self.turn = turn
        self.size = size/5
        self.text = text
        self.pos = pos
        self.circle = pg.Vector2()
        self.clicked = False
        self.rect_new = pg.Rect(pos[0]-size*1.5, pos[1], size *3, size)
        self.rect = pg.Rect(pos[0], pos[1], size *3, size)
        self.max = self.rect_new.right - 5
        self.least = self.rect_new.left + 5
        self.circle.x = self.least
        self.circle.y = self.rect_new.centery
        self.side = sides
        self.color = color
        self.bg = bg
        self.outline = outline
        self.shades = shade
    def draw(self):
        pos = pg.mouse.get_pos()
        if pg.mouse.get_pressed()[0] ==1 :
            if self.rect_new.collidepoint(pos) and  not self.clicked:
                self.clicked = True
                if self.turn:
                    self.turn= False
                elif not self.turn:
                    self.turn = True
        if pg.mouse.get_pressed()[0] == 0:
            self.size = self.font_size/1.5 + 2
        
        if pg.mouse.get_pressed()[0] == 0 and self.clicked:
            self.clicked = False
        elif pg.mouse.get_pressed()[0] == 0 and not self.rect_new.collidepoint(pos):
            self.size = self.font_size/1.5
        if self.turn:
            self.color_circle = 'Green'
            self.circle.x = self.max
        elif not self.turn: 
            self.color_circle = 'Red'
            self.circle.x = self.least
        pg.draw.rect(screen, ('White'), (self.rect_new), 0, 15)
        pg.draw.rect(screen, ('Gray'), (self.rect_new), 0, 15)
        pg.draw.rect(screen, (self.color_circle), (self.rect_new), 0, 15)
        pg.draw.rect(screen, ('Black'), (self.rect_new), 3, 15)
        pg.draw.circle(screen, ('white'), (self.circle.x, self.circle.y), self.size)
        pg.draw.circle(screen, ('Black'), (self.circle.x, self.circle.y), self.size, 2)
        Label(self.text, (self.rect.x, self.rect.centery - self.font_size - self.rect_new.w/10 - 5), size=self.font_size, side=self.side, shade=self.shades, outline=self.outline, bg=self.bg, color = self.color)
    def choice(self):
        if self.turn:
            return True
        else:
            return False
class Dot:
    def __init__(self, pos, color, size):
        self.g = 0.2
        self.M = 10e7
        self.mass = 1
        self.x = pos[0]
        self.y = pos[1]
        self.momentum_x = 500
        self.momentum_y = 500
        self.dt = 0.005
        self.color = color
        self.size = size
        self.random_dir = pg.Vector2(r.randint(-10,10), r.randint(-10,10))
    def random(self):
        self.x += self.random_dir.x
        self.y += self.random_dir.y
    def move(self, x_y_central_mass):
        x2 = x_y_central_mass[0]
        y2 = x_y_central_mass[1]
        hyp = (self.x - x2) ** 2 + (self.y - y2) ** 2
        theta = m.atan2(y2 - self.y, x2 - self.x)
        force = (self.g * self.mass * self.M) / hyp
        force_x = force * m.cos(theta)
        force_y = force * m.sin(theta)
        self.momentum_x += force_x * self.dt
        self.momentum_y += force_y * self.dt
        self.x += self.momentum_x / self.mass * self.dt
        self.y += self.momentum_y / self.mass * self.dt
    def draw(self, screens):
        pg.draw.circle(screen, self.color,(self.x, self.y),self.size)
        pg.draw.circle(screens, (self.color[0], self.color[1], self.color[1], 50),(self.x, self.y), self.size*2)
class Hands():
    def __init__(self):
        self.hand = HandDetector(maxHands=1, detectionCon=0.9)
        self.palm = []
        self.fingers_list = {1:[], 2:[], 3:[], 4:[], 5:[]}
        self.fingers = []
        self.points = []
        self.draw_work = False
        self.color_pen = (255, 0, 0)
        self.drawing_list = []
        self.spread_out = False
        self.drawing_timer = 0
        self.lmList1 = None
        self.draw_work = False
        self.work = True
        self.pos = [0,0]
        self.length = 1
        self.hands_down = False
        self.gravity = False
        self.labels = {1:[], 2:[]}
        self.momentum = pg.Vector2(500,500)
    def update(self, img, draw, event):
        red = Button(' ', (WIDTH-50, 20),colors,  outline='White', shade=[None,None], size=30, bg=(255, 0, 0), side='bottomleft')
        blue = Button(' ', (WIDTH-90, 20),colors,  outline='White', shade=[None,None], size=30, bg=(0, 0, 255), side='bottomleft')
        green = Button(' ', (WIDTH-130, 20), colors, outline='White', shade=[None,None], size=30, bg=(0, 255, 0), side='bottomleft')
        yellow = Button(' ', (WIDTH-170, 20), colors, outline='White', shade=[None,None], size=30, bg=(255, 255, 0), side='bottomleft')
        purple = Button(' ', (WIDTH-210, 20), colors, outline='White', shade=[None,None], size=30, bg=(255, 0, 255), side='bottomleft')
        black = Button(' ', (WIDTH-250, 20), colors, outline='White', shade=[None,None], size=30, bg=(0, 0, 0), side='bottomleft')
        hands, img = self.hand.findHands(img)
        if hands:
            hand1 = hands[0]
            self.lmList1 = lmList1 = hand1['lmList']
            bbox1 = hand1['bbox'] 
            centerPoint1 = hand1['center']
            Handtype = hand1['type']
            self.fingers = self.hand.fingersUp(hand1)
            for i in range(len(lmList1)):
                if i in [0, 1, 2,3, 5,9,13,17]:
                    self.palm.append((int(abs(lmList1[i][0]/(1280/WIDTH)-WIDTH)),int(lmList1[i][1]/(720/HEIGHT))))
                if i in [4,3]:
                    a = (int(abs(lmList1[i][0]/(1280/WIDTH)-WIDTH)),int(lmList1[i][1]/(720/HEIGHT)))
                    self.fingers_list[1].append((a[0], a[1]))
                if i in [5, 6,7,8]:
                    a = (int(abs(lmList1[i][0]/(1280/WIDTH)-WIDTH)),int(lmList1[i][1]/(720/HEIGHT)))
                    self.fingers_list[2].append((a[0], a[1]))
                if i in [9, 10, 11, 12]:
                    a = (int(abs(lmList1[i][0]/(1280/WIDTH)-WIDTH)),int(lmList1[i][1]/(720/HEIGHT)))
                    self.fingers_list[3].append((a[0], a[1]))
                if i in [13, 14, 15, 16]: 
                    a = (int(abs(lmList1[i][0]/(1280/WIDTH)-WIDTH)),int(lmList1[i][1]/(720/HEIGHT)))
                    self.fingers_list[4].append((a[0], a[1]))
                if i in [17, 18, 19, 20]:
                    a = (int(abs(lmList1[i][0]/(1280/WIDTH)-WIDTH)),int(lmList1[i][1]/(720/HEIGHT)))
                    self.fingers_list[5].append((a[0], a[1]))
                self.points.append((lmList1[i][0]/(1280/WIDTH), lmList1[i][1]/(720/HEIGHT), '1', 3))
        else:
            self.fingers = []
        if draw:
            if self.fingers != None and self.work:
                self.commands()
            self.draw(event)
    def draw(self, event):
        screens = pg.Surface((screen.get_size()), pg.SRCALPHA)
        #! drawing ------------------------------------
        for i in self.drawing_list:
            if self.spread_out:
                i.random()
            elif self.gravity:
                try:
                    i.move(self.pos)
                except:
                    pass
            i.draw(screens)
        #!hand -----------------------------------
        for i in self.points:
            a = (int(abs(i[0]-WIDTH)),int(i[1]))
            pg.draw.circle(screen, color, (a[0], a[1]), abs(i[3]))
            pg.draw.circle(screens, (color[0], color[1], color[2], 50), (a[0], a[1]), abs(i[3]) + 5)
            self.points.clear()
        try:
            pg.draw.polygon(screens, color, self.palm, 5)
            for i in range(1,6):
                pg.draw.lines(screens, color, False, self.fingers_list[i], 10)
                self.fingers_list[i].clear()
        except ValueError:
            pass
        self.palm.clear()
        #!color buttons -------------------------------------
        if self.draw_work:
            for i in colors:
                i.draw()
                if i.choice(self.pos):
                    self.color_pen = i.bg
        colors.clear()
        #!labels --------
        if not self.draw_work:
            for i in self.labels[1]:
                i.draw(event)
                if i.output == '':
                    self.labels[2].append(i.clicked)
                    for j in event:
                        if j.type == pg.KEYUP:
                            if j.key == pg.K_BACKSPACE:
                                self.labels[1].pop()

                if i.clicked:
                    if self.fingers == [1,1,0,0,0]:
                        i.size = self.length
                    i.rect_new.center = pg.mouse.get_pos()
                    if self.fingers == [1,1,1,1,1]:
                        i.clicked = False

        screen.blit(screens, (0,0))
    def commands(self):
        global color
        #!pointing finger pos ------------------------------
        try:
            self.pos = (abs(self.lmList1[8][0]/(1280/WIDTH)-WIDTH), self.lmList1[8][1]/(720/HEIGHT))
        except:
            pass
        #! draw --------------------------------------------------
        if self.fingers == [0, 1, 0, 0, 0] and self.draw_work:
            self.drawing() 
        else:
            self.magic_timer = 0

        if self.fingers ==[1,0,0,0,1]:
            if not self.draw_work:
                self.drawing_timer += 1
                if self.drawing_timer > 20:
                    self.draw_work = True
                    self.spread_out = False
                    self.gravity = False
                    self.drawing_timer = 0
            if len(self.drawing_list) > 0:
                self.draw_work = False
                self.spread_out = False
                self.drawing_list.clear()
        #! dot random/gravity------------------
        if self.fingers == [0,0,0,0,0] or self.fingers == None:
            self.hands_down = True
        if self.fingers ==[1,1,1,1,1] and self.draw_work and self.hands_down:
            self.spread_out = not self.spread_out
            self.gravity = False
            self.hands_down = False
        elif self.fingers ==[0,1,1,1,1] and self.draw_work and self.hands_down:
            self.gravity = not self.gravity
            self.spread_out = False
            self.hands_down = False
        #!size -----------------------------------
        if self.fingers == [1,1,0,0,0]:
            x1, y1 = (abs(self.lmList1[4][0]/(1280/WIDTH)-WIDTH), self.lmList1[4][1]/(720/HEIGHT))
            x2, y2 = (abs(self.lmList1[8][0]/(1280/WIDTH)-WIDTH), self.lmList1[8][1]/(720/HEIGHT))
            pg.draw.line(screen, color, (x1,y1), (x2, y2))
            length = m.hypot(x2 - x1, y2 - y1)
            self.length = int(length/12)
            Label(self.length,  ((x2+x1)//2, (y2+y1)//2), outline=None, shade=[None,None], size=25, bg=None, color= color)
        #!Label ----------------------------------
        if self.fingers == [0,1,1,1,0] and not self.draw_work and False:
            print(self.labels[2])
            if len(self.labels[2]) < 1 or not all(self.labels[2]):
                a = Input(['',''], self.pos, 150, bg='black', shade=[None,None], outline='white', color='white')
                a.clicked = True
                self.labels[1].append(a)
            self.labels[2].clear()
    def drawing(self):
        a = Dot((abs(self.lmList1[8][0]/(1280/WIDTH)-WIDTH), self.lmList1[8][1]/(720/HEIGHT)), self.color_pen,self.length)
        self.drawing_list.append(a)
class Faces():
    def __init__(self):
        self.points = []
        self.face  = FaceMeshDetector(maxFaces=1)
        self.face_outline = {'pos': {},'id':[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]}
        self.forehead = {'pos': {}, 'id':[127,162, 21, 54, 103, 67, 109, 10, 338, 297,332, 284,251,389, 301,298,333,299,337,151,108,69,104,68,71,139]}
        self.hair = {'pos':{}, 'id':[301,298,333,299,337,151,108,69,104,68,71,139]}
        self.forehead_list = []
        self.lip_inner = {'pos': {},'id':[78,191,80,81,82,13,312,311,310,415,308,324,318,402,317,14,87,178,88,95]}
        self.lip_outer = {'pos': {},'id':[61,185,40,39,37,0,267,269,270,409,291,375,320,404,315,16,85,180,90,146]}
        self.eye_left = {'pos': {},'id':[33,246,161,160,159,158,157,173,133,155,154,153,145,144,163,7]}
        self.eye_right ={'pos': {},'id':[263,466,388,387,386,385,384,398,362,382,381,380,374,373,390,249]}
        self.eyes = {'pos': {},'id':[468,473 ]}
        self.eyebrow_left = {'pos': {},'id':[55,65,52,53,46]}
        self.eyebrow_right = {'pos': {},'id':[285,295,282,283,276]}
        self.iris_left = {'pos': {},'id':[468,469,470,471,472]}
        self.iris_right = {'pos': {},'id':[473,474,475,476,477]}
        self.list = [self.face_outline, self.lip_inner, self.lip_outer, self.eye_left,self.eye_right,self.eyebrow_left, self.eyebrow_right,self.iris_left, self.iris_right]
    def update(self, img, draw):
        img, faces = self.face.findFaceMesh(img)
        if self.face.results.multi_face_landmarks:
            for faceLms in self.face.results.multi_face_landmarks:
                for id, pos in enumerate(faceLms.landmark):
                    x = abs((pos.x*WIDTH)-WIDTH)
                    y = pos.y*HEIGHT
                    z = pos.z * 50
                    self.points.append([x,y,z, id])
        if draw:
            self.draw()
    def findmsall(self, list1:list, pos):
        new_list = []
        old_list = []
        for i in range(len(list1)-1):
            old_list.append(list1[i][pos])
        for i in range(50):
            old_list.sort()
            new_list.append(old_list[i])
        return new_list
    def face_draw(self):
        
        try:
            for i in range(len(self.face_outline['id'])-1):
                first, second = self.face_outline['id'][i], self.face_outline['id'][i+1]
                x1, y1 = self.face_outline['pos'][first][0], self.face_outline['pos'][first][1]
                x2, y2 = self.face_outline['pos'][second][0], self.face_outline['pos'][second][1]
                z = self.face_outline['pos'][first][2] 
                pg.draw.line(screen, color, (x1,y1), (x2,y2),int(z))
                if i == 34:
                    first, second = self.face_outline['id'][0], self.face_outline['id'][35]
                    x1, y1 = self.face_outline['pos'][first][0], self.face_outline['pos'][first][1]
                    x2, y2 = self.face_outline['pos'][second][0], self.face_outline['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), int(z))


            for i in range(len(self.forehead['id'])-1):
                first, second = self.forehead['id'][i], self.forehead['id'][i+1]
                x1, y1 = self.forehead['pos'][first][0], self.forehead['pos'][first][1]
                x2, y2 = self.forehead['pos'][second][0], self.forehead['pos'][second][1]
                self.forehead_list.append([x1,y1])
                pg.draw.line(screen, color, (x1,y1), (x2,y2))

            # for i in range(len(self.hair['id'])-1):
            #     first = self.hair['id'][i]
            #     x1, y1 = self.hair['pos'][first][0], self.hair['pos'][first][1]
            #     pg.draw.circle(screen, color, (x1,y1), r.randint(9,12))
            #     pg.draw.circle(screen, 'black', (x1,y1), r.randint(9,12),2)
        except KeyError:
            pass
        try:
            pg.draw.polygon(screen, color, self.forehead_list)
            self.forehead_list.clear()
        except:
            pass
    def eyes_draw(self):
        try:
            #!eyes------------------------------------------------------------------------------------
            for i in range(len(self.eye_left['id'])-1):
                first, second = self.eye_left['id'][i], self.eye_left['id'][i+1]
                x1, y1 = self.eye_left['pos'][first][0], self.eye_left['pos'][first][1]
                x2, y2 = self.eye_left['pos'][second][0], self.eye_left['pos'][second][1]
                pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
                if i == 14:
                    first, second = self.eye_left['id'][0], self.eye_left['id'][14]
                    x1, y1 = self.eye_left['pos'][first][0], self.eye_left['pos'][first][1]
                    x2, y2 = self.eye_left['pos'][second][0], self.eye_left['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)

            for i in range(len(self.eye_right['id'])-1):
                first, second = self.eye_right['id'][i], self.eye_right['id'][i+1]
                x1, y1 = self.eye_right['pos'][first][0], self.eye_right['pos'][first][1]
                x2, y2 = self.eye_right['pos'][second][0], self.eye_right['pos'][second][1]
                pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
                if i == 14:
                    first, second = self.eye_right['id'][0], self.eye_right['id'][14]
                    x1, y1 = self.eye_right['pos'][first][0], self.eye_right['pos'][first][1]
                    x2, y2 = self.eye_right['pos'][second][0], self.eye_right['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)



            #!eyebrow-----------------------------------------------------------------------------------------
            for i in range(len(self.eyebrow_left['id'])-1):
                first, second = self.eyebrow_left['id'][i], self.eyebrow_left['id'][i+1]
                x1, y1 = self.eyebrow_left['pos'][first][0], self.eyebrow_left['pos'][first][1]
                x2, y2 = self.eyebrow_left['pos'][second][0], self.eyebrow_left['pos'][second][1]
                pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
                if i == 8:
                    first, second = self.eyebrow_left['id'][0], self.eyebrow_left['id'][8]
                    x1, y1 = self.eyebrow_left['pos'][first][0], self.eyebrow_left['pos'][first][1]
                    x2, y2 = self.eyebrow_left['pos'][second][0], self.eyebrow_left['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)
            for i in range(len(self.eyebrow_right['id'])-1):
                first, second = self.eyebrow_right['id'][i], self.eyebrow_right['id'][i+1]
                x1, y1 = self.eyebrow_right['pos'][first][0], self.eyebrow_right['pos'][first][1]
                x2, y2 = self.eyebrow_right['pos'][second][0], self.eyebrow_right['pos'][second][1]
                pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
                if i == 8:
                    first, second = self.eyebrow_right['id'][0], self.eyebrow_right['id'][8]
                    x1, y1 = self.eyebrow_right['pos'][first][0], self.eyebrow_right['pos'][first][1]
                    x2, y2 = self.eyebrow_right['pos'][second][0], self.eyebrow_right['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)
            #!eyeballs----------------------------------------------------------------------------------------------
            x = self.eye_left['pos'][33][0] - (abs(self.eye_left['pos'][33][0] - self.eye_left['pos'][133][0])/2) 
            y = (abs(self.eye_left['pos'][159][1] - self.eye_left['pos'][145][1])/2) + self.eye_left['pos'][159][1]
            pg.draw.circle(screen, color, (x,y), 4, 1)
            x1 = self.eye_right['pos'][263][0] + (abs(self.eye_right['pos'][362][0] - self.eye_right['pos'][263][0])/2) 
            y1 = (abs(self.eye_right['pos'][386][1] - self.eye_right['pos'][374][1])/2) + self.eye_right['pos'][386][1]
            pg.draw.circle(screen, color, (x1,y1), 4, 1)
        except KeyError:
            pass
    def lips_draw(self):
        try:
            for i in range(len(self.lip_inner['id'])-1):
                first, second = self.lip_inner['id'][i], self.lip_inner['id'][i+1]
                x1, y1 = self.lip_inner['pos'][first][0], self.lip_inner['pos'][first][1]
                x2, y2 = self.lip_inner['pos'][second][0], self.lip_inner['pos'][second][1]
                pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
                if i == 18:
                    first, second = self.lip_inner['id'][0], self.lip_inner['id'][18]
                    x1, y1 = self.lip_inner['pos'][first][0], self.lip_inner['pos'][first][1]
                    x2, y2 = self.lip_inner['pos'][second][0], self.lip_inner['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)
            for i in range(len(self.lip_outer['id'])-1):
                first, second = self.lip_outer['id'][i], self.lip_outer['id'][i+1]
                x1, y1 = self.lip_outer['pos'][first][0], self.lip_outer['pos'][first][1]
                x2, y2 = self.lip_outer['pos'][second][0], self.lip_outer['pos'][second][1]
                pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
                if i == 18:
                    first, second = self.lip_outer['id'][0], self.lip_outer['id'][18]
                    x1, y1 = self.lip_outer['pos'][first][0], self.lip_outer['pos'][first][1]
                    x2, y2 = self.lip_outer['pos'][second][0], self.lip_outer['pos'][second][1]
                    pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)
        except KeyError:
            pass
    def iris_draw(self):
        for i in range(len(self.iris_left['id'])-1):
            first, second = self.iris_left['id'][i], self.iris_left['id'][i+1]
            x1, y1 = self.iris_left['pos'][first][0], self.iris_left['pos'][first][1]
            x2, y2 = self.iris_left['pos'][second][0], self.iris_left['pos'][second][1]
            pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
            # if i == 18:
            #     first, second = self.lip_inner['id'][0], self.lip_inner['id'][18]
            #     x1, y1 = self.lip_inner['pos'][first][0], self.lip_inner['pos'][first][1]
            #     x2, y2 = self.lip_inner['pos'][second][0], self.lip_inner['pos'][second][1]
            #     pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)
        for i in range(len(self.iris_right['id'])-1):
            first, second = self.iris_right['id'][i], self.iris_right['id'][i+1]
            x1, y1 = self.iris_right['pos'][first][0], self.iris_right['pos'][first][1]
            x2, y2 = self.iris_right['pos'][second][0], self.iris_right['pos'][second][1]
            pg.draw.line(screen, color, (x1,y1), (x2,y2),2)
            # if i == 18:
            #     first, second = self.lip_outer['id'][0], self.lip_outer['id'][18]
            #     x1, y1 = self.lip_outer['pos'][first][0], self.lip_outer['pos'][first][1]
            #     x2, y2 = self.lip_outer['pos'][second][0], self.lip_outer['pos'][second][1]
            #     pg.draw.line(screen, color, (x1,y1), (x2,y2), 2)
    def draw(self):
        screens = pg.Surface((screen.get_size()), pg.SRCALPHA)
        for i in self.points:
            if i[3] in self.face_outline['id']:
                self.face_outline['pos'][i[3]] = [i[0], i[1], i[2]]
            if i[3] in self.forehead['id']:
                self.forehead['pos'][i[3]] = [i[0], i[1], i[2]]
            if i[3] in self.hair['id']:
                self.forehead['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.lip_inner['id']:
                self.lip_inner['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.lip_outer['id']:
                self.lip_outer['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.eye_left['id']:
                self.eye_left['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.eye_right['id']:
                self.eye_right['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.eyebrow_left['id']:
                self.eyebrow_left['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.eyebrow_right['id']:
                self.eyebrow_right['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.iris_left['id']:
                self.iris_left['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.iris_right['id']:
                self.iris_right['pos'][i[3]] = [i[0], i[1], i[2]]
            elif i[3] in self.eyes['id']:
                self.eyes['pos'][i[3]] = [i[0], i[1], i[2]]
            else:
                pg.draw.circle(screen, color, (i[0], i[1]), 1)
                pg.draw.circle(screens, (color[0], color[1], color[2], 50), (i[0], i[1]), 5)
        screen.blit(screens, (0,0))
        self.face_draw()
        self.eyes_draw()
        self.lips_draw()
        for i in self.list:
            i['pos'].clear()
        self.points.clear()
class Pong():
    def __init__(self):
        self.player_rect = pg.Rect(0, 0, 30, 80)
        self.player_rect.center = (20, 250)
        self.player_points = 0
        self.player_speed = 6

        self.bot_rect = pg.Rect(0, 0, 30, 80)
        self.bot_rect.center = (480, 250)
        self.bot_speed = 6
        self.bot_points = 0

        self.ball_rect = pg.Rect(0, 0, 10, 10)
        self.ball_rect.center = (255, 255)
        self.ball_speed = pg.Vector2()
        self.ball_speed.x = r.choice((-1, 1))
        self.ball_speed.y = r.choice((-1, 1))
        self.ball_num = 2

        self.started = False
        self.prev_time = time.time()
    def update(self,y, work):
        Label(f"{self.player_points} : {self.bot_points}", (250, 20),color='orange', outline=None, shade=[None,None], size=25, bg=None)
        #self.player_rect.y = y
        now = time.time()
        dt = now - self.prev_time
        self.prev_time = now
        self.draw(y)
        if work:
            self.started = True
        if self.started:
            self.ball(self.ball_rect, self.player_rect, self.bot_rect, dt)
            self.player(self.player_rect, y, dt)
            self.bot(self.ball_rect, self.bot_rect, dt)
    def reset(self):
        self.player_rect = pg.Rect(0, 0, 30, 80)
        self.player_rect.center = (20, 250)

        self.bot_rect = pg.Rect(0, 0, 30, 80)
        self.bot_rect.center = (480, 250)
        self.bot_speed = 5

        self.ball_rect = pg.Rect(0, 0, 10, 10)
        self.ball_rect.center = (255, 255)
        self.ball_speed = pg.Vector2()
        self.ball_speed.x = r.choice((-1, 1)) 
        self.ball_speed.y = r.choice((-1, 1)) 

        self.ball_num = 2
        self.started = False
    def ball(self, ball, player, bot, dt):
        ball.x += self.ball_speed.x * dt * 40 * self.ball_num
        ball.y += self.ball_speed.y * dt * 40 * self.ball_num
        #player collusions 
        if ball.colliderect(player):
            if abs(ball.right - player.left) < 10 and self.ball_speed.x >0:
                ball.right = player.left
                self.ball_speed.x *= -1
                self.ball_num += 0.1
            if abs(ball.left - player.right) < 10 and self.ball_speed.x <0:
                ball.left = player.right
                self.ball_speed.x *= -1
                self.ball_num += 0.1
            if abs(ball.top - player.bottom) < 10 and self.ball_speed.y <0:
                ball.top = player.bottom
                self.ball_speed.x *= -1
                self.ball_num += 0.1
            if abs(ball.bottom - player.top) < 10 and self.ball_speed.y >0:
                ball.bottom = player.top
                self.ball_speed.x *= -1
                self.ball_num += 0.1
        #bot collusions
        if ball.colliderect(bot):
            if abs(ball.right - bot.left) < 10 and self.ball_speed.x >0:
                ball.right = bot.left
                self.ball_speed.x *= -1
                self.ball_num += 0.1
            if abs(ball.left - bot.right) < 10 and self.ball_speed.x <0:
                ball.left = ball.right
                self.ball_speed.x *= -1
                self.ball_num += 0.1
            if abs(ball.top - bot.bottom) < 10 and self.ball_speed.y <0:
                ball.top = bot.bottom
                self.ball_speed.x *= -1
                self.ball_num += 0.1
            if abs(ball.bottom - bot.top) < 10 and self.ball_speed.y >0:
                ball.bottom = bot.top
                self.ball_speed.x *= -1
                self.ball_num += 0.1
        if ball.y < 1 or ball.y > 499:
            self.ball_speed.y *= -1
            self.ball_num += 0.1
        if ball.x < 1:
            self.bot_points += 1
            self.reset()
        elif ball.x > 480:
            self.player_points += 1
            self.reset()
    def bot(self, ball, bot, dt):
        a = range(bot.y -5, bot.y + bot.h + 5, 1)
        if not ball.y in a:
            if ball.y > bot.y + bot.h/2:
                bot.y += self.bot_speed * dt * 40
            else:
                bot.y -= self.bot_speed * dt * 40
        else:
            bot.y = ball.y - bot.h/2
        if bot.y < 0:
            bot.y = 0
        elif bot.y + bot.h > 500:
            bot.y = 500 - bot.h
    def player(self, player, dir, dt):
        try:
            dir = int(dir)
        except:
            dir = 250
        a = range(player.y - 5, player.y + player.h + 5, 1)
        if  not dir in a:
            if dir > player.y + player.h/2:
                player.y += self.player_speed * dt * 40
            elif dir < player.y + player.h/2:
                player.y -= self.player_speed * dt * 40
            else:
                player.y = dir - player.h/2
        if player.y < 0:
            player.y = 0
        elif player.y + player.h > 500:
            player.y = 500 - player.h
    def draw(self, y):
        screens = pg.Surface((screen.get_size()), pg.SRCALPHA)
        pg.draw.rect(screens, (0,0,255, 50), (self.player_rect), 8, 5)
        pg.draw.rect(screen, 'blue', self.player_rect, 3,5)
        pg.draw.rect(screens, (255, 0, 0, 50), self.bot_rect, 8,5)
        pg.draw.rect(screen, 'red', self.bot_rect, 3,5)
        if y != None:
            pg.draw.circle(screen, color, (60, y), 10, 3)
        pg.draw.circle(screen, 'green', (self.ball_rect.x, self.ball_rect.y), 10, 3)
        pg.draw.circle(screens, (0, 255, 0, 50), (self.ball_rect.x, self.ball_rect.y), 10, 8)
        screen.blit(screens, (0,0))
class Mouse():
    def __init__(self):
        self.water = Water(amplitude=20)
        self.points = []
        self.dots = []
        self.mouse = None
        self.water_work = False
        self.line_work = False
        self.clicked = False
    def update(self, event):
        self.mouse = pg.mouse.get_pressed(), pg.mouse.get_pos()
        for i in event:
            if i.type == pg.KEYUP:
                if i.key == pg.K_l:
                    self.line_work = not self.line_work
                    self.water = Water(amplitude=20)
                    if not self.line_work:
                        self.points.clear()
                if i.key == pg.K_w:
                    self.water_work = not self.water_work
        if self.line_work:
            Label('Line is Working', (WIDTH-100, 20), outline=None, shade=[None,None], size=25, bg=None, color= color)
            self.lines()
        self.draw()
        if self.mouse[0][0] == 0:
            self.clicked = False
    def draw(self):
        keys = pg.key.get_pressed()
        screens = pg.Surface((screen.get_size()), pg.SRCALPHA)
        for i in self.dots:
            i.draw(screens)
            if keys[pg.K_SPACE]:
                i.move(self.mouse[1])
            if keys[pg.K_BACKSPACE]:
                self.dots.clear()
        if self.water_work:
            self.water.update()
        screen.blit(screens, (0,0))
    def lines(self):
        if self.mouse[0][0] == 1 and not self.clicked :
            self.clicked = True
            self.points.append(self.mouse[1])
        for i in self.points:
            pg.draw.circle(screen, 'red', i, 5)
        if len(self.points) == 2:
            pg.draw.line(screen, color,(self.points[0]), self.points[1])
            angle =m.atan2(self.points[1][0] - self.points[0][1], self.points[1][0] -self.points[0][0]) 
            x_vel = m.cos(angle) * 1.1
            y_vel = m.sin(angle) * 1.1
            power = m.hypot(self.points[0][0] - self.points[1][0], self.points[0][1] - self.points[1][1])
            for i in range(int(power)):
                i + 1
                x = self.points[0][0] + (x_vel * i)
                y = self.points[0][1]+ (y_vel * i)
                self.dots.append(Dot((x,y), (r.randint(0,255),r.randint(0,255),r.randint(0,255)), 2))
            self.points.clear()
class Cheats():
    def __init__(self):
        self.list = []
        self.click = Switch('Clicker', (WIDTH+100, 50),False, shade=[None,None],size=20)
        self.text = Switch('Text',(WIDTH+100, 125),False, shade=[None,None],size=20 )
        self.aimbot = Switch('AimBot',(WIDTH+100, 250),False, shade=[None,None],size=20 )
        self.dir = Input(["","",], (WIDTH+100, 300),22, shade=[None,None],size=20)
        self.input = Input(['',''], (WIDTH+100, 175),22, shade=[None,None],size=20)
        self.start = Input(['start','q'], (WIDTH+100, 425),22, shade=[None,None],size=20)
        self.key = ''
    def reset(self):
        self.text.turn = False
        self.click.turn = False
        self.aimbot.turn = False
        self.input.output = ''
    def on_press(self, key):
        try:
            k = key.char
        except:
            k = key.name
        if  k == self.key and self.click.choice():
            self.mouse()
        if k ==  self.key and self.text.choice():
            self.keyboard()
        if k == self.key and self.aimbot.choice():
            self.on_aimbot()
    def mouse(self):
        mouse = M()
        for i in range(20):
            one = time.time_ns()
            mouse.click(B.left)
            p.PAUSE = 0.0001
            two = time.time_ns()
    def keyboard(self):
        if self.input.choice() != None:
            keyboard = K()
            one = time.time_ns()
            keyboard.type(self.input.choice())
            p.PAUSE = 0.0001
            two = time.time_ns()
    def on_aimbot(self):
        mouse = M()
        dir = '/Users/kostia/Desktop/'+ str(self.dir.choice())
        try:
            x,y =p.locateCenterOnScreen(dir, confidence=0.6,  grayscale=True)
            one = time.time_ns()
            p.moveTo(x//2,y//2, 0.001)
            mouse.click(B.left)
            p.PAUSE = 0.01
            two = time.time_ns()
        except:
            pass

    def update(self, event):
        self.key = self.start.choice()
        self.text.draw()
        self.click.draw()
        self.aimbot.draw()
        if self.click.choice():
            self.text.turn = False
            self.aimbot.turn = False
        if self.text.choice():
            self.input.draw(event)
            self.click.turn = False
            self.aimbot.turn = False
        if self.aimbot.choice():
            self.dir.draw(event)
            self.click.turn = False
            self.text.turn = False
        self.start.draw(event)
class Water:
    x = [-10,WIDTH+20]
    y = [HEIGHT+10]
    points = []
    water_heights = []
    dy = []
    spacing = 10 #pixels
    sea_level = 200
    friction = 0.01
    surface_tension = 0.5
    oscillator = 0
    for i in range(0,x[1]+spacing,spacing):
        water_heights.append(y[0]-sea_level )
        dy.append(0)
    for i in range(len(water_heights)):
        points.append(((spacing*i) + x[0],water_heights[i]))
    points.append((x[0]+x[1],y[0]))
    points.append((x[0],y[0]))

    def __init__(self,amplitude=10,period=30,):
        self.amplitude = amplitude
        self.period = period
        self.list = []
    def shiftWaterHeight(self, mouse_pos, water_heights):
        x,y = mouse_pos
        index = 0
        for i in range(len(water_heights)):
            if Water.spacing*i <= x and x <= Water.spacing*(i+1):
                index = i
                break
        water_heights[index] = y
    def drops(self):
        if len(self.list) <= 5: 
            self.list.append(pg.Rect( r.randint(0,WIDTH),r.randint(-100, -10), 10, r.randint(3,7)))
        for i in self.list:
            pg.draw.circle(screen, color, i.center, i.h)
            i.y += 3
            for j in self.points:
                if i.collidepoint(j):
                    self.shiftWaterHeight((i.centerx, i.centery+i.h), Water.water_heights)
                    i.x, i.y = r.randint(0,WIDTH),r.randint(-100, -10)
    def update(self):
        self.drops()
        mouse = pg.mouse.get_pressed(), pg.mouse.get_pos()
        screens  = pg.Surface((screen.get_size()), pg.SRCALPHA)
        if mouse[0][0] ==1:
            self.shiftWaterHeight(mouse[1], Water.water_heights)



        for i in range(len(Water.dy)):
            #Neighboring heights pull on the dy values
            neighbor_heights = 0
            neighbor_count = 0
            if i>0:
                neighbor_heights += Water.water_heights[i-1]
                neighbor_count += 1
            if i<len(Water.dy)-1:
                neighbor_heights += Water.water_heights[i+1]
                neighbor_count += 1
            Water.dy[i] += Water.surface_tension*(neighbor_heights - neighbor_count*Water.water_heights[i])
            #friction
            Water.dy[i] = (1-Water.friction)*Water.dy[i]
        for i in range(len(Water.water_heights)):
            Water.water_heights[i] += Water.dy[i]
        Water.water_heights[-1] = Water.y[0]-Water.sea_level-self.amplitude*m.sin(Water.oscillator/self.period)
        Water.oscillator += 1
        for i in range(len(Water.water_heights)):
            Water.points[i] = ((Water.spacing*i) +Water.x[0],Water.water_heights[i])
        pg.draw.polygon(screens, (color[0],color[1], color[2], 150), Water.points)
        screen.blit(screens, (0,0))
class Main():
    def __init__(self):
        global color, num
        self.hand = Hands()
        self.face = Faces()
        self.mouse = Mouse()
        self.ping_pong_work = False
        self.pos = None
        self.pressed = False
        self.ping_pong = Pong()
        self.face_work = True
        self.hand_work = True
        self.pos = [0,0]
        self.keybinds = False
        self.update()
    def ping_pong_game(self, img):
        if self.ping_pong_work:
            self.ping_pong.reset()
        self.hand.update(img, False)
        work = self.hand.fingers == [0, 1, 1, 0, 0]
        try:
            self.ping_pong.update(self.hand.lmList1[8][1]/(720/HEIGHT), work)
        except:                
            self.ping_pong.update(self.pos[1], work)
    def update(self):
        global WIDTH, HEIGHT, screen
        while 1:
            keys = pg.key.get_pressed()
            clock.tick(60)
            event = pg.event.get()
            for i in event:
                if i.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if i.type == pg.KEYUP:
                    if i.key == pg.K_TAB:
                        self.keybinds = not self.keybinds
                    if self.keybinds:
                        if i.key == pg.K_1:
                            self.ping_pong_work = not self.ping_pong_work
                        if i.key == pg.K_ESCAPE:
                            self.cheat_work = False
                            screen = pg.display.set_mode((WIDTH, HEIGHT))
                        if i.key == pg.K_UP:
                            WIDTH += 40
                            HEIGHT += 40
                            screen = pg.display.set_mode((WIDTH, HEIGHT))
                        elif i.key == pg.K_DOWN:
                            WIDTH -= 40
                            HEIGHT -= 40
                            screen = pg.display.set_mode((WIDTH, HEIGHT))
                        if i.key == pg.K_f:
                            self.face_work = not self.face_work
                        if i.key == pg.K_h:
                            self.hand_work = not self.hand_work
            _, img = cap.read()

            for i in range(0,2):
                if color[i] > 253 or color[i] < 1:
                    num[i] *= -1
                color[i] += num[i]
            screen.fill('white')
            pg.draw.rect(screen, 'black', (0,0, WIDTH,HEIGHT))
            Label(self.hand.fingers, (100, 20), outline=None, shade=[None,None], size=20, bg=None, color= color)
                

                

            if self.ping_pong_work and not self.cheat_work:
                self.ping_pong_game(img)
            else:
                if self.hand_work:
                    self.hand.update(img, True, event)
                if self.face_work:
                    self.face.update(img, True)
                self.mouse.update(event)
            try:
              self.pos = (abs(self.hand.lmList1[8][0]/(1280/WIDTH)-WIDTH), self.hand.lmList1[8][1]/(720/HEIGHT))
            except:
                pass
            # cv2.imshow('Avatar', img)
            pg.display.update()
main = Main()


