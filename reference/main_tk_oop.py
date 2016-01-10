import tkinter as tk
from tkinter import ttk

import random


class Application(tk.Tk):
    "Main Tkinter application class."

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.parent = ttk.Frame(self)

        self.WIDTH, self.HEIGHT = 600, 500
        self.TITLE = "Semio v0.1"
        self.COPYRIGHT = "Copyright (c) Benjamin Shanahan 2016"

        self.minsize(self.WIDTH, self.HEIGHT)
        self.title(self.TITLE)

        # checkbutton names and states
        self.checkbutton_names = [
            "one1", "two1", "three1", "four1", "five1", "six1", "seven1", "eight1",
            "one2", "two2", "three2", "four2", "five2", "six2", "seven2", "eight2",
            "one3", "two3", "three3", "four3", "five3", "six3", "seven3", "eight3",
            "one4", "two4", "three4", "four4", "five4", "six4", "seven4", "eight4",
            "one5", "two5", "three5", "four5", "five5", "six5", "seven5", "eight"
        ]
        self.checkbutton_states = {self.checkbutton_names[i]: False for i in range(len(self.checkbutton_names))}

        self.frames = {
            MainFrame: MainFrame(self.parent, self)
        }
        self.frames[MainFrame].pack()
        self.parent.pack(fill=tk.BOTH, expand=True)  # pack this last so frame order is correct

    def optionmenu_patch(self, optionmenu, variable):
        "Set checked item to item that is actually selected. This fixes a tkinter bug."
        menu = optionmenu["menu"]
        last = menu.index("end")
        for i in range(0, last+1):
            menu.entryconfig(i, variable=variable)

    def optionmenu_handler(self, selected, index, omtype):
            if omtype == 1:  # patient information configuration
                # print(selected, index, omtype)
                pass
            elif omtype == 2:  # symptom onset side selection
                # print(selected, index, omtype)
                pass

    def checkbutton_handler(self, button):
        self.checkbutton_states[button] = True if self.checkbutton_states[button] is False else False

    def button_handler(self, button):
        status = self.frames[MainFrame].frames[FooterFrame].status
        if button == "open":
            status("Opening file...")
        elif button == "save":
            status("Saving file...")
        elif button == "export":
            status("Exporting for render...")
        elif button == "exit":
            status("Exitting...")
            self.quit()
        elif button == "help":
            status("Loading application help...")
        elif button == "about":
            status("About Semio...")


class MainFrame(tk.Frame):
    "Main container frame for all other frames present in application."

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.button_handler = self.controller.button_handler

        # add menubar
        self.menubar = tk.Menu(self.controller)
        self.controller.config(menu=self.menubar)
        # file menu
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Symptoms File", command=lambda : self.button_handler("open"), accelerator="Ctrl+O", underline=0)
        self.filemenu.add_command(label="Save Symptoms File", command=lambda : self.button_handler("save"), accelerator="Ctrl+S", underline=0)
        self.filemenu.add_command(label="Export for Render...", command=lambda : self.button_handler("export"), accelerator="Ctrl+E", underline=0)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=lambda : self.button_handler("exit"), accelerator="Esc", underline=1)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        # help menu
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Help", command=lambda : self.button_handler("help"), accelerator="F1", underline=0)
        self.helpmenu.add_command(label="About", command=lambda : self.button_handler("about"), underline=0)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        # some instructions
        instructions = ttk.Label(self.controller, text="Select and configure the patient's symptoms:", padding="0 0 0 10")
        instructions.pack(fill=tk.X)

        # add additional frames
        self.frames = {
            ConfigFrame: ConfigFrame(self.parent, self),
            SymptomFrame: SymptomFrame(self.parent, self),
            FooterFrame: FooterFrame(self.parent, self)
        }
        self.frames[ConfigFrame].pack(fill=tk.BOTH, expand=False)
        self.frames[SymptomFrame].pack(fill=tk.BOTH, expand=True)
        self.frames[FooterFrame].pack(fill=tk.X, expand=False)


class ConfigFrame(tk.Frame):
    "User configuration of patient information."

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.optionmenu_handler = self.controller.controller.optionmenu_handler
        self.optionmenu_patch = self.controller.controller.optionmenu_patch

        self.han_label = ttk.Label(self, text="Handedness:", padding="0 0 0 0")
        self.dom_label = ttk.Label(self, text="Dominant Hemisphere:", padding="50 0 0 0")
        
        self.han_choice = tk.StringVar()
        self.han_om = ttk.OptionMenu(self, self.han_choice, "Right", "Right", "Left", command=lambda selected : self.optionmenu_handler(selected, index=0, omtype=1))
        self.han_om.config(width=7)
        
        self.dom_choice = tk.StringVar()
        self.dom_om = ttk.OptionMenu(self, self.dom_choice, "Left", "Right", "Left", command=lambda selected : self.optionmenu_handler(selected, index=1, omtype=1))
        self.dom_om.config(width=7)
        
        self.han_label.grid(row=0, column=0)
        self.han_om.grid(row=0, column=1)
        self.optionmenu_patch(self.han_om, self.han_choice)
        self.dom_label.grid(row=0, column=2)
        self.dom_om.grid(row=0, column=3)
        self.optionmenu_patch(self.dom_om, self.dom_choice)


class SymptomFrame(tk.Frame):
    "Symptom selection frame. Contains scrollable widget canvas."

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.optionmenu_handler = self.controller.controller.optionmenu_handler
        self.optionmenu_patch = self.controller.controller.optionmenu_patch
        self.checkbutton_handler = self.controller.controller.checkbutton_handler

        self.checkbutton_names = self.controller.controller.checkbutton_names
        self.checkbutton_states = self.controller.controller.checkbutton_states

        self.subframe = ttk.Frame(self, padding="5 5 5 5", relief=tk.GROOVE)
        self.canvas = tk.Canvas(self.subframe)
        self.canvas.config(highlightthickness=0)
        
        # create scrollable window
        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=tk.NW)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # track changes to the canvas and frame width and sync them, while updating scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=self.interior.winfo_reqwidth())
        def _configure_canvas(event):
            if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
        self.interior.bind('<Configure>', _configure_interior)
        self.canvas.bind('<Configure>', _configure_canvas)

        # add column titles
        sos_label = ttk.Label(self.interior, text="Onset Side", padding="0 0 0 0")
        sym_label = ttk.Label(self.interior, text="Symptom", padding="0 0 0 0")
        sos_label.grid(row=0, column=0, sticky=tk.W)
        sym_label.grid(row=0, column=1, sticky=tk.W)

        # add widgets to canvas
        for i, b in enumerate(self.checkbutton_names):
            # add optionmenu to select symptom onset side
            if random.randint(0,1000) % 2 == 0:
                user_choice = tk.StringVar()
                om = ttk.OptionMenu(self.interior, user_choice, "Right", "Right", "Left", command=lambda selected, index=i, omtype=2 : self.optionmenu_handler(selected, index, omtype))
                om.config(width=5)
                om.grid(row=i+1, column=0, sticky=tk.EW, padx=(0, 25))
                self.optionmenu_patch(om, user_choice)

            # add symptom checkbutton
            cb = ttk.Checkbutton(self.interior, 
                                text=b, 
                                width=20,
                                command=(lambda b=b : self.checkbutton_handler(b)))
            cb.state(["!alternate"])  # remove initial black square inside ttk checkbutton
            cb.grid(row=i+1, column=1)

        # add vertical scrollbar to subframe and attach it to canvas
        self.vbar = ttk.Scrollbar(self.subframe, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        
        # pack the frames
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.subframe.pack(fill=tk.BOTH, expand=True)

        self.add_bindings()

    def add_bindings(self):
        "Attach mouse wheel scroll to canvas y scroll position."
        def _on_mousewheel(event):
            self.canvas.yview_scroll(-1*int(event.delta/120), "units")
        self.bind_all('<MouseWheel>', _on_mousewheel)


class FooterFrame(tk.Frame):
    "Application footer."

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller

        self.TITLE = self.controller.controller.TITLE
        self.COPYRIGHT = self.controller.controller.COPYRIGHT

        self.statustextframe= ttk.Frame(self)
        self.status_string = tk.StringVar()
        self.status(self.TITLE)
        self.statustext = ttk.Label(self.statustextframe, textvariable=self.status_string)

        self.footertextframe = ttk.Frame(self)
        self.footertext = ttk.Label(self.footertextframe, text=self.COPYRIGHT)
        
        self.statustext.pack()
        self.footertext.pack()
        self.statustextframe.pack(side=tk.LEFT)
        self.footertextframe.pack(side=tk.RIGHT)

    def status(self, text):
        self.status_string.set(str(text))


if __name__ == "__main__":
    app = Application()
    app.mainloop()