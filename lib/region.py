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

from . import globals as g
from . import util

class RegionList:
    "Class to manage the list of Regions."

    def __init__(self):
        self.regions = []

    def __str__(self):
        string = ""
        for r in self.regions:
            string += (str(r) + " (" + str(r.votes) + " votes)\n")
        return string

    def reset(self):
        self.regions = []

    def add(self, item, info):
        "Add a new Region to the RegionList. If not unique, the pre-existing region's votes are incremented."

        # require that item and info are both of type dict
        if type(item) is not dict or type(info) is not dict:
            raise Exception("Function parameters must be of type dict.")

        # parse all information from our function input
        lobes = [s.strip() for s in item["_lobe"].lower().split(";")]
        locations = [s.strip() for s in item["_location"].lower().split(";")]    
        lateralization = item["_lateralization"].lower()   # must be a single value in JSON file
        ppv = item["_ppv"].lower()                         # must be a single value in JSON file
        onset_side = info["symptom_onset_side"]  # may be set to None, so be sure to check first
        handedness = info["handedness"].lower()
        dominant_hemisphere = info["dominant_hemisphere"].lower()

        if onset_side is not None:
            onset_side = onset_side.lower()

        # some minor error checking first
        if len(lobes) != len(locations):  # verify that number of lobes and locations is the same!
            raise Exception("Lobes and locations found in JSON file are not the same length. Please fix this and then try again.")
        if ppv not in g.Constants.POSSIBLE_PPVS:
            raise Exception("Unrecognized PPV. Please fix this in the JSON file.")

        # determine hemispheres (right, left, or both)
        if lateralization == g.Constants.IPSILATERAL:
            hemispheres = [onset_side]
        elif lateralization == g.Constants.CONTRALATERAL:
            hemispheres = [g.Constants.LEFT] if onset_side == g.Constants.RIGHT else [g.Constants.RIGHT]
        elif lateralization == g.Constants.DOMINANT:
            hemispheres = [dominant_hemisphere]
        elif lateralization == g.Constants.NONDOMINANT:
            hemispheres = [g.Constants.LEFT] if dominant_hemisphere == g.Constants.RIGHT else [g.Constants.RIGHT]
        else:  # if lateralization is "none", "undefined", or something else, then it is both
            hemispheres = [g.Constants.RIGHT, g.Constants.LEFT]  # add both hemispheres

        # If this region is unique, append it to the regions list and set its vote count to 
        # the PPV vote conversion. If not unique, find the pre-existing region and add this
        # region's votes to its vote counter.
        for hemisphere in hemispheres:
            for i, lobe in enumerate(lobes):
                location = locations[i]
                new_region = Region(hemisphere, lobe.replace(" ",""), location.replace(" ",""), util.Voting.ppv2votes(ppv))
                region_exists = False
                for region in self.regions:
                    if region == new_region:
                        region.votes += new_region.votes
                        region_exists = True
                        break
                if not region_exists:
                    self.regions.append(new_region)

    def export(self):
        "Prepare regions list for export to text file containing probabilities."

        # Go through the region list adjusting votes for all entries that contain an undefined
        # lobe or location. If the lobe is undefined, we add this region's votes to everything 
        # within the same hemisphere excluding itself. If the location is undefined, we add
        # this region's votes to everything within the same lobe excluding itself.
        for region in self.regions:
            if region.lobe == g.Constants.UNDEFINED:
                for r in self.regions:
                    if r != region and r.hemisphere == region.hemisphere:
                        r.votes += region.votes
            elif region.lobe != g.Constants.UNDEFINED and region.location == g.Constants.UNDEFINED:
                for r in self.regions:
                    if r != region and r.hemisphere == region.hemisphere and r.lobe == region.lobe:
                        r.votes += region.votes

        # convert vote counts to probabilities (region votes divided by total votes) and at
        # the same time prepare a string which will be saved to an output file
        string = ""
        total_votes = 0
        linebreak = "\n"
        for r in self.regions:
            total_votes += r.votes
        for i, r in enumerate(self.regions):
            if i == len(self.regions)-1:  # we are at the end, don't add linebreak
                linebreak = ""
            string += "%s\t%.5f%s" % (r, r.votes/total_votes, linebreak)
        
        # return output string that can be written to a file
        return string


class Region:
    "Class to store vote counts for each defined hemisphere / lobe / location."

    def __init__(self, hemisphere=None, lobe=None, location=None, votes=0):
        self.hemisphere = hemisphere
        self.lobe = lobe
        self.location = location
        self.votes = votes

    def __str__(self):
        "Return information about this region as a String when requested."
        return self.hemisphere + "." + self.lobe + "." + self.location

    def __eq__(self, other):
        "Define Region equality operator for == comparison in code."
        return self.hemisphere == other.hemisphere and self.lobe == other.lobe and self.location == other.location

    def equals(self, hemisphere, lobe, location):
        "Define Region equals function for comparison with non-Region Object, ie string values."
        return self.hemisphere == hemisphere and self.lobe == lobe and self.location == location

    def update(self, hemisphere=None, lobe=None, location=None):
        if hemisphere is not None:
            self.hemisphere = hemisphere
        if lobe is not None:
            self.lobe = lobe
        if location is not None:
            self.location = location