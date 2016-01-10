import tkinter as tk
from tkinter import ttk

import random

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.width, self.height = 600, 500
        self.parent.geometry("%dx%d" % (self.width, self.height))
        self.parent.minsize(self.width, self.height)

        # add menubar to application
        self.menubar = tk.Menu(self.parent)
        self.parent.config(menu=self.menubar)

        # file menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Symptoms File", command=lambda : self.btn_handler("open"), accelerator="Ctrl+O", underline=0)
        self.filemenu.add_command(label="Save Symptoms File", command=lambda : self.btn_handler("save"), accelerator="Ctrl+S", underline=0)
        self.filemenu.add_command(label="Export for Render...", command=lambda : self.btn_handler("export"), accelerator="Ctrl+E", underline=0)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.parent.quit, accelerator="Ctrl+Q", underline=1)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Help", command=lambda : self.btn_handler("help"), accelerator="F1", underline=0)
        self.helpmenu.add_command(label="About", command=lambda : self.btn_handler("about"), underline=0)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        # symptom buttons
        self.cb_names = ["one1", "two1", "three1", "four1", "five1", "six1", "seven1", "eight1",
                        "one2", "two2", "three2", "four2", "five2", "six2", "seven2", "eight2",
                        "one3", "two3", "three3", "four3", "five3", "six3", "seven3", "eight3",
                        "one4", "two4", "three4", "four4", "five4", "six4", "seven4", "eight4",
                        "one5", "two5", "three5", "four5", "five5", "six5", "seven5", "eight5"]
        self.cb_states = {self.cb_names[i]: False for i in range(len(self.cb_names))}

        # mainframe (note that this is a subframe within the MainApplication Frame)
        self.mainframe = ttk.Frame(parent, padding="10 10 10 10")

        # some instructions
        instructions = ttk.Label(self.mainframe, text="Select and configure the patient's symptoms:", padding="0 0 0 10")
        instructions.pack(fill=tk.X)
        
        # patient configuration
        self.configframe = ttk.Frame(self.mainframe, padding="0 0 0 0", relief=tk.FLAT)
        han_label = ttk.Label(self.configframe, text="Handedness:", padding="0 0 0 0")
        dom_label = ttk.Label(self.configframe, text="Dominant Hemisphere:", padding="50 0 0 0")
        han_choice = tk.StringVar()
        han_om = ttk.OptionMenu(self.configframe, han_choice, "Right", "Right", "Left", command=lambda selected : self.om_handler(selected, index=0, omtype=1))
        han_om.config(width=7)
        dom_choice = tk.StringVar()
        dom_om = ttk.OptionMenu(self.configframe, dom_choice, "Left", "Right", "Left", command=lambda selected : self.om_handler(selected, index=1, omtype=1))
        dom_om.config(width=7)
        han_label.grid(row=0, column=0)
        han_om.grid(row=0, column=1)
        self.optionmenu_patch(han_om, han_choice)
        dom_label.grid(row=0, column=2)
        dom_om.grid(row=0, column=3)
        self.optionmenu_patch(dom_om, dom_choice)

        # application footer (including status and footer text)
        self.footerframe = ttk.Frame(self.mainframe, relief=tk.FLAT, padding="0 5 0 0")
        self.statustextframe= ttk.Frame(self.footerframe)
        self.status_string = tk.StringVar()
        self.status("Semio v0.1")
        statustext = ttk.Label(self.statustextframe, textvariable=self.status_string)
        self.footertextframe = ttk.Frame(self.footerframe)
        footertext = ttk.Label(self.footertextframe, text="Copyright (c) Benjamin Shanahan 2016")
        statustext.pack()
        footertext.pack()
        self.statustextframe.pack(side="left")
        self.footertextframe.pack(side="right")

        # add subframe and canvas
        self.subframe = ttk.Frame(self.mainframe, padding="5 5 5 5", relief=tk.GROOVE)
        self.canvas = tk.Canvas(self.subframe, width=self.width)
        self.canvas.config(highlightthickness=0, background="white")

        # create scrollable window
        self.interior = ttk.Frame(self.canvas, **kwargs)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=self.interior.winfo_reqwidth())
        self.interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)

        # add column titles
        sos_label = ttk.Label(self.interior, text="Onset Side", padding="0 0 0 0")
        sym_label = ttk.Label(self.interior, text="Symptom", padding="0 0 0 0")
        sos_label.grid(row=0, column=0, sticky=tk.W)
        sym_label.grid(row=0, column=1, sticky=tk.W)

        # add widgets to canvas
        for i, b in enumerate(self.cb_names):
            # add optionmenu to select symptom onset side
            if random.randint(0,1000) % 2 == 0:
                user_choice = tk.StringVar()
                om = ttk.OptionMenu(self.interior, user_choice, "Right", "Right", "Left", command=lambda selected, index=i, omtype=2 : self.om_handler(selected, index, omtype))
                om.config(width=5)
                om.grid(row=i+1, column=0, sticky=tk.EW, padx=(0, 25))
                self.optionmenu_patch(om, user_choice)

            # add symptom checkbutton
            cb = ttk.Checkbutton(self.interior, 
                                text=b, 
                                width=20,
                                command=(lambda b=b : self.cb_handler(b)))
            cb.state(["!alternate"])  # remove initial black square inside ttk checkbutton
            cb.grid(row=i+1, column=1)
            

        # add vertical scrollbar to subframe and attach it to canvas
        self.vbar = ttk.Scrollbar(self.subframe, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        
        # pack the frames
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.configframe.pack(fill=tk.BOTH, expand=False)
        self.subframe.pack(fill=tk.BOTH, expand=True)
        self.footerframe.pack(fill=tk.X, expand=False)
        self.mainframe.pack(fill=tk.BOTH, expand=True)

        # add event bindings for user interactivity
        self.add_bindings()

    def optionmenu_patch(self, om, var):
        "Set checked item to item that is actually selected. This fixes a tkinter bug."
        menu = om["menu"]
        last = menu.index("end")
        for i in range(0, last+1):
            menu.entryconfig(i, variable=var)

    def om_handler(self, selected, index, omtype):
        if omtype == 1:  # config
            print(selected, index, omtype)
        elif omtype == 2:  # symptom onset side selection
            print(selected, index, omtype)

    def cb_handler(self, button):
        self.cb_states[button] = True if self.cb_states[button] is False else False

    def btn_handler(self, button):
        self.status(button)

    def add_bindings(self):
        # mouse wheel scroll
        def _on_mousewheel(event):
            self.canvas.yview_scroll(-1*int(event.delta/120), "units")
        self.bind_all('<MouseWheel>', _on_mousewheel)

    def status(self, text):
        self.status_string.set(text)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Semio v0.1")
    MainApplication(root)
    root.mainloop()