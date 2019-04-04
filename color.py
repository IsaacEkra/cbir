import sys
import os
import math
import glob as gb
import numpy as np
from tkinter import *
from PIL import ImageTk
from PIL import Image


class Color(Frame):
    def __init__(self, root, pix):
        self.pix = pix
        self.imgs = pix.get_Imgs()
        self.phts = pix.get_phts()
        self.colorsBinaries = pix.get_colorCode()
        self.allBinaries = []
        self.m_X = pix.get_m_X() + 15
        self.m_Y = pix.get_m_Y() + 5
        self.bg_color = '#353535'
        self.bt = '#565656'
        self.abt_color = '#2d2c2c'
        self.fg_color = '#f7efef'
        self.bt_h = 10
        self.curPage = 0
        self.currPhts = pix.get_phts()
        self.currImgs = pix.get_Imgs()
        self.maxNumPages = int(self.get_maxNumPages())
        self.currIteration = 0
        self.imgWeights = []
        self.mainWindow = Frame(root, bg = self.bg_color)
        self.mainWindow.pack()
        self.topWindow = Frame(self.mainWindow, bg = self.bg_color)
        self.topWindow.pack(side = RIGHT)
        self.botWindow = Frame(self.mainWindow, bg = self.bg_color)
        self.botWindow.pack(side = LEFT)
        self.currView = Label(self.topWindow, width=450, height=pix.get_y(), bg = self.bg_color)
        self.currView.pack(side = TOP)
        self.update_View(self.imgs[0].filename)

        self.menuText = Frame(self.topWindow, bg = self.bg_color)
        self.menuText.pack()
        self.button_ColorCode = Button(self.menuText, text = "Search by color code", width = 40, pady = self.bt_h, border = 0, bg = self.bt, fg = self.fg_color, activebackground = self.abt_color, command=lambda:self.find_dist("ColorCode"))
        self.button_ColorCode.pack()
        self.emptyLine1 = Label(self.menuText, bg = self.bg_color, text = ' ')
        self.emptyLine1.pack()

        self.b_reset = Button(self.menuText,text="Reset", width=40,pady=self.bt_h,border=0,bg=self.bt,fg=self.fg_color,activebackground=self.abt_color,command=lambda:self.reset())
        self.b_reset.pack()

        self.resultWindow = Frame(self.botWindow, bg = self.bg_color)
        self.resultWindow.pack()
        steps = Label(self.resultWindow, bg = self.bg_color, fg = '#aaaaaa', text = "Select an image by clicking on it.")
        steps.pack()
        self.canvasArea = Canvas(self.resultWindow, bg = self.bg_color, highlightthickness = 0)

        self.pageNav = Frame(self.botWindow, bg = self.bg_color)
        self.pageNav.pack()
        self.button_PreviousNav = Button(self.pageNav, text = "<<", width = 30, border = 0, bg = self.bt, fg = self.fg_color, activebackground = self.abt_color, command=lambda:self.prev_Page())
        self.button_PreviousNav.pack(side = LEFT)

        self.pageNumLabel = Label(self.pageNav,text="Page 1 / " + str(self.maxNumPages),width = 43,bg = self.bg_color, fg='#ff0000')
        self.pageNumLabel.pack(side = LEFT)
        self.button_NextNav = Button(self.pageNav, text = ">>", width = 30, border = 0, bg = self.bt, fg = self.fg_color, activebackground = self.abt_color, command=lambda:self.next_Page())
        self.button_NextNav.pack(side = RIGHT)

        self.reset()

    def reset(self):
        self.currIteration = 0
        self.imgWeights = []
        self.update_View(self.imgs[0].filename)
        self.currImgs = self.imgs
        self.currPhts = self.phts
        i_l = self.currImgs[:20]
        p_l = self.currPhts[:20]
        self.update_Output((i_l, p_l))

    def get_position(self, filename):
        position = -1
        for i in range(len(self.imgs)):
            file = self.imgs[i].filename.replace("\\","/")
            if filename == file:
                position = i
        return position

    def avg_vals(self,matrix):
        new_Matrix = []
        for i in range(len(matrix)):
            x,y = self.imgs[i].size
            size = x * y
            feats = [f / float(size) for f in matrix[i]]
            new_Matrix.append(feats)
        return new_Matrix

    def norm_weights(self):
        fdback = []
        f = []
        s = []
        w_lbd = []
        i = 0
        min_s = 0

        fdback.append(self.allBinaries[self.get_position(self.selected.filename)])
        if len(fdback) > 1:
            for i in range(len(fdback)):
                for j in range(len(fdback[i])):
                    if len(f) <= j:
                        f.append([fdback[i][j]])
                    else:
                        f[j].append(fdback[i][j])
            u_lbd = [reduce(lambda x,y: x + y, l) / len(l) for l in f]

            for i in range(len(f)):
                s.append(np.std(f[i]))
            min_s = min(filter(lambda a: a != 0,s))

            w_lbd = [0.0] * len(f)
            for i in range(len(f)):
                if s[i] == 0 and u_lbd[i] == 0:
                    w_lbd[i] = 0
                elif s[i] == 0 and u_lbd[i] != 0:
                    w_lbd[i] = 1 / float(min_s * 0.5)
                else:
                    w_lbd[i] = 1 / float(s[i])

            sum_ofW = reduce(lambda a,b: a + b,w)

            for i in range(len(self.imgWeights)):
                self.imgWeights[i] = w_lbd[i] / sum_ofW

            for a,b,c in zip(fdback[0],s,self.imgWeights):
                print(str(a) + "\t" + str(b)+ "\t"+ str(c))

    def find_dist(self,method):
        position = self.get_position(self.selected.filename)
        all_Values = []
        result = []

        if method == 'ColorCode':
            all_Values = self.avg_vals(self.colorsBinaries)

        i_values = all_Values[position]

        for i in range(len(all_Values)):
            if i != position:
                d = 0.0
                k_values = all_Values[i]
                for j in range(len(i_values)):
                    di = abs(float(i_values[j]) - float(k_values[j]))
                    d += di
                self.insert_tuple(result,(d,i))

        self.currImgs,self.currPhts = [],[]
        for img in result:
            self.currImgs.append(self.imgs[img[1]])
            self.currPhts.append(self.phts[img[1]])

        i_L = self.currImgs[:20]
        p_L = self.currPhts[:20]
        self.curPage = 0
        self.update_Output((i_L,p_L))

    def insert_tuple(self,array,tuple):
        if len(array) == 0:
            array.insert(0,tuple)
        else:
            for i in range(len(array)):
                if tuple[0] < array[i][0]:
                    array.insert(i,tuple)
                    return
            array.insert(len(array),tuple)



    def update_Output(self,st):
        self.pageNumLabel.configure(text="Page " + str(self.curPage+1) \
                                 + " / " + str(self.maxNumPages))
        columns = 5
        self.canvasArea.delete(ALL)
        self.canvasArea.config(width = (self.m_X) * 5, height = self.m_Y * 4)
        self.canvasArea.pack()

        imgLeft = []
        for i in range(len(st[0])):
            f = st[0][i].filename
            img = st[1][i]
            imgLeft.append((f,img))

        rowPosition = 0
        while imgLeft:
            imgRow = imgLeft[:columns]
            imgLeft = imgLeft[columns:]
            colPosition = 0
            for (filename, img) in imgRow:
                frame = Frame(self.canvasArea, bg = self.bg_color,border = 0)
                frame.pack()
                imgLink = Button(frame, image = img, border = 0,bg=self.bg_color,width=self.pix.get_m_X(),activebackground=self.bg_color)
                imgHander = lambda f = filename: self.update_View(f)
                imgLink.config(command = imgHander)
                imgLink.pack(side = LEFT)
                self.canvasArea.create_window(
                    colPosition,
                    rowPosition,
                    anchor=NW,
                    window=frame,
                    width=self.m_X,
                    height=self.m_Y)
                colPosition += self.m_X
            rowPosition += self.m_Y

    def update_View(self,file):
        self.selected = Image.open(file.replace("\\","/"))
        self.selectedImg=ImageTk.PhotoImage(self.selected)
        self.currView.configure(image = self.selectedImg)

    def prev_Page(self):
        self.curPage -= 1
        if self.curPage < 0:
            self.curPage = self.maxNumPages-1
        start = self.curPage * 20
        end = start + 20
        i_L = self.currImgs[start:end]
        p_L = self.currPhts[start:end]
        self.update_Output((i_L,p_L))

    def next_Page(self):
        self.curPage += 1
        if self.curPage >= self.maxNumPages:
            self.curPage = 0
        start = self.curPage * 20
        end = start + 20
        i_L = self.currImgs[start:end]
        p_L = self.currPhts[start:end]
        self.update_Output((i_L,p_L))

    def get_maxNumPages(self):
        pageCount = len(self.phts) / 20
        if len(self.phts) % 20 > 0:
            pageCount += 1
        return pageCount
