#!/usr/bin/env python3


# Functions for Alfred-Alphabet (aka Alfrabet) Workflow: 


import sys
import os
import plistlib
import re
import json
import csv



from config import DIRNAME, PREFIXES, log, WF_CUSTOM, INCLUDE_DISABLED
prefixes = (PREFIXES or '').split(' ')


MYINPUT = sys.argv[1]


# summary string glyphs: workflow, custom hotkey, both, unused
yesS = '🟢'
yesC = '🟠'
yesSS = '🔴'
noS = '⚪'

BASE_LETTERS = 'abcdefghijklmnopqrstuvwxyz'

#order for summary string
# none-custom prefixes - 4 single keys - 3 combo - 2 combo 1 combo
# example:
# ⚪-⚪⚪⚪-⚪⚪⚪⚪-⚪⚪⚪-⚪⚪-⚪-⚪⚪⚪-⚪
MY_KEY_ORDER = [
    'sht',
    'ctl',
    'opt',
    'cmd',

    'spacer', #non existing key, corresponding to hyphen

    'sht-ctl',
    'sht-opt',
    'sht-cmd',

    'spacer', #non existing key, corresponding to hyphen

    'ctl-opt',
    'ctl-cmd',

    'spacer', #non existing key, corresponding to hyphen

    'opt-cmd',

    'spacer', #non existing key, corresponding to hyphen

    'sht-ctl-opt',
    'sht-ctl-cmd',
    'ctl-opt-cmd',

    'spacer', #non existing key, corresponding to hyphen
    'sht-ctl-opt-cmd',
    ]






def check_string(string):
    
    
    prefix_pattern = '|'.join(re.escape(prefix) for prefix in prefixes)
    pattern = r'^(' + prefix_pattern + r')([\w!@#$%^&*()_])$'  # Regular expression pattern
    
    match = re.match(pattern, string)
    if (len (string) == 1):
        prefix = 'none'
        letter = string
        
    elif match:
        prefix = match.group(1)
        letter = match.group(2)
    
    else:
        prefix = ''
        letter =''
        
    return prefix, letter


def fetchCustomVariable (userConfig, myVarName,myPrefPath):
    variable_value = ''  # Default value if variable is not found

    for item in userConfig:
        if item['variable'] == myVarName:
            variable_value = item['config']['default']
            break
    try:
        with open(myPrefPath, 'rb') as fp:
            myPrefs = plistlib.load(fp)
            #log (f"MYPREFS:++++++ {myPrefs}")
            variable_value = myPrefs[myVarName]
            #log (f"{myVarName}: using {variable_value}")
    except:
        log (f"{myVarName}: ===pref value absent==, using default {variable_value}")
        

    return variable_value

def fetchCustomHotkeys (): 

    # if custom.csv does not exist, create it with demo data
    if not os.path.exists(WF_CUSTOM):
        data = [
            ['Letter', 'Modifier', 'Command or application'],
            ['Q', 'ctl-cmd', 'Lock Screen'],
            ['C', 'cmd', 'Copy'],
            ['V', 'cmd', 'Paste'],
            ['Q', 'sht-cmd', 'Log out']
        ]
        with open(WF_CUSTOM, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        log (f"CSV file '{WF_CUSTOM}' created successfully.")
        customAlphabet =[]
        with open(WF_CUSTOM, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customAlphabet.append(row)
        return customAlphabet
    else:
        customAlphabet =[]
        with open(WF_CUSTOM, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                customAlphabet.append(row)
        return customAlphabet



def buildAlphabet():

    # this information is borrowed from (com.help.shawn.rice) by Shawn Rice
    hotmod = {
                    131072 : "sht",
                    262144 : "ctl",
                    262401 : "ctl", # https://github.com/shawnrice/alfred2-workflow-help/pull/2/files
                    393216 : "sht-ctl",
                    524288 : "opt",
                    655360 : "sht-opt",
                    786432 : "ctl-opt",
                    917504 : "sht-ctl-opt",
                    1048576 : "cmd",
                    1179648 : "sht-cmd",
                    #1048576 : "ctl-cmd",
                    1310720: "ctl-cmd",
                    1310985 : "ctl-cmd", 
                    1441792 : "sht-ctl-cmd",
                    1572864 : "opt-cmd",
                    1703936 : "sht-opt-cmd",
                    1835008 : "ctl-opt-cmd",
                    1966080 : "sht-ctl-opt-cmd"
    }

    
    dirs = [f for f in os.listdir(DIRNAME) if os.path.isdir(os.path.join(DIRNAME, f))]
    alphabet = {}
    

    # I want to create a list of dictionaries, one per workflow. Each dictionary will have workflow name, a list of hotkeys, and a list of keywords
    for (idx,d) in enumerate(dirs): # goes through each directory looking for a plist file. idx is a counter from enumerate, d is the directory (and plist file) name
        
        try:
            myPlistPath = (os.path.join(DIRNAME, d, 'info.plist'))
            myPrefPath = (os.path.join(DIRNAME, d, 'prefs.plist'))
            myPath = (os.path.join(DIRNAME, d))
            
            with open(myPlistPath, 'rb') as fp:
                myPlist = plistlib.load(fp)
                
        except:
            continue
                
        if myPlist['disabled'] == True:
            if (INCLUDE_DISABLED == "0"): 
                log (f"skipping {myPlist['name']} (disabled)")
                continue
        ## KEYWORDS
        try:
            # fetching keywords in each workflow, adding them to myKeyList
            myKeyList=[]
            #log (f"Looking for keywords for {myPlist['name']}")
            myObjects = myPlist['objects']
            for o in myObjects:
                # retrieving all the keys for the current workflow
                if ('alfred.workflow.input' in o['type']) and ('keyword' in o['config']):
                    
                    # if the keyword is set in Workflow Configuration: retrieve the variable name and fetch the value from the prefs file
                    if o['config']['keyword'].startswith("{var:"):
                        myVarName = o['config']['keyword'].split(':')[1][:-1]
                        
                        try:
                            myCustomKey = fetchCustomVariable (myPlist['userconfigurationconfig'],myVarName, myPrefPath)
                            if myCustomKey:
                                myKeyList.append (myCustomKey)
                        except:
                            log (f"Custom key for {myPlist['name']} not found")
                       
                    # standard keyword
                    elif (o['config']['keyword']):
                        #log (o['config']['keyword'])
                        myKeyList.append (o['config']['keyword'])
            
            # checking if any of the keys match criteria
            for myKey in myKeyList:
                #log (f"{myPlist['name']}: ========= {myKey}")
                prefix, letter = check_string (myKey)
                if letter:
                    #log (letter)
                    alphabet.setdefault(letter, []).append({'name': myPlist['name'], 'type': 'workflow', 'prefix': prefix, 'path': myPath,'bundle': myPlist['bundleid']})
                    #log (f"{myPlist['name']}: matching key:========= {myKey}")
                    
                    
        except KeyError:
            log (f"{myPlist['name']}: NO keywords=========")
            continue
                

        ## HOTKEYS
        myHotkeys = []  # reset per workflow: a KeyError below must not reuse the previous workflow's hotkeys
        try:
            # all the hotkeys in each workflow, use hotmod to convert the ID to a string
            myHotkeys = [hotmod[o['config']['hotmod']]+"-"+o['config']['hotstring'].lower()
                for o in myPlist['objects']
                if 'alfred.workflow.trigger.hotkey' in o['type']
                and o['config']['hotmod'] != 0 and o['config']['hotkey'] != 0]
        except KeyError:
            log (f"{myPlist['name']}: KEY ERROR")
            # currenty this error happens if there is an empty hotkey and no workflow configuration (so older workflows) and it should be harmless
                
        for myHot in myHotkeys:
            letter = myHot [-1]
            prefix = myHot [:-2]
            alphabet.setdefault(letter, []).append({'name': myPlist['name'], 'type': 'workflow','prefix': prefix, 'path': myPath,'bundle': myPlist['bundleid']})
        

    
    customAlphabet = fetchCustomHotkeys()
    for xx in customAlphabet:
        alphabet.setdefault(xx['Letter'].casefold(), []).append({'name': xx['Command or application'], 'type': 'custom','prefix': xx['Modifier'],'path': 'icons','bundle': 'none'})
    
    alphabet = {k: alphabet[k] for k in sorted(alphabet.keys())}
    #log (alphabet)

    return alphabet


def fetchPlists():
    alphabet = buildAlphabet()


    
    result = {"items": []}
    myKeyOrder = MY_KEY_ORDER
    # compiling the default summary string (here is the place where one could add systemwide shortcuts)
    if prefixes == ['']:
        customPrefString = ''    
    else:
        customPrefString = '-'+ '⚪'*len(prefixes)
    
    
    if MYINPUT:
        filteredAlpha = {key: value for key, value in alphabet.items() if key == MYINPUT.casefold()}
    else: 
        filteredAlpha = alphabet
    
    for key, values in filteredAlpha.items():
        summaryString = f'⚪{customPrefString}-⚪⚪⚪⚪-⚪⚪⚪-⚪⚪-⚪-⚪⚪⚪-⚪'
        summarySubtitle = [key]
        myCounter = 0

        single_letter = any(d.get('prefix') == 'none' for d in values)
        
        # creating a summary emoji string
        if single_letter == True:
            summaryString = summaryString[:0] + yesS + summaryString[0+1:]
            summarySubtitle.append(values[0]['prefix'])
        myCounter += 2
        
        if prefixes != ['']:
            for myPrefix in prefixes:
                has_prefix = any(d.get('prefix') == myPrefix for d in values)
                if has_prefix == True:
                    summaryString = summaryString[:myCounter] + yesS + summaryString[myCounter+1:]
                    summarySubtitle.append(myPrefix)
                myCounter += 1
            myCounter += 1

        
    
        myPrefCounter = 0        
        for myHotkey in myKeyOrder:
            
            
            
            
            
            custom_hotkey = any((d.get('type') == 'custom' and d.get('prefix') == myHotkey) for d in values)
            if custom_hotkey:
                summaryString = summaryString[:(myCounter+myPrefCounter)] + yesC + summaryString[(myCounter+myPrefCounter+1):]
                summarySubtitle.append(myHotkey)                            
            
            workflow_hotkey = any((d.get('type') == 'workflow' and d.get('prefix') == myHotkey) for d in values)
            if workflow_hotkey:
                summaryString = summaryString[:(myCounter+myPrefCounter)] + yesS + summaryString[(myCounter+myPrefCounter+1):]
                summarySubtitle.append(myHotkey)
            
            if custom_hotkey and workflow_hotkey:
            
                summaryString = summaryString[:(myCounter+myPrefCounter)] + yesSS + summaryString[(myCounter+myPrefCounter+1):]
            myPrefCounter += 1
        


        
        summarySubtitleString = ",".join(summarySubtitle[1:])
        summarySubtitleStringLarge = summarySubtitle[0] + ': ' + ",".join(summarySubtitle[1:])
        result["items"].append({
                "title": f"{summaryString}",
                'subtitle': summarySubtitleString,
                'valid': True,
            
            "mods": {
                    "ctrl": {
                        "valid": True,
                        "subtitle": "Show summary in large font",
                        "variables": {
                            'mySummary': f"{summaryString}\n{summarySubtitleStringLarge}",
                            
                    },
                        },
                
                },
                'variables': {
                    'myDict': json.dumps({key: alphabet[key]}),
                    'myKey': key
                },
                "icon": {
                    "path": f'icons/{key}.png'
                },
                'arg': ''
                    }) 

    

    if MYINPUT and not filteredAlpha:
        if len (MYINPUT) == 1:
            myString = f"No single-letter keywords of hotkeys with {MYINPUT}"
        else: 
            myString = f"{MYINPUT}: invalid query. Enter one letter!"
        result["items"].append({
                "title": myString,
                'subtitle': "Try another query 🔤",
                'valid': True,
            
                "icon": {
                    "path": f'icons/warning.png'
                },
                'arg': ""
                    }) 

    print (json.dumps(result))  


    

     
                
        
     
    





def prefixLabel (myPrefix):
    # 'none' is how single-letter keywords (no prefix at all) are stored
    return 'no prefix' if myPrefix == 'none' else myPrefix


def letterBlocks (alphabet):
    # a-z always first and always in the same position, so that the same column
    # means the same letter in every row; anything else in use (digits, symbols)
    # goes in a final block
    blocks = [BASE_LETTERS[i:i+5] for i in range(0, len(BASE_LETTERS), 5)]
    extras = ''.join(sorted(k for k in alphabet if k not in BASE_LETTERS))
    if extras:
        blocks.append(extras)
    return blocks


def prefixSummary (myPrefix, alphabet, blocks):
    # one circle per letter, same color code as the by-letter view
    summaryBlocks = []
    myLetters = []
    for block in blocks:
        summaryBlock = ''
        for letter in block:
            values = [d for d in alphabet.get(letter, []) if d.get('prefix') == myPrefix]
            workflow_key = any(d.get('type') == 'workflow' for d in values)
            custom_key = any(d.get('type') == 'custom' for d in values)

            if workflow_key and custom_key:
                summaryBlock += yesSS
            elif workflow_key:
                summaryBlock += yesS
            elif custom_key:
                summaryBlock += yesC
            else:
                summaryBlock += noS
                continue
            myLetters.append(letter)
        summaryBlocks.append(summaryBlock)

    return '-'.join(summaryBlocks), myLetters


def fetchByPrefix():
    # the by-letter view transposed: one row per prefix/modifier, one circle per letter
    alphabet = buildAlphabet()
    blocks = letterBlocks(alphabet)

    usedPrefixes = {d['prefix'] for values in alphabet.values() for d in values}

    # no prefix and the user's own prefixes are always listed (an empty row means
    # the whole alphabet is still free there); modifiers only when in use
    myPrefixes = ['none'] + [p for p in prefixes if p]
    myPrefixes += [k for k in MY_KEY_ORDER if k != 'spacer' and k in usedPrefixes]

    if MYINPUT:
        myQuery = MYINPUT.casefold()
        myPrefixes = [p for p in myPrefixes if myQuery in prefixLabel(p).casefold()]

    result = {"items": []}
    for myPrefix in myPrefixes:
        summaryString, myLetters = prefixSummary(myPrefix, alphabet, blocks)
        myLabel = prefixLabel(myPrefix)
        summarySubtitle = ",".join(myLetters) if myLetters else 'no keywords or hotkeys'
        summarySubtitleLarge = f"{myLabel}: {summarySubtitle}"

        myDict = {letter: [d for d in alphabet[letter] if d.get('prefix') == myPrefix]
            for letter in myLetters}

        myIcon = f'icons/{myPrefix}.png'
        if not os.path.exists(myIcon):
            myIcon = 'icons/icon.png'

        result["items"].append({
                "title": f"{summaryString}",
                'subtitle': f"{myLabel}: {summarySubtitle}",
                'valid': True,

            "mods": {
                    "ctrl": {
                        "valid": True,
                        "subtitle": "Show summary in large font",
                        "variables": {
                            'mySummary': f"{summaryString}\n{summarySubtitleLarge}",

                    },
                        },

                },
                'variables': {
                    'myDict': json.dumps(myDict),
                    'myKey': myPrefix
                },
                "icon": {
                    "path": myIcon
                },
                'arg': ''
                    })

    if not result["items"]:
        if MYINPUT:
            myString = f"No prefix or modifier matching {MYINPUT}"
        else:
            myString = "No prefixes to show"
        result["items"].append({
                "title": myString,
                'subtitle': "Try another query, or add prefixes in Workflow Configuration 🔤",
                'valid': True,

                "icon": {
                    "path": f'icons/warning.png'
                },
                'arg': ""
                    })

    print (json.dumps(result))
