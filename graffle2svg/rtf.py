
from styles import CascadingStyles

def isint(i):
    try:
        int(i)
        return True
    except:
        return False

def extractRTFString(s):
    """Extract a string and some styling info"""
    bracket_depth = 0
    instruction = False
    inst_code = ""
    
    # The string being generated:
    std_string = ""
    style = CascadingStyles()
    # Want to set these as defaults even if not specified
    style.appendScope()
    style["fill"]="#000000"
    """TODO: 
     extract styling 
     
     e.g. 
     {\rtf1\ansi\ansicpg1252\cocoartf949\cocoasubrtf460
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\ql\qnatural\pardirnatural

\f0\fs28 \cf0 Next ads are represented in a book-ended carousel on end screen}
    """
    
    def do_instruction(inst_code):
        if inst_code == "b":
            style["font-weght"] = "bold"
        if inst_code == "ql":
            style["text-align"] = "left"
        elif inst_code == "qr":
            style["text-align"] = "right"
        elif inst_code == "qj":
            style["text-align"] = "justify"
        elif inst_code == "qc":
            style["text-align"] = "center"
        elif inst_code[:2]=="fs" and isint(inst_code[2:]):
            # font size - RTF specifies half pt sizes
            style["font-size"] = "%.1fpt"%(float(inst_code[2:])/2.)
        elif inst_code[:2]=="cf" and isint(inst_code[2:]):
            # font colour is enytry int(inst_code[2:]) in the colour table :-(
            # font is chosen from font table using fN (N\in\int)
            pass
    
    for c in s:
        if c == "{":
            bracket_depth +=1
            style.appendScope()
        elif c == "}":
            if std_string != "":
                yield {"string":std_string, "style":str(style)}
                std_string = ""
            style.popScope()
            bracket_depth -=1
        elif c == "\\":
            if len(inst_code) > 0:
                do_instruction(inst_code)
            instruction = True
            inst_code = ""
        
        if instruction:
            if c == " ":
                instruction = False
                do_instruction(inst_code)
            elif c == "\n":
                instruction = False
                if inst_code == "":
                    # new line so yield
                    yield {"string":std_string, "style":str(style)}
                    std_string = ""
                else:
                    do_instruction(inst_code)
            elif c != "\\":
                inst_code += c

        else:
            if bracket_depth == 1:
                if not c in "{}\\\n\r":
                    # those characters are escaped
                    std_string += c
    style.popScope()
