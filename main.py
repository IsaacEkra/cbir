from color import Color
from pix import Pix
import sys
import os
from tkinter import *

if __name__ == '__main__':
    my_path = os.path.abspath(__file__)
    mydir = os.path.dirname(my_path)
    root = Tk()
    root.resizable(width=False, height=False)
    pix = Pix(root)
    top = Color(root,pix)
    root.mainloop()
