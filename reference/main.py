# coding: utf-8

from lib import parser, region
from lib import globals as g

# these will be defined by the user later on
handedness = g.Constants.RIGHT
dominant_hemisphere = g.Constants.LEFT

if __name__ == "__main__":
    # load / parse JSON file containing items
    p = parser.Parser()
    p.load("data/items.json")
    p.parse()

    # initialize RegionList manager
    rl = region.RegionList()

    # define temporary list of items that we will be exporting, along with applicable information
    # to help sort into regions (ie side of symptom onset, lateralization of symptom, PPV)
    # do this part manually as the GUI is not yet implemented
    # this adds every symptom, with symptom onset side on the right
    n_categories = p.n_categories
    for c in range(n_categories):
        n_items = p.n_items[c]
        for i in range(n_items):
            # info dict to be passed along with each region being added
            info = {
                "symptom_onset_side": g.Constants.RIGHT,  # this will be defined by the user
                "handedness": handedness,
                "dominant_hemisphere": dominant_hemisphere 
            }
            if n_items == 1:  # handle case with only one item (nesting difference)
                rl.add(p.items[c], info)
            else:
                rl.add(p.items[c][i], info)
    
    # print(rl)

    # export regions list to textfile
    rl.export("output.3d")