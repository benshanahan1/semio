'''
Example of  canvas with that can be scrolled with mouse and 
dragged around with middle mouse of the button.
Written and tested using Python 3.4 on Ubuntu x64 14.04
'''

from tkinter import *


class MyCanvas(Canvas):
    
    def __init__(self, parent=None, img=None, *parms, **kparms):
        Canvas.__init__(self, parent, *parms, **kparms)
        
        self._width =  1000;
        self._height = 1000;
         
        self._starting_drag_position = ()

        self.config(width = self._width, height=self._height, bg='green')
        
        self._draw_some_example_objects()
                
        self._add_scrollbars()        
        self._addMouseBindings()
        
        self.pack(fill=BOTH, expand=YES)
        
    def _add_scrollbars(self):
        
        self.sbarV = Scrollbar(self.master, orient=VERTICAL)
        self.sbarH = Scrollbar(self.master, orient=HORIZONTAL)
        
        self.sbarV.config(command=self.yview)
        self.sbarH.config(command=self.xview)
        
        self.config(yscrollcommand=self.sbarV.set)  
        self.config(xscrollcommand=self.sbarH.set)
        
        self.sbarV.pack(side=RIGHT, fill=Y)  
        self.sbarH.pack(side=BOTTOM, fill=X)


    def _addMouseBindings(self):
    
        # mouse wheel scroll
        self.bind('<4>', lambda event : self.yview('scroll', -1, 'units'))
        self.bind('<5>', lambda event : self.yview('scroll', 1, 'units'))        
        
        # dragging canvas with mouse middle button 
        self.bind("<Button-2>", self.__start_scroll)
        self.bind("<B2-Motion>", self.__update_scroll)
        self.bind("<ButtonRelease-2>", self.__stop_scroll)

      
    def __start_scroll(self, event):
        
        # set the scrolling increment. 
        # value of 0 is unlimited and very fast
        # set it to 1,2,3 or whatever to make it slower
        self.config(yscrollincrement=3) 
        self.config(xscrollincrement=3) 
                
        self._starting_drag_position = (event.x, event.y)
        
        self.config(cursor="fleur")
    
        
    def __update_scroll(self, event):
       
        deltaX = event.x - self._starting_drag_position[0]
        deltaY = event.y - self._starting_drag_position[1]
       
        
        self.xview('scroll', deltaX, 'units')
        self.yview('scroll', deltaY, 'units')
      
            
        self._starting_drag_position =  (event.x, event.y)
        
        
        
    def __stop_scroll(self, event):
        
        # set scrolling speed back to 0, so that mouse scrolling 
        # works as expected.
        self.config(xscrollincrement=0) 
        self.config(yscrollincrement=0)
        
        self.config(cursor="")

        
    def _draw_some_example_objects(self):
        
        colors = dict(outline="black")
        
        self.config(scrollregion=(0,0, self._width, self._height))  
        
        self.create_rectangle(30, 10, 120, 120, fill="red", **colors)        
        self.create_rectangle(330, 410, 420, 460, fill="blue", **colors)
        self.create_rectangle(830, 810, 920, 960, fill="yellow", **colors)
        self.create_rectangle(830, 210, 990, 500, fill="cyan", **colors)
        self.create_rectangle(130, 810, 290, 999, fill="gray", **colors)
                
      

class MyGUI(Tk):
    
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Drag canvas with mouse")
        self.geometry("500x500")
        
        self._addWidgets()
    
    def _addWidgets(self):
        my_canvas = MyCanvas(self)
            
        
    
        
if __name__ == '__main__':
    
    MyGUI().mainloop()                
        