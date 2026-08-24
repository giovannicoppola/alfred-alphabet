#!/usr/bin/env python3


# Functions for Alfred-Alphabet (aka Alfrabet) Workflow: 


import sys
import os
import json



def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


myDictRaw = os.getenv('myDict')
MYINPUT = json.loads(myDictRaw) if myDictRaw else {}

# one character filters by letter (the point of the by-prefix view: the letter
# you are after can be far down the list), anything longer by workflow name
MYQUERY = (sys.argv[1] if len(sys.argv) > 1 else '').strip().casefold()




def main():


    result = {"items": []}

    # one entry per letter in the by-letter view, one per prefix (so possibly
    # several letters) in the by-prefix view
    for myLetter, values in sorted(MYINPUT.items()):
        if len(MYQUERY) == 1 and myLetter.casefold() != MYQUERY:
            continue
        for x in values:
            if len(MYQUERY) > 1 and MYQUERY not in x['name'].casefold():
                continue
            if x['prefix'] == 'none':
                prefString = ''
            else:
                prefString = x['prefix']+'-'
            result["items"].append({
                "title": f"{x['name']}: {prefString}{myLetter}",
                'subtitle': f"{x['prefix']}",

                'variables': {
                    'myBundle': x['bundle']
                },

                "icon": {
                    "path": f"{x['path']}/icon.png"
                },
                'arg':  ""
                    })

    if not result["items"]:
        result["items"].append({
            "title": f"Nothing matching {MYQUERY}" if MYQUERY else "Nothing to show",
            'subtitle': "Enter a letter, or part of a workflow name \U0001F524",
            'valid': False,

            "icon": {
                "path": f'icons/warning.png'
            },
            'arg':  ""
                })

    print (json.dumps(result))



if __name__ == '__main__':
    main ()



    

     
                
        
     
    



