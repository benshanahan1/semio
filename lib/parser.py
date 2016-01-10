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

import json

class Parser:
    "Parser class for parsing JSON file containing data. Specific to Semio."

    def __init__(self):
        self.path = None
        self.data = None
        self.categories = None
        self.n_categories = 0
        self.symptoms = None
        self.n_symptoms = []
        self.parse_run = False

    def __str__(self):
        "Return a text tree version of the parsed input."
        string = ""
        for c in range(self.n_categories):
            string += "%s\n" % self.categories[c]
            if self.n_symptoms[c] == 1:
                string += "    %s\n" % self.symptoms[c]["_label"]
            else:
                for i in range(self.n_symptoms[c]):
                    string += "    %s\n" % self.symptoms[c][i]["_label"]
        return string

    def load(self, path):
        "Load JSON file from specified path."
        self.path = path
        with open(path) as f:
            self.data = json.load(f)

    def parse(self):
        "Parse the loaded JSON data into meaningful variables."
        # retrieve categories from JSON file
        flat = self.data["semiology"]["category"]  # flatten loaded data for easier access
        self.categories = [flat[c]["_label"] for c in range(len(flat))]
        self.n_categories = len(self.categories) 
        
        # Create a list with as many elements as there are categories. Within each index,
        # place the item list retrieved from the JSON file. This list contains a dictionary 
        # defining a new symptom at each index.
        self.symptoms = [flat[c]["item"] for c in range(len(flat))]
        for item in self.symptoms:
            length = 1
            if type(item) is list:  # if not, it is a dict and therefore one element long
                length = len(item)
            self.n_symptoms.append(length)
        if len(self.n_symptoms) != self.n_categories:
            raise Exception("Number of item groups and number of categories should match.")
        self.parse_run = True

    def get_symptom_display_info(self):
        "Return list of tuples, each containing information about a given symptom."
        symptom_list = []
        if not self.parse_run:
            raise Exception("Please run parse() before calling this method.")
        for c, category in enumerate(self.categories):
            if type(self.symptoms[c]) is list:
                for i, symptom in enumerate(self.symptoms[c]):
                    row = ((c, i), category, symptom["_label"], symptom["_lateralization"], symptom["_info"])
                    symptom_list.append(row)
            else:  # single entry, so it is a dictionary instead of a list of dictionaries
                symptom = self.symptoms[c]
                row = ((c, -1), category, symptom["_label"], symptom["_lateralization"], symptom["_info"])
                symptom_list.append(row)
        return symptom_list