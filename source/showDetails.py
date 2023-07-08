#!/usr/bin/env python3


# Functions for Alfred-Alphabet (aka Alfrabet) Workflow: 


import sys
import os
import json



def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


MYINPUTs = os.getenv('myDict').replace("'","\"")
MYINPUT = json.loads(MYINPUTs)




def main():


    result = {"items": []}
  
    content = list(MYINPUT.values())
    myLetter = list(MYINPUT.keys())[0]
    for x in content[0]:
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

    print (json.dumps(result))



if __name__ == '__main__':
    main ()



    

     
                
        
     
    



