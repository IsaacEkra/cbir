from PIL import ImageTk
from PIL import Image
import glob as gb
import os

class Pix:
    def __init__(self, master):

        self.master = master
        self.imgs = []
        self.phts = []
        self.m_X = 0
        self.m_Y = 0
        self.x = 0
        self.y = 0
        self.colorCode = []

        for infile in gb.glob('dataset/*.jpg'):
            file, ext = os.path.splitext(infile)
            image = Image.open(infile)
            pt = ImageTk.PhotoImage(image)

            imgSize = image.size
            x = imgSize[0]
            y = imgSize[1]
            if x > self.x:
              self.x = x
            if y > self.y:
              self.y = y
            x = imgSize[0]/3
            y = imgSize[1]/3
            imResize = image.resize((int(x), int(y)), Image.ANTIALIAS)
            ph = ImageTk.PhotoImage(imResize)

            if x > self.m_X:
              self.m_X = x
            if y > self.m_Y:
              self.m_Y = y

            self.imgs.append(image)
            self.phts.append(ph)

        if os.path.isfile('colorMatrix.txt'):
            colorMatrix = open('colorMatrix.txt','r')
            for textLine in colorMatrix:
                textLine = textLine.replace("[","").replace("]","").replace(" ","").split(",")
                textLine = [int(x) for x in textLine]
                self.colorCode.append(textLine)

        else:
            for image in self.imgs[:]:
                pList = list(image.getdata())
                colorcode_Binaries = self.encode_Image(pList)
                self.colorCode.append(colorcode_Binaries)
                colorMatrix = open('colorMatrix.txt','w')
                for i in range(len(self.colorCode)):
                    colorMatrix.write(str(self.colorCode[i]))
                    colorMatrix.write("\n")
                colorMatrix.close()

    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def get_Imgs(self):
        return self.imgs
    def get_phts(self):
        return self.phts
    def get_largePL(self):
        return self.largePL
    def get_m_X(self):
        return self.m_X
    def get_m_Y(self):
        return self.m_Y
    def get_colorCode(self):
        return self.colorCode

    def encode_Image(self, pl):
        colorcode_Binaries = [0]*64

        for values in pl:
            i = 0.299*values[0] + 0.587*values[1] + 0.114*values[2]
            t_Binaries = int(i/10)
            if t_Binaries > 24:
                t_Binaries = 24

            red,green,blue = values[0],values[1],values[2]
            c_Values = int(str(self.bit_Numbering(red))+str(self.bit_Numbering(green))+str(self.bit_Numbering(blue)),2)
            colorcode_Binaries[c_Values] += 1

        return colorcode_Binaries

    def bit_Numbering(self, x):
        binary = bin(x)
        binary = binary[2:]
        while (len(binary) < 8):
            binary = '0' + binary
        bit_Numbering = binary[:2]
        return bit_Numbering
