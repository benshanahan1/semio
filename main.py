""" 
The MIT License (MIT)
Copyright (c) 2016 Benjamin Shanahan

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os, json, webbrowser, subprocess
from tkinter import ttk
from lib import parser, region
from lib import globals as g


class Application(tk.Tk):
    "Main Tkinter application class."

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.parent = ttk.Frame(self)

        # GUI constants
        self.WIDTH, self.HEIGHT = 700, 600
        self.APP_ICO = "icon/favicon.ico"
        self.APP_TITLE = "Semio"
        self.TITLE = "Semio v1.0"
        self.COPYRIGHT = "Copyright (c) Benjamin Shanahan 2016"
        self.HELP_WEBPAGE = "http://www.bshanahan.info/semio"
        self.DESCRIPTION = "Semio is a objective semiology diagnostic tool, intended for usage as a conflict mediator among surgeons during discussions concerning seizure-onset-zone.\n\nSemio has a sizeable database of semiology information pulled from current and past literature. The database can be appended at any time to reflect new developments in the field.\n\nThe user selects all symptoms exhibited by a patient, choosing also the symptom's side of onset. These selected symptoms are then used to calculate the probability of seizure onset for different locations across the brain.\n\nOnce the user has selected the patient's symptoms and chosen to render the probabilities, a 3D representation of the brain can be rendered with the probabilities overlayed."

        # update GUI
        self.minsize(self.WIDTH, self.HEIGHT)
        self.title(self.APP_TITLE)
        self.iconbitmap(os.path.abspath(self.APP_ICO))

        # Semio constants
        self.EXPORT_EXTENSION = "*.3d"
        self.QUICK_EXPORT_FILENAME = "quick_export"
        self.EXPORT_FILETYPES = [("3D file", self.EXPORT_EXTENSION)]
        self.EXPORT_INITIALDIR = "export/"
        self.SAVE_EXTENSION = "*.semio"
        self.SAVE_FILETYPES = [("Symptom file", self.SAVE_EXTENSION)]
        self.SAVE_INITIALDIR = "saved/"
        self.JSON_FILEPATH = "data/data.json"
        self.MAX_APP_PATH = "max/Semiology.exe"  # location of 3D rendering program
        
        # check if export and save directories exist, and if not, create them
        if not os.path.exists(self.EXPORT_INITIALDIR):
            os.makedirs(self.EXPORT_INITIALDIR)
        if not os.path.exists(self.SAVE_INITIALDIR):
            os.makedirs(self.SAVE_INITIALDIR)

        # Semio variables
        self.handedness = g.Constants.RIGHT
        self.dominant_hemisphere = g.Constants.LEFT
        self.regionlist = region.RegionList()

        # load and parse JSON file containing symptom information
        self.p = parser.Parser()
        self.p.load(self.JSON_FILEPATH)
        self.p.parse()

        # symptom display in GUI
        self.symptom_info = self.p.get_symptom_display_info()
        self.symptom_checkbutton_states = {str(i): False for i in range(len(self.symptom_info))}
        self.symptom_onset_sides = {str(i): None for i in range(len(self.symptom_info))}

        self.frames = {
            MainFrame: MainFrame(self.parent, self)
        }
        self.frames[MainFrame].pack()
        self.parent.pack(fill=tk.BOTH, expand=True)  # pack this last so frame order is correct

        # add keyboard shortcut bindings
        self.add_bindings()

        # get access to things located within frame children
        self.symptomframe = self.frames[MainFrame].frames[SymptomFrame]
        self.configframe = self.frames[MainFrame].frames[ConfigFrame]
        self.footerframe = self.frames[MainFrame].frames[FooterFrame]
        self.status = self.footerframe.status

    def optionmenu_patch(self, optionmenu, variable):
        "Set checked item to item that is actually selected. This fixes a tkinter bug."
        menu = optionmenu["menu"]
        last = menu.index("end")
        for i in range(0, last+1):
            menu.entryconfig(i, variable=variable)

    def optionmenu_handler(self, selected, index, omtype):
            if omtype == 1:  # patient information configuration
                if index == 0:
                    self.handedness = selected.lower()
                elif index == 1:
                    self.dominant_hemisphere = selected.lower()
            elif omtype == 2:  # symptom onset side selection
                self.symptom_onset_sides[index] = selected

    def checkbutton_handler(self, key):
        self.symptom_checkbutton_states[key] = True if self.symptom_checkbutton_states[key] is False else False

    def button_handler(self, button):
        if button == "open":
            self.open()
        elif button == "save":
            self.save()
        elif button == "export":
            self.export(render=False)
        elif button == "export_render":
            self.export(render=True)
        elif button == "exit":
            self.exit()
        elif button == "help":
            self.help()
        elif button == "about":
            self.about()

    def prepare_export(self):
        "Add regions to region list, observing user defined variables."
        self.regionlist.reset()  # remove all regions before exporting to prevent duplicates
        for idx, checked in self.symptom_checkbutton_states.items():
            if checked:  # boolean indicating if checkbox is checked
                symptom = self.symptom_info[int(idx)]
                c, i = symptom[0]  # retrieve category and symptom indices from symptom var
                info = {
                    "symptom_onset_side": self.symptom_onset_sides[idx],
                    "handedness": self.handedness,
                    "dominant_hemisphere": self.dominant_hemisphere
                }
                if self.p.n_symptoms[c] == 1:  # handle case with only one symptom (nesting differences)
                    self.regionlist.add(self.p.symptoms[c], info)
                else:
                    self.regionlist.add(self.p.symptoms[c][i], info)

    def update_widgets(self, data):
        "Update widget states and the widgets themselves based on information in given data dict."
        handedness = data["handedness"] if "handedness" in data else None
        dominant_hemisphere = data["dominant_hemisphere"] if "dominant_hemisphere" in data else None
        symptom_onset_sides = data["symptom_onset_sides"] if "symptom_onset_sides" in data else None
        symptom_checkbutton_states = data["symptom_checkbutton_states"] if "symptom_checkbutton_states" in data else None
        if handedness is not None:
            self.handedness = handedness
            self.configframe.han_choice.set(self.handedness.title())
        if dominant_hemisphere is not None:
            self.dominant_hemisphere = dominant_hemisphere
            self.configframe.dom_choice.set(self.dominant_hemisphere.title())
        if symptom_onset_sides is not None:
            self.symptom_onset_sides = symptom_onset_sides
            for key, value in self.symptom_onset_sides.items():
                if value is not None:
                    self.symptomframe.optionmenus_vars[key].set(value)
        if symptom_checkbutton_states is not None:
            self.symptom_checkbutton_states = symptom_checkbutton_states
            for key, value in self.symptom_checkbutton_states.items():
                self.symptomframe.checkbuttons_vars[key].set(int(value))
        
    def add_bindings(self):
        "Bind keyboard shortcuts."
        self.bind("<Escape>", self.exit)         # quit application
        self.bind("<Control-o>", self.open)      # open symptoms file
        self.bind("<Control-s>", self.save)      # save symptoms file
        self.bind("<Control-e>", self.export)    # export symptoms to text file
        export_render = lambda event=None, render=True : self.export(event, render=render)
        self.bind("<Control-r>", export_render)  # export and render symptoms
        self.bind("<F1>", self.help)             # open application help

        "Bind scrollwheel to scroll symptoms window."
        def _on_mousewheel(event):
            self.symptomframe.canvas.yview_scroll(-1*int(event.delta/120), "units")
        self.bind("<MouseWheel>", _on_mousewheel)

    def exit(self, event=None):
        self.quit()

    def open(self, event=None):
        fd = filedialog.askopenfile(mode="r",
            defaultextension=self.SAVE_EXTENSION,
            filetypes=self.SAVE_FILETYPES,
            initialdir=self.SAVE_INITIALDIR,
            title="Open")
        if fd is None: return  # dialog is closed by user
        else:
            data = json.load(fd)
            self.update_widgets(data)
            fd.close()
            self.status("Opened %s." % fd.name)

    def save(self, event=None):
        data = {
            "handedness": self.handedness,
            "dominant_hemisphere": self.dominant_hemisphere,
            "symptom_checkbutton_states": self.symptomframe.symptom_checkbutton_states,
            "symptom_onset_sides": self.symptomframe.symptom_onset_sides
        }
        fd = filedialog.asksaveasfile(mode="w", 
            defaultextension=self.SAVE_EXTENSION, 
            filetypes=self.SAVE_FILETYPES,
            initialdir=self.SAVE_INITIALDIR,
            title="Save As")
        if fd is None: return  # dialog is closed by user
        else:
            json.dump(data, fd)
            fd.close()
            self.status("Saved to %s." % fd.name)

    def export(self, event=None, render=False):
        self.prepare_export()
        output = self.regionlist.export()
        if render:
            fd = None
            quick_path = self.EXPORT_INITIALDIR + self.QUICK_EXPORT_FILENAME + self.EXPORT_EXTENSION[1:]
            with open(quick_path, "w") as fd:
                fd.write(output)
            self.status("Exported as %s." % fd.name)
            try:
                subprocess.Popen('"%s" %s' % (self.MAX_APP_PATH, fd.name))  # render 3D
            except Exception:
                self.status("Fatal error: failed to launch Semiology.exe.")
        else:
            fd = filedialog.asksaveasfile(mode="w", 
                defaultextension=self.EXPORT_EXTENSION, 
                filetypes=self.EXPORT_FILETYPES,
                initialdir=self.EXPORT_INITIALDIR,
                title="Export")
            if fd is None: return  # dialog is closed by user
            else:
                fd.write(output)
                fd.close()
                self.status("Exported as %s." % fd.name)            

    def help(self, event=None):
        webbrowser.open(self.HELP_WEBPAGE)

    def about(self):
        messagebox.showinfo("About %s" % self.TITLE, message="%s\n\n%s" % (self.DESCRIPTION, self.COPYRIGHT))


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
        self.filemenu.add_command(label="Export...", command=lambda : self.button_handler("export"), accelerator="Ctrl+E", underline=0)
        self.filemenu.add_command(label="Export and Render...", command=lambda : self.button_handler("export_render"), accelerator="Ctrl+R", underline=11)
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

        self.symptom_info = self.controller.controller.symptom_info
        self.symptom_checkbutton_states = self.controller.controller.symptom_checkbutton_states
        self.symptom_onset_sides = self.controller.controller.symptom_onset_sides

        self.subframe = ttk.Frame(self, padding="5 5 5 5", relief=tk.GROOVE)
        self.canvas = tk.Canvas(self.subframe)
        self.canvas.config(highlightthickness=0)

        # add all added widgets to dictionaries so we can set their values later
        self.optionmenus = {}
        self.optionmenus_vars = {}
        self.checkbuttons = {}
        self.checkbuttons_vars = {}
        
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
        sos_label = ttk.Label(self.interior, text="Onset Side", padding="0 0 0 0").grid(row=0, column=0, sticky=tk.W)
        cat_label = ttk.Label(self.interior, text="Category", padding="0 0 0 0").grid(row=0, column=1, sticky=tk.W)
        sym_label = ttk.Label(self.interior, text="Symptom", padding="0 0 0 0").grid(row=0, column=2, sticky=tk.W)
        des_label = ttk.Label(self.interior, text="Description", padding="5 0 0 0").grid(row=0, column=3, sticky=tk.W)

        # add widgets to canvas
        old_category, color = None, None
        color_counter = 0
        colors = ["black", "dark violet"]  # options: http://wiki.tcl.tk/37701
        for i, b in enumerate(self.symptom_info):
            # NOTE: the commented lines below were changed from ttk to tk to allow changing colors.

            indices, category, symptom, lateralization, description = b  # unpack the tuple
            category = category.title()

            if old_category != category:
                # increment color choice
                color = colors[color_counter]
                color_counter += 1
                if color_counter >= len(colors): color_counter = 0  # overflow back to 0

            old_category = category
            lateralization = lateralization.lower()
            if description.lower() == g.Constants.NONE or description.lower() == g.Constants.UNDEFINED:
                description = None

            # should we include a right/left selection option menu for symptom onset side?
            display_sos = (g.Constants.IPSILATERAL, g.Constants.CONTRALATERAL)
            if lateralization in display_sos:
                self.symptom_onset_sides[str(i)] = "Right"  # change index from default None to a value
                choice = tk.StringVar()
                om = ttk.OptionMenu(self.interior, choice, "Right", "Right", "Left", command=lambda selected, index=str(i), omtype=2 : self.optionmenu_handler(selected, index, omtype))
                om.config(width=5)
                om.grid(row=i+1, column=0, sticky=tk.EW, padx=(0, 25))
                self.optionmenu_patch(om, choice)
                self.optionmenus[str(i)] = om
                self.optionmenus_vars[str(i)] = choice
            else:
                self.optionmenus[str(i)] = None
                self.optionmenus_vars[str(i)] = None

            # add category label
            # categorylabel = ttk.Label(self.interior, text=category, padding="0 0 5 0").grid(row=i+1, column=1, sticky=tk.W)
            categorylabel = tk.Label(self.interior, text=category, fg=color).grid(row=i+1, column=1, sticky=tk.W)

            # add checkbutton
            var_selected = tk.IntVar()
            var_selected.set(0)  # default to all unselected
            # cb = ttk.Checkbutton(self.interior, text=symptom, variable=var_selected,
            cb = tk.Checkbutton(self.interior, text=symptom, variable=var_selected, fg=color,
                                command=(lambda var=str(i) : self.checkbutton_handler(var)))
            # cb.state(["!alternate"])  # remove initial black square inside ttk checkbutton
            cb.grid(row=i+1, column=2, sticky=tk.W)
            self.checkbuttons[str(i)] = cb
            self.checkbuttons_vars[str(i)] = var_selected

            # add description if applicable
            if description is not None:
                # descriptionlabel = ttk.Label(self.interior, text=description, padding="5 0 0 0").grid(row=i+1, column=3, sticky=tk.W)
                descriptionlabel = tk.Label(self.interior, text=description, fg=color).grid(row=i+1, column=3, sticky=tk.W)
        
        # add vertical scrollbar to subframe and attach it to canvas
        self.vbar = ttk.Scrollbar(self.subframe, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.vbar.set)
        
        # pack the frames
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.subframe.pack(fill=tk.BOTH, expand=True)


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