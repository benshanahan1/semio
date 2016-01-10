/*

Semiology Diagnostic Tool v1.0
Copyright (C) 2014 Benjamin Shanahan

---

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For documentation, please click in-application 'Help' button
or press the 'H' key while executing program
    
*/



//////////////////////////////
// imports and variables

import flash.display.MovieClip;
import flash.events.Event;
import xml_tree.XMLTree;
import src.*;
import fl.controls.CheckBox;
import fl.controls.Label;
import fl.controls.ComboBox;
import flash.events.MouseEvent;
import flash.events.KeyboardEvent;
import flash.ui.Keyboard;
import flash.net.FileReference;
import flash.net.FileFilter;
import flash.net.URLRequest;
import flash.net.URLLoader;
import flash.net.URLLoaderDataFormat;
import flash.events.IOErrorEvent;
import flash.display.Stage;
import flash.display.StageScaleMode;
import flash.display.StageAlign;
import flash.filesystem.File;
import flash.filesystem.FileMode;
import flash.filesystem.FileStream;
import flash.events.FocusEvent;
import flash.net.SharedObject;
import flash.errors.IOError;

// general variables
var uiSourceContainer:MovieClip = new MovieClip();
var xmlTree:XMLTree;
var displayList:Array;

// variables for sizing and spacing
var listButtonHeight:int = 20;
var listButtonWidth:int = 20;
var indent:int = 15;

// useful program constants
const DATA_XML_FILEPATH:String = "data.xml";
const CATEGORY:String = "category";
const ITEM:String = "item";
const PLUS:String = "plus";
const MINUS:String = "minus";
const SPACER:String = "_";
const PLACEHOLDER:String = "x";
const RIGHT:String = "right";
const LEFT:String = "left";
const BOTH:String = "both";
const NEWLINE:String = "\r\n";
const DOMINANT:String = "dominant";
const NONDOMINANT:String = "nondominant";
const CONTRALATERAL:String = "contralateral";
const IPSILATERAL:String = "ipsilateral";
const UNDEFINED:String = "undefined";
const NONE:String = "none";
const SCROLL_SPEED:int = 20;

// global variables for program operation
var handedness:String = RIGHT;
var dominantHemisphere:String = LEFT;
var fr:FileReference;
var urlPointersFilepath:String = "pointers.txt";
var helpURL:String;
var checkURL:String;
var dataURL:String;
var HIGH:String = "high";
var MODERATE:String = "moderate";
var LOW:String = "low";
var VOTE_COUNTS:Array = new Array(3, 2, 1, 0); // high votes, moderate votes, low votes, undefined votes
var DECIMAL_PRECISION:int = 4;
var typing:Boolean = false;
var loc_f:File;
var locator:SharedObject;
var clearLocator:Boolean = false; // debug variable, set to false unless you want to clear locator SharedObject

// IMPORTANT: KEEP THE FOLLOWING LINE UP-TO-DATE
const POINTERS_FILE_TEXT = "help_url=http://apps.bugeyedesigns.com/SemiologyDiagnosticTool/index.html&check_url=http://apps.bugeyedesigns.com/SemiologyDiagnosticTool/check.txt&data_url=http://apps.bugeyedesigns.com/SemiologyDiagnosticTool/data.xml";



//////////////////////////////
// debug

// if clearLocator is true, clear the locator SharedObject
locator = SharedObject.getLocal("semio_loc");

if (clearLocator)
{
    locator.data.loc = "";
    throw new Error("Locator variable cleared. Please set clearLocator back to false and restart.");
}



//////////////////////////////
// start program

init();



//////////////////////////////
// initialize application

function init():void
{
    // set scrollspeed of scrollpane and display area on stage
    uiScrollpane.verticalLineScrollSize = SCROLL_SPEED;
    uiScrollpane.horizontalLineScrollSize = SCROLL_SPEED;
    
    // set up the stage
    stage.scaleMode = StageScaleMode.NO_SCALE; // do not scale on resize
    stage.align = StageAlign.TOP_LEFT;
    
    // resize objects so they fit with screen
    resizeScreen();
    
    // calibrate objects on stage when stage is resized
    stage.addEventListener(Event.RESIZE, resizeHandler);
    
    // check internet connection, download data.xml, etc
    var urlLoader:URLLoader = new URLLoader();
    
    urlLoader.dataFormat = URLLoaderDataFormat.VARIABLES;
    urlLoader.addEventListener(Event.COMPLETE, pointersLoadHandler);
    urlLoader.addEventListener(IOErrorEvent.IO_ERROR, noPointersFile);
    urlLoader.load(new URLRequest(urlPointersFilepath));
}

function pointersLoadHandler(event:Event):void
{
    event.currentTarget.removeEventListener(Event.COMPLETE, pointersLoadHandler);
    
    helpURL = event.currentTarget.data.help_url;
    checkURL = event.currentTarget.data.check_url;
    dataURL = event.currentTarget.data.data_url;
    
    // now we load the data.xml file in
    xmlTree = new XMLTree(DATA_XML_FILEPATH);
    xmlTree.addEventListener(XMLTree.TREE_BUILT, treeBuiltHandler);
    xmlTree.addEventListener(XMLTree.XML_FILE_NOT_FOUND, xmlFileNotFoundHandler);
}

function noPointersFile(event:IOErrorEvent):void
{
    event.currentTarget.removeEventListener(IOErrorEvent.IO_ERROR, noPointersFile);
    
    displayArea.text = "";
    displayArea.appendText("Pointers file missing. Please re-download program from initial source." + NEWLINE + NEWLINE);
    displayArea.appendText("Alternatively, you can create a new text file (*.txt) in the same directory as this program. Name it 'pointers.txt' and paste the following text into it (Note - be sure that there are no spaces or newlines at the beginning or termination of the 'pointers.txt' file; if there are, a download error will likely occur). Please restart the program after creating 'pointers.txt'." + NEWLINE + NEWLINE);
    displayArea.appendText(POINTERS_FILE_TEXT + NEWLINE + NEWLINE);
    displayArea.appendText("If the location of the data, help, and check files have moved, simply insert their new locations into the pointers file in the corresponding sections. The correct pointers file construction is as follows: " + NEWLINE + NEWLINE);
    displayArea.appendText("help_url=[url to help file here]&check_url=[url to text file with text 'connected' here]&data_url=[url of data file here]");
}

function xmlFileNotFoundHandler(event:Event):void
{
    xmlTree.removeEventListener(XMLTree.XML_FILE_NOT_FOUND, xmlFileNotFoundHandler);
    
    checkInternet();
}

function checkInternet():void
{
    var connectionChecker:ConnectionChecker = new ConnectionChecker(checkURL, "connected");
    
    connectionChecker.addEventListener(ConnectionChecker.EVENT_ERROR, connectionError);
    connectionChecker.addEventListener(ConnectionChecker.EVENT_SUCCESS, connectionSuccess);
    connectionChecker.check();
}

function connectionSuccess(event:Event):void
{
    event.currentTarget.removeEventListener(ConnectionChecker.EVENT_SUCCESS, connectionSuccess);
    
    var fileDownload:FileDownload = new FileDownload(dataURL);
    
    displayArea.text = "";
    displayArea.appendText("Please save this file ('data.xml') in the same folder (at the same level) as this application." + NEWLINE + NEWLINE);
    displayArea.appendText("Please be patient and wait for this message area to confirm the external data file download. It could take up to a minute.");
    
    fileDownload.addEventListener(FileDownload.DOWNLOAD_COMPLETE, downloadCompleteHandler);
    fileDownload.startDownload();
}

function connectionError(event:Event):void
{
    event.currentTarget.removeEventListener(ConnectionChecker.EVENT_ERROR, connectionError);
    
    displayArea.text = "";
    displayArea.appendText("An error occurred:" + NEWLINE + NEWLINE);
    displayArea.appendText("We were unable to establish an internet connection to download the external 'data.xml' file." + NEWLINE + NEWLINE);
    displayArea.appendText("Please connect to the internet and restart the program. If you have the 'data.xml' file on your computer, please place it in the same directory as the program itself.");
}

function downloadCompleteHandler(event:Event):void
{   
    event.currentTarget.removeEventListener(FileDownload.DOWNLOAD_COMPLETE, downloadCompleteHandler);
    
    displayArea.text = "";
    displayArea.appendText("External data file successfully downloaded. Please restart program to continue.");
}

function nameInputFocusIn(event:FocusEvent):void
{
    typing = true;
}

function nameInputFocusOut(event:FocusEvent):void
{
    typing = false;
}



//////////////////////////////
// setup functions

function treeBuiltHandler(event:Event):void
{
    xmlTree.removeEventListener(XMLTree.TREE_BUILT, treeBuiltHandler);
    
    // disable right click content menu
    stage.addEventListener(MouseEvent.RIGHT_CLICK, rightClickHandler);
    
    // add event listeners
    contractListBtn.addEventListener(MouseEvent.CLICK, contractListHandler);
    expandListBtn.addEventListener(MouseEvent.CLICK, expandListHandler);
    handednessCombo.addEventListener(Event.CHANGE, setHandedness);
    dominantHemisphereCombo.addEventListener(Event.CHANGE, setDominantHemisphere);
    helpBtn.addEventListener(MouseEvent.CLICK, showHelpHandler);
    exportBtn.addEventListener(MouseEvent.CLICK, exportHandler);
    saveBtn.addEventListener(MouseEvent.CLICK, saveFileHandler);
    loadBtn.addEventListener(MouseEvent.CLICK, loadFileHandler);
    resetAllBtn.addEventListener(MouseEvent.CLICK, resetAllHandler);
    stage.addEventListener(KeyboardEvent.KEY_DOWN, shortcutHandler);
    nameInput.addEventListener(FocusEvent.FOCUS_IN, nameInputFocusIn);
    nameInput.addEventListener(FocusEvent.FOCUS_OUT, nameInputFocusOut);

    // set scrollpane source
    uiScrollpane.source = uiSourceContainer;
    
    initDisplayList();
    renderUiScrollpane();
}

function initDisplayList():void
{
    displayList = new Array();
    
    for (var k:int = 0; k < xmlTree.tree.categories.length; k++)
    {
        displayList.push(k + SPACER + PLACEHOLDER); // format: #_x, x = nonexistent, first num = category, then item; spacers separate numbers
    }
}

function renderUiScrollpane():void
{
    configureUiSourceContainer();
    uiScrollpane.update();
}

function contractList():void
{
    for (var i:int = 0; i < xmlTree.tree.categories.length; i++)
    {
        xmlTree.tree.categories[i].expanded = false;
    }
    
    initDisplayList();
    renderUiScrollpane();
}

function expandList():void
{
    displayList = new Array();
    
    for (var c:int = 0; c < xmlTree.tree.categories.length; c++)
    {
        xmlTree.tree.categories[c].expanded = true;
        displayList.push(c + SPACER + PLACEHOLDER);
        
        for (var i:int = 0; i < xmlTree.tree.categories[c].items.length; i++)
        {
            displayList.push(c + SPACER + i);
        }
    }
    
    renderUiScrollpane();
}

function resetTree():void
{
    for (var c:int = 0; c < xmlTree.tree.categories.length; c++)
    {
        for (var i:int = 0; i < xmlTree.tree.categories[c].items.length; i++)
        {
            xmlTree.tree.categories[c].items[i].checked = false;
        }
    }
}

function resetAll():void
{
    displayArea.text = "";
    resetAllComboBoxes();
    resetTree();
    contractList();
}



//////////////////////////////
// render functions

function resizeScreen():void
{
    // adjust certain elements with stage resize
    var sw:int = stage.stageWidth;
    var sh:int = stage.stageHeight;
    var yPos:int = sh - expandListBtn.height;
    
    // resize bottom buttons
    expandListBtn.width = sw / 5;
    contractListBtn.width = sw / 5;
    saveBtn.width = sw / 10;
    loadBtn.width = sw / 10;
    exportBtn.width = sw * 2 / 5;
    
    // reposition buttons
    helpBtn.x = sw - helpBtn.width - 10;
    resetAllBtn.x = sw - resetAllBtn.width - 10;
    helpBtn.y = 10;
    resetAllBtn.y = helpBtn.y + helpBtn.height + 10;
    contractListBtn.x = expandListBtn.width;
    saveBtn.x = contractListBtn.x + contractListBtn.width;
    loadBtn.x = saveBtn.x + saveBtn.width;
    exportBtn.x = loadBtn.x + loadBtn.width;
    expandListBtn.y = yPos;
    contractListBtn.y = yPos;
    loadBtn.y = yPos;
    saveBtn.y = yPos;
    exportBtn.y = yPos;
    
    // resize displayArea and uiScrollpane
    uiScrollpane.width = sw * 3 / 5;
    displayArea.width = sw * 2 / 5;
    uiScrollpane.height = sh - 108;
    displayArea.height = uiScrollpane.height;
    displayArea.x = uiScrollpane.width;
}

function configureUiSourceContainer():void
{
    removeAllChildren(uiSourceContainer);
    
    var cIDStr:String;
    var iIDStr:String;
    var cID:int;
    var iID:int;
    var categoryListButton:ListButton;
    var itemListButton:ListButton;
    var listCheckBox:ListCheckBox;
    var listComboBox:ListComboBox;
    var descriptionText:String = "";
        
    for (var i:int = 0; i < displayList.length; i++)
    {
        var spacers:Array = getIndices(displayList[i], SPACER);
        
        cIDStr = displayList[i].substring(0, spacers[0]);
        iIDStr = displayList[i].substring(spacers[0] + 1);
        
        if (cIDStr != PLACEHOLDER && iIDStr == PLACEHOLDER)
        {
            cID = int(cIDStr);
            
            if (xmlTree.tree.categories[cID].expanded)
            {
                categoryListButton = new ListButton(cID, -1, CATEGORY, MINUS);
            }
            else
            {
                categoryListButton = new ListButton(cID, -1, CATEGORY, PLUS);
                
            }
            
            categoryListButton.addEventListener(MouseEvent.CLICK, updateTree);
            addTo(uiSourceContainer, new Array(categoryListButton, 0, listButtonHeight * i), new Array(new ListLabel(xmlTree.tree.categories[cID].label), listButtonWidth, listButtonHeight * i));
        }
        else if (cIDStr != PLACEHOLDER && iIDStr != PLACEHOLDER)
        {
            var comboWidth:int = 60;
            
            iID = int(iIDStr);
            
            if (xmlTree.tree.categories[cID].items[iID].info != "none" && xmlTree.tree.categories[cID].items[iID].info != "undefined") // add description text to end of listCheckBox label
            {
                descriptionText = " (" + xmlTree.tree.categories[cID].items[iID].info + ")";
            }
            else
            {
                descriptionText = "";
            }
            
            // if item is contralateral or ipsilateral, user needs to specify which side of patient exhibited symptom; we then choose the opposite (opposite side of brain)
            if (xmlTree.tree.categories[cID].items[iID].lateralization == CONTRALATERAL || xmlTree.tree.categories[cID].items[iID].lateralization == IPSILATERAL)
            {
                listComboBox = new ListComboBox(cID, iID, new Array({label: "Right", data: RIGHT}, {label: "Left", data: LEFT}), comboWidth, comboWidth, 0); 
                
                if (xmlTree.tree.categories[cID].items[iID].sideWithSymptom == LEFT)
                {
                    listComboBox.selectedIndex = 1;
                }
                else // if sideWithSymptom == RIGHT
                {
                    listComboBox.selectedIndex = 0;
                    xmlTree.tree.categories[cID].items[iID].sideWithSymptom = RIGHT;
                }
                
                listComboBox.addEventListener(Event.CHANGE, symptomSideChosen);
            }
            
            listCheckBox = new ListCheckBox(cID, iID, xmlTree.tree.categories[cID].items[iID].label + descriptionText);
            listCheckBox.selected = xmlTree.tree.categories[cID].items[iID].checked;
            listCheckBox.addEventListener(MouseEvent.CLICK, updateSelectedItem);
            
            addTo(uiSourceContainer, new Array(listCheckBox, indent, listButtonHeight * i));
            
            if (listComboBox != null)
            {
                var offset:int = indent + listCheckBox.width;
                var subdivision:int = comboWidth;
                
                if (offset % subdivision != 0)
                {
                    offset += subdivision - (offset % subdivision); // just position combo boxes so they're more aligned w each other
                }
                
                addTo(uiSourceContainer, new Array(listComboBox, offset, listButtonHeight * i));
                listComboBox = null;
            }
        }
        else
        {
            trace("An error occurred: category index not specified (see configureuiSourceContainer() function)");
        }
    }
}

function updateTree(event:MouseEvent):void
{
    var thisCategoryID:int = event.currentTarget.categoryID;
    var thisItemID:int = event.currentTarget.itemID;
    var thisState:String = event.currentTarget.state;
    var thisType:String = event.currentTarget.type;
    
    if (thisType == CATEGORY)
    {
        xmlTree.tree.categories[thisCategoryID].expanded = (thisState == PLUS);
        
        if (thisState == PLUS)
            event.currentTarget.state = MINUS;
        else
            event.currentTarget.state = PLUS;
    }
    else if (thisType == ITEM)
    {
        xmlTree.tree.categories[thisCategoryID].items[thisItemID].expanded = (thisState == PLUS);
        
        if (thisState == PLUS)
            event.currentTarget.state = MINUS;
        else
            event.currentTarget.state = PLUS;
    }
    
    updateDisplayList(event.currentTarget.type, event.currentTarget.state, thisCategoryID, thisItemID);
    renderUiScrollpane();
}

function updateDisplayList(type:String, state:String, cID:int, iID:int):void
{
    var cStartIndex:int;
    var iStartIndex:int;
    var spacers:Array;
    var tempStr:String;
    var stopIndex:int;
    
    spacers = getIndices(displayList[m], SPACER);
    
    // set start indices
    for (var m:int = 0; m < displayList.length; m++)
    {
        
        tempStr = displayList[m].substring(0, spacers[0]);
        
        if (tempStr != PLACEHOLDER && int(tempStr) == cID)
        {
            cStartIndex = m;
            break;
        }
    }
    for (var n:int = cStartIndex; n < displayList.length; n++)
    {
        tempStr = displayList[n].substring(spacers[0] + 1, spacers[1]);
        
        if (tempStr != PLACEHOLDER && int(tempStr) == iID)
        {
            iStartIndex = n;
            break;
        }
    }
        
    // manipulate displayList
    if (type == CATEGORY)
    {
        if (state == PLUS)
        {
            stopIndex = getCategoryStopIndex(cStartIndex) - (cStartIndex + 1);
            
            if (stopIndex < 0)
                stopIndex = xmlTree.tree.categories[cID].items.length;
            
            displayList.splice(cStartIndex + 1, stopIndex); // substring takes LENGTH
        }
        else // state == MINUS
        {
            for (var i:int = 0; i < xmlTree.tree.categories[cID].items.length; i++)
            {
                displayList.splice(cStartIndex + i + 1, 0, cID + SPACER + i);
                xmlTree.tree.categories[cID].items[i].expanded = false;
            }
        }
    }
    else if (type == ITEM)
    {
        if (state == PLUS)
        {
            displayList.splice(iStartIndex + 1,  xmlTree.tree.categories[cID].items[iID].subselections.length);
        }
        else // state == MINUS
        {
            for (var s:int = 0; s < xmlTree.tree.categories[cID].items[iID].subselections.length; s++)
            {
                displayList.splice(iStartIndex + s + 1, 0, cID + SPACER + iID);
            }
        }
    }
}

function updateDisplayArea():void
{
    displayArea.textField.selectable = false;
    displayArea.text = "";
    
    for (var c:int = 0; c < xmlTree.tree.categories.length; c++)
    {
        for (var i:int = 0; i < xmlTree.tree.categories[c].items.length; i++)
        {
            if (xmlTree.tree.categories[c].items[i].checked)
            {
                displayArea.appendText(xmlTree.tree.categories[c].items[i].label);
                
                if (xmlTree.tree.categories[c].items[i].sideWithSymptom != null)
                    displayArea.appendText(" (" + xmlTree.tree.categories[c].items[i].sideWithSymptom + ")");
                
                displayArea.appendText(NEWLINE);
            }
        }
    }
}

function updatePatientInfo():void
{
    if (handedness == RIGHT)
        handednessCombo.selectedIndex = 0;
    else
        handednessCombo.selectedIndex = 1;
    
    if (dominantHemisphere == LEFT)
        dominantHemisphereCombo.selectedIndex = 0;
    else
        dominantHemisphereCombo.selectedIndex = 1;
}



//////////////////////////////
// update tree and selections

function updateSelectedItem(event:Event):void
{
    xmlTree.tree.categories[event.currentTarget.categoryID].items[event.currentTarget.itemID].checked = event.currentTarget.selected;
    updateDisplayArea();
}

function setHandedness(event:Event):void
{
    handedness = event.currentTarget.selectedItem.data;
}

function setDominantHemisphere(event:Event):void
{
    dominantHemisphere = event.currentTarget.selectedItem.data;
}

function updateSideWithSymptom(event:Event):void
{
    xmlTree.tree.categories[event.currentTarget.categoryID].items[event.currentTarget.itemID].sideWithSymptom = event.currentTarget.selectedItem.data;
    updateDisplayArea();
}

function symptomSideChosen(event:Event):void
{
    xmlTree.tree.categories[event.currentTarget.categoryID].items[event.currentTarget.itemID].sideWithSymptom = event.currentTarget.selectedItem.data;
    xmlTree.tree.categories[event.currentTarget.categoryID].items[event.currentTarget.itemID].checked = true;
    updateDisplayArea();
    renderUiScrollpane();
}



//////////////////////////////
// save / load / export functions and handlers

function saveFile():void
{
    if (nameInputValid())
    {
        var savedata:String = handedness + "_" + dominantHemisphere + "" + NEWLINE;
        var date:Date = new Date();
        var timestamp:String = (date.getMonth() + 1) + "" + date.date + String(date.fullYear).substring(2) + date.hours + date.minutes;
        var counter:int = 0;
        
        for (var c:int = 0; c < xmlTree.tree.categories.length; c++)
        {
            for (var i:int = 0; i < xmlTree.tree.categories[c].items.length; i++)
            {
                if (xmlTree.tree.categories[c].items[i].checked)
                {
                    savedata = savedata + c + SPACER + i + SPACER;
                    
                    savedata += xmlTree.tree.categories[c].items[i].sideWithSymptom + NEWLINE;
                    
                    counter++;
                }
            }
        }
        
        if (savedata.substring(savedata.length - 2) == NEWLINE) // remove extra line break at end of file
            savedata = savedata.substring(0, savedata.length - 2);
        
        if (counter > 0)
        {
            var fs:FileStream = new FileStream();
            var targetFile:File = File.documentsDirectory.resolvePath("Semiology Diagnostic Tool/Patients/" + nameInput.text + "_" + timestamp + ".patient");
            fs.open(targetFile, FileMode.WRITE);
            fs.writeUTFBytes(savedata);
            fs.close();
            
            displayArea.text = "Patient data successfully saved to file. File stored in \"/My Documents/Semiology Diagnostic Tool/Patients/\".";
        }
        else
            displayArea.text = "Save aborted. Please select patient symptoms first.";
    }
    else
    {
        displayArea.text = "Invalid patient name or file identifier. Must be alphanumeric characters, spaces, dashes, and underscores only.";
    }
}

function loadFile():void
{
    fr = new FileReference();
    fr.browse([new FileFilter("Patient files (*.patient)", "*.patient")]);
    fr.addEventListener(Event.SELECT, loadSelectedFile);
}

function export():void
{
    if (nameInputValid())
    {   
        var regionList:Array = new Array();
        var probabilityList:Array = new Array();
        var counter:int = 0;
        var stopExport:Boolean = false;
        
        // create a list of all regions
        for (var c:int = 0; c < xmlTree.tree.categories.length; c++)
        {
            for (var i:int = 0; i < xmlTree.tree.categories[c].items.length; i++)
            {
                if (xmlTree.tree.categories[c].items[i].checked)
                {
                    var possibleLobes:Array = removeChar(xmlTree.tree.categories[c].items[i].lobe, " ", false).split(";");
                    var possibleLocations:Array = removeChar(xmlTree.tree.categories[c].items[i].location, " ", false).split(";");removeChar(xmlTree.tree.categories[c].items[i].location, " ", true).split(";");
                    var thisHemisphere:String;
                    var thisLateralization:String = xmlTree.tree.categories[c].items[i].lateralization;
                    
                    if (possibleLobes.length == possibleLocations.length)
                    {
                        for (var l:int = 0; l < possibleLobes.length; l++)
                        {
                            var duplicateItem:Boolean = false;
                            var dupeAt:int = -1;
                            
                            // set thisHemisphere based on data file criteria
                            if (thisLateralization == IPSILATERAL)
                            {
                                thisHemisphere = xmlTree.tree.categories[c].items[i].sideWithSymptom;
                            }
                            else if (thisLateralization == CONTRALATERAL)
                            {
                                if (xmlTree.tree.categories[c].items[i].sideWithSymptom == RIGHT)
                                    thisHemisphere = LEFT;
                                else
                                    thisHemisphere = RIGHT;
                            }
                            else if (thisLateralization == DOMINANT)
                            {
                                thisHemisphere = dominantHemisphere;
                            }
                            else if (thisLateralization == NONDOMINANT)
                            {
                                if (dominantHemisphere == RIGHT)
                                    thisHemisphere = LEFT;
                                else
                                    thisHemisphere = RIGHT;
                            }
                            else // if (thisLateralization == NONE || thisLateralization == UNDEFINED)
                            {
                                thisHemisphere = BOTH;
                            }
                            
                            // before we do anything, check if this is gonna be a duplicate
                            for (var r:int = 0; r < regionList.length; r++)
                            {
                                if (thisHemisphere == regionList[r].hemisphere && possibleLobes[l] == regionList[r].lobe && possibleLocations[l] == regionList[r].location)
                                {
                                    duplicateItem = true;
                                    dupeAt = r;
                                }
                            }
                            
                            if (!duplicateItem)
                            {
                                if (thisHemisphere == BOTH)
                                {
                                    regionList.push(new Region(LEFT, possibleLobes[l], possibleLocations[l], convertToVotes(xmlTree.tree.categories[c].items[i].ppv)));
                                    regionList.push(new Region(RIGHT, possibleLobes[l], possibleLocations[l], convertToVotes(xmlTree.tree.categories[c].items[i].ppv)));
                                    
                                }                               
                                else
                                    regionList.push(new Region(thisHemisphere, possibleLobes[l], possibleLocations[l], convertToVotes(xmlTree.tree.categories[c].items[i].ppv)));
                                
                                counter++;
                            }
                            else
                            {
                                regionList[dupeAt].addVotes(convertToVotes(xmlTree.tree.categories[c].items[i].ppv));
                            }
                        }
                    }
                    else
                    {
                        displayArea.text = "Dimension mismatch in lobes and locations on item " + i + " in category " + c + ". Please correct data file.";
                        stopExport = true;
                    }
                }
            }
        }
        
        // add votes to locations contained in (undefined) lobes
        for (var region:int = 0; region < regionList.length; region++)
        {
            /** Loop pseudocode:
             *   If we find hemisphere.lobe.undefined (ie whole lobe is highlighted), give every 
             *   other matching hemisphere.lobe.location the votes of hemisphere.lobe.undefined
             */
            if (regionList[region].location == UNDEFINED)
            {
                // Create another loop and look through regionList again for regions contained in this lobe
                for (var r2:int = 0; r2 < regionList.length; r2++)
                {
                    if (regionList[r2].hemisphere == regionList[region].hemisphere && regionList[r2].lobe == regionList[region].lobe && regionList[r2].location != UNDEFINED)
                    {
                        regionList[r2].addVotes(regionList[region].votes);
                    }
                }
            }
        }
        
        // continue with export, but only if stopExport is false
        if (counter == 0)
        {
            displayArea.text = "Export aborted. Please select patient symptoms first, then click export.";
            stopExport = true;
        }
        else if (!stopExport)
        {
            var totalVotes:int = 0;
            
            for (var v:int = 0; v < regionList.length; v++)
            {
                totalVotes += regionList[v].votes;
            }
            
            // create array with all probabilities; corresponds directly to regionList array
            for (var p:int = 0; p < regionList.length; p++)
            {
                probabilityList.push(roundNumber(regionList[p].votes / totalVotes, DECIMAL_PRECISION));
            }
            
            // now save the exported data to a text file
            var savedata:String = "";
            var date:Date = new Date();
            var timestamp:String = (date.getMonth() + 1) + "" + date.date + String(date.fullYear).substring(2) + date.hours + date.minutes;
            
            for (var k:int = 0; k < regionList.length; k++)
            {
                savedata = savedata + regionList[k] + " " + probabilityList[k];
                
                if (k < regionList.length - 1)
                    savedata += NEWLINE;
            }
            
            var fs:FileStream = new FileStream();
            var targetFile:File = File.documentsDirectory.resolvePath("Semiology Diagnostic Tool/Export/" + nameInput.text + "_" + timestamp + ".3d");
            fs.open(targetFile, FileMode.WRITE);
            fs.writeUTFBytes(savedata);
            fs.close();
            
            // call semio
            runSemio(targetFile);
            
            // display export success
            displayArea.text = "Symptom probabilities exported. File stored in \"/My Documents/Semiology Diagnostic Tool/Export\".";
        }
    }
    else
    {
        displayArea.text = "Invalid patient name or file identifier. Must be alphanumeric characters, spaces, dashes, and underscores only.";
    }
}

function loadSelectedFile(event:Event):void
{
    fr.removeEventListener(Event.SELECT, loadSelectedFile);
    fr.addEventListener(Event.COMPLETE, parseLoadedFile);
    
    resetTree();
    fr.load();
}

function parseLoadedFile(event:Event):void
{
    var tempArray:Array = String(event.currentTarget.data).split(NEWLINE);
    
    // first index of tempArray is handedness and dominantHemisphere
    var spacersFirst:Array = getIndices(tempArray[0], SPACER);
    
    handedness = String(tempArray[0].substring(0, spacersFirst[0]));
    dominantHemisphere = String(tempArray[0].substring(spacersFirst[0] + 1));
    updatePatientInfo();
    
    for (var t:int = 1; t < tempArray.length; t++)
    {
        var spacers:Array = getIndices(tempArray[t], SPACER);
        var categoryStr:String = tempArray[t].substring(0, spacers[0]);
        var itemStr:String = tempArray[t].substring(spacers[0] + 1, spacers[1]);
        var sideWithSymptom:String = tempArray[t].substring(spacers[1] + 1);
        
        xmlTree.tree.categories[int(categoryStr)].items[int(itemStr)].checked = true;
        
        if (sideWithSymptom != "null")
        {
            xmlTree.tree.categories[int(categoryStr)].items[int(itemStr)].sideWithSymptom = sideWithSymptom;
        }
    }
    
    renderUiScrollpane();
    updateDisplayArea();
    
    fr.removeEventListener(Event.COMPLETE, parseLoadedFile);
}

function onProcessErrorHandler(event:Event):void
{
    trace("onProcessErrorHandler detected an error in NativeProcessStartupInfo.");
    //displayArea.text = "Failed to call Semiology rendering application. Please load application seperately and try again.";
}



//////////////////////////////
// utility functions

function addTo(parentObject:Object, ... objs)
{
    // IMPORTANT
    // objs should be constructed as follows, every parameter after the parentObject MUST be passed as an array: new Array(Object, xPos:int, yPos:int)
    for (var i:int = 0; i < objs.length; i++)
    {
        objs[i][0].x = objs[i][1];
        objs[i][0].y = objs[i][2];
        parentObject.addChild(objs[i][0]);
    }
}

function removeAllChildren(container:MovieClip):void
{
    while (container.numChildren > 0)
    {
        container.removeChildAt(0);
    }
}

function getIndices(haystack:String, needle:String):Array
{
    var returns:Array = [];
    var position:int = 0;
    
    while(haystack.indexOf(needle, position) > -1){
        var index:int = haystack.indexOf(needle, position);
        
        returns.push(index);
        position = index + needle.length;
    }
    
    return returns;
}

function getCategoryStopIndex(startIndex:int):int
{   
    // returns index of next type at same level as given type @ startIndex
    if (startIndex < 0)
        trace("Invalid start index.");
    
    var searchTerm:int = startIndex + 1;
    var spacers:Array;
    
    for (var d:int = startIndex; d < displayList.length; d++)
    {
        spacers = getIndices(displayList[d], SPACER);
        
        if ((int(displayList[d].substring(0, spacers[0]))) == searchTerm)
            return d;
    }
    //trace("[" + searchTerm + "] not found after index " + startIndex + " in " + displayList + "; item may have no neighbors or be at the end of display list");
    return -1;
}

function showHelp():void
{
    var request:URLRequest = new URLRequest(helpURL);
    try
    {
        navigateToURL(request);
    }
    catch (event:Error)
    {
        trace("Error occurred while trying to access help file. Please restart program, check internet connection, and try again.");
    }
}

function shortcutHandler(event:KeyboardEvent):void
{
    if (!typing)
    {
        switch(event.keyCode)
        {
            case Keyboard.EQUAL :
            case Keyboard.NUMPAD_ADD :
                expandList();
                break;
            case Keyboard.MINUS :
            case Keyboard.NUMPAD_SUBTRACT :
                contractList();
                break;
            case Keyboard.S :
                saveFile();
                break;
            case Keyboard.L :
                loadFile();
                break;
            case Keyboard.E :
                export();
                break;
            case Keyboard.H :
                showHelp();
                break;          
        }
        
        if (event.ctrlKey && event.keyCode == Keyboard.R) resetAll();
        if (event.keyCode == Keyboard.DOWN || event.keyCode == Keyboard.NUMPAD_2) uiScrollpane.verticalScrollPosition += SCROLL_SPEED;
        if (event.keyCode == Keyboard.UP || event.keyCode == Keyboard.NUMPAD_8) uiScrollpane.verticalScrollPosition -= SCROLL_SPEED;
        if (event.keyCode == Keyboard.LEFT || event.keyCode == Keyboard.NUMPAD_4) uiScrollpane.horizontalScrollPosition -= SCROLL_SPEED;
        if (event.keyCode == Keyboard.RIGHT || event.keyCode == Keyboard.NUMPAD_6) uiScrollpane.horizontalScrollPosition += SCROLL_SPEED;
    }
}

function removeChar(word:String, charToRemove:String, capitalizeFirstLetters:Boolean = true):String
{
   var words:Array = word.split(charToRemove);
   
   if (capitalizeFirstLetters)
   {
       for(var i in words)
       {
           words[i] = String(words[i]).charAt(0).toUpperCase() + String(words[i]).substr(1, String(words[i]).length).toLowerCase();
       }
   }
   
   return words.join("");
}

function resetAllComboBoxes():void
{
    handednessCombo.selectedIndex = 0;
    dominantHemisphereCombo.selectedIndex = 0;
    handedness = RIGHT;
    dominantHemisphere = LEFT;
    
    for (var c:int = 0; c < xmlTree.tree.categories.length; c++)
    {
        for (var i:int = 0; i < xmlTree.tree.categories[c].items.length; i++)
        {
            xmlTree.tree.categories[c].items[i].sideWithSymptom = null;
        }
    }
}

function convertToVotes(ppvString:String):int
{
    switch(ppvString)
    {
        case HIGH :
            return VOTE_COUNTS[0];
            break;
        case MODERATE :
            return VOTE_COUNTS[1];
            break;
        case LOW :
            return VOTE_COUNTS[2];
            break;
        case UNDEFINED :
            return VOTE_COUNTS[3];
            break;
        default :
            return -1;
            break;
    }
}

function roundNumber(num:Number, decimal:Number):Number
{
    var precision:Number = Math.pow(10, decimal);
    return Math.round(num * precision) / precision;
}

function nameInputValid():Boolean
{
    if (nameInput.text == "") return false;
    
    var rex:RegExp = /^[\w\-\s]+$/;
    
    return (nameInput.text.match(rex) != null);
}

function runSemio(f:File):void
{
    if (NativeProcess.isSupported)
    {
        // check if we can find text file pointing to Semio / update global vars
        locator = SharedObject.getLocal("semio_loc");
        loc_f = f;
        
        if (locator.size > 0)
        {
            // check that this location works
            var urlRequest:URLRequest = new URLRequest(locator.data.loc);
            var urlLoader:URLLoader = new URLLoader();
            urlLoader.dataFormat = URLLoaderDataFormat.BINARY;
            urlLoader.addEventListener(Event.COMPLETE, semioExists);
            urlLoader.addEventListener(IOErrorEvent.IO_ERROR, semioNotFound);
            urlLoader.load(urlRequest);
        }
        else
        {
            displayArea.text = "Semio program not found. Please select it now.";
            selectSemioDir(locator);
        }
    }
    else
    {
        // display message saying that we're unable to launch
        displayArea.text = "Unfortunately, your machine does not support launching Semio directly from this tool. Please load Semio separately and then press Ctrl+O to open / view your exported symptoms.";
    }
}

function selectSemioDir(s:SharedObject):void
{
    // SemioDir is nonexistant, prompt user to select location of Semiology.exe
    var f:File = new File();
    
    f.addEventListener(Event.SELECT, browseForSemioHandler);
    f.browse([new FileFilter("Executables","*.exe")]);
}

function browseForSemioHandler(e:Event):void
{
    e.target.removeEventListener(Event.SELECT, browseForSemioHandler);
    
    var path:String = e.target.nativePath;
    
    if (path.length > 0)
    {
        displayArea.text = "Semio directory successfully set.";
        
        var apploc:String = path;
        
        locator.data.loc = apploc;
        locator.flush();
        
        // now that we've selected semio dir, if this directory is nonempty, rerun runSemio()
        if (locator.size > 0)
        {
            runSemio(loc_f);
        }
    }
    else
    {
        displayArea.text = "An error occurred! Try selecting the Semio .exe location again (click export).";
    }
    
    return; // return
}

function semioExists(e:Event):void 
{
    e.target.removeEventListener(Event.COMPLETE, semioExists);
    
    // the file exists! now execute Semiology.exe with args
    var process:NativeProcess = new NativeProcess();
    var nativeProcessStartupInfo:NativeProcessStartupInfo = new NativeProcessStartupInfo();
    var args:Vector.<String> = new Vector.<String>; 
    
    // write our args!
    var pathURL:String = loc_f.url.substr(8); // remove File:/// from beginning of URL
    var splitPathURL:Array = pathURL.split("%20");
    pathURL = splitPathURL.join(" "); // replace %20 with spaces
    args.push(pathURL);
    trace(pathURL);
    
    // configure nativeProcessStartupInfo
    nativeProcessStartupInfo.arguments = args;
    nativeProcessStartupInfo.executable = new File(locator.data.loc);
    
    // execute nativeProcess using nativeProcessStartupInfo
    process.addEventListener(ProgressEvent.STANDARD_ERROR_DATA, onProcessErrorHandler);  
    process.start(nativeProcessStartupInfo);
    process.standardInput.writeUTFBytes(args + "\n");
}

function semioNotFound(e:IOErrorEvent):void
{
    e.target.removeEventListener(IOErrorEvent.IO_ERROR, semioNotFound);
    
    displayArea.text = "Semio program not found. Please select it now.";
    
    selectSemioDir(locator);
}



//////////////////////////////
// Redirect handlers (directly call another function)

function saveFileHandler(event:MouseEvent):void
{
    saveFile();
}

function loadFileHandler(event:MouseEvent):void
{
    loadFile();
}

function exportHandler(event:MouseEvent):void
{
    export();
}

function resizeHandler(event:Event):void
{
    resizeScreen();
}

function rightClickHandler(event:MouseEvent):void
{
    // do nothing
}

function resetAllHandler(event:MouseEvent):void
{
    resetAll();
}

function expandListHandler(event:MouseEvent):void
{
    expandList();
}

function contractListHandler(event:MouseEvent):void
{
    contractList();
}

function showHelpHandler(event:MouseEvent):void
{
    showHelp();
}