#!/usr/bin/python
#Copyright (c) 2009, Tim Wintle
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#    * Neither the name of the project nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import xml.dom.minidom
from rtf import extractRTFString
from styles import CascadingStyles
import geom
import fileinfo

def mkHex(s):
    # s is a string of a float
    h = "%x"%(int(float(s)*256))
    if h[0] == " ":
        h="0"+h[1]
    return h

def nodeListGen(nodelist):
    """We need this so we can pass continuations around"""
    for e in nodelist:
        yield e
        
def parseCoords(s):
    """in: "{0,1}" -> [0,1]"""
    return [float(a) for a in s[1:-1].split(",")]

class GraffleParser(object):
    g_dom = None
    svg_dom = None
    svg_current_layer = None
    svg_current_font  = ""
    svg_def = None
    
    def __init__(self):
        self.svg_dom = xml.dom.minidom.Document()
        self.svg_dom.doctype = ""
        svg_tag = self.svg_dom.createElement("svg")
        svg_tag.setAttribute("xmlns","http://www.w3.org/2000/svg")
        svg_tag.setAttribute("xmlns:xlink","http://www.w3.org/1999/xlink")
        self.svg_dom.appendChild(svg_tag)
        def_tag = self.svg_dom.createElement("defs")
        svg_tag.appendChild(def_tag)
        self.svg_def = def_tag
        
        # set of required macros
        self.required_defs = set()
        
        self.style = CascadingStyles()
        self.style.appendScope()
        self.style["fill"]="#fff"
        self.style["stroke"]="#000000"

        graphic_tag = self.svg_dom.createElement("g")
        graphic_tag.setAttribute("style",str(self.style))
        svg_tag.appendChild(graphic_tag)
        self.svg_current_layer = graphic_tag        
                
        
    @property
    def svg(self):
        """Return the svg document"""
        return self.svg_dom.toprettyxml()
        
    def walkGraffle(self, xmlstr, **kwargs):
        """Walk over the file"""
        self.g_dom = xml.dom.minidom.parseString(xmlstr)
        
        self.walkGraffleDoc(self.g_dom, **kwargs)
        self.svg_add_requirements()
        
        
    def walkGraffleDoc(self, parent, page = 0):
        # want to pass this around like a continuation
        cont = nodeListGen(parent.childNodes)
        i = 0
        mydict = None
        for e in cont:
            if e.nodeType == e.DOCUMENT_TYPE_NODE:
                pass
            localname = e.localName
            
            if localname == "plist":
                # Apple's main container
                self.walkGraffleDoc(e)
                
            if localname == "dict":
                mydict = self.ReturnGraffleDict(e)

        if mydict is not None:
            # Extract file information
            self.fileinfo = fileinfo.FileInfo(mydict)
            # Graffle lists it's image references separately
            self.imagelist = mydict.get("ImageList",[])
            # Sometimes have multiple sheets
            if mydict.get("Sheets") is not None:
                self.extractPage(mydict["Sheets"][page])
            else:
                self.extractPage(mydict)
                
                
    def extractPage(self, grafflenodeasdict):
        mydict = grafflenodeasdict
        
        if self.fileinfo.fmt_version >= 6:
            # Graffle version 6 has a background graphic
            background = mydict["BackgroundGraphic"]
            # draw this 
            self.svgItterateGraffleGraphics([background])
        elif self.fileinfo.fmt_version < 6:
            # Version 5 has a CanvasColor property instead
            colour = mydict["CanvasColor"]
            sty = {}
            
            # We have to guess the document's dimensions from the print size
            # - these numbers appear to match up with the background size in 
            #  version 6.
            origin = parseCoords(mydict.get("CanvasOrigin","{0,0}"))
            print_info = self.fileinfo.printinfo
            
            paper_size = print_info.paper_size
                    
            Lmargin = print_info.left_margin
            Rmargin = print_info.right_margin
            Tmargin = print_info.top_margin
            Bmargin = bottom_margin
            
            x, y   = origin
            width  = paper_size[0] - Lmargin - Rmargin
            height = paper_size[1] - Bmargin - Tmargin
            self.svg_addRect(self.svg_current_layer,
                                    x = x,
                                    y = y,
                                    width = width,
                                    height = height,
                                    rx=None,
                                    ry=None)
        
        graphics = mydict["GraphicsList"]
        self.svgItterateGraffleGraphics(graphics)
        
    def ReturnGraffleNode(self, parent):
        """Return a python representation of the 
           node passed"""
        if parent.nodeType == parent.TEXT_NODE:
            return parent.wholeText
        elif parent.localName == "dict":
            return self.ReturnGraffleDict(parent)
        elif parent.localName == "array":
            return self.ReturnGraffleArray(parent)
        elif parent.localName == "true":
            return True
        elif parent.localName == "false":
            return False
        elif parent.localName in ["string","real","int"]:
            return self.ReturnGraffleNode(parent.firstChild)
        return parent.nodeType
        
    def ReturnGraffleDict(self, parent):
        """Graffle has dicts like
            <dict>
                <key />
                <integer />
                <key />
                <string />
            </dict>
            - pass the <dict> node to this method
        """
        retdict = {}
        cont = nodeListGen(parent.childNodes)
        key, val = None, None
        for e in cont:
            if e.nodeType == e.TEXT_NODE:
                continue
            localname = e.localName
            if localname == "key":
                key = self.ReturnGraffleNode(e.firstChild)
            else:
                val = self.ReturnGraffleNode(e)
                retdict[key] = val
        return retdict
        
    def ReturnGraffleArray(self, parent):
        """Graffle has arrays like
            <array>
                <string />
                <string />
            </array>
            - pass the <array> node to this method
        """
        retlist = []
        cont = nodeListGen(parent.childNodes)
        for e in cont:
            if e.nodeType == e.TEXT_NODE:
                continue
            retlist.append(self.ReturnGraffleNode(e))
        return retlist
        
        
    def extractMagnetCoordinates(self,mgnts):
        pts = [parseCoords(a) for a in mgnts]
        return pts
        
    def extractBoundCOordinates(self,bnds):
        bnds = bnds[1:-1].strip()
        bnds = bnds.split(",")
        coords = []
        for bnd in bnds:
            bnd = bnd.replace("{","")
            bnd = bnd.replace("}","")
            coords.append(float(bnd))

        return coords

                
    def svgItterateGraffleGraphics(self,GraphicsList):
        """parent should be a list of """
        for graphics in GraphicsList:
            # Styling
            self.style.appendScope()
            if graphics.get("Style") is not None:
                self.svgSetGraffleStyle(graphics.get("Style"))
            
            cls = graphics["Class"]
            if cls == "SolidGraphic":
                # used as background - add a 
                shallowcopy = {"Shape":"Rectangle"}
                shallowcopy.update(graphics)
                self.svgAddGraffleShapedGraphic(shallowcopy)
            elif cls == "ShapedGraphic":
                try:
                    self.svgAddGraffleShapedGraphic(graphics)
                except:
                    raise
                    print "could not show shaped graphic"
                
            elif cls == "LineGraphic":
                pts = self.extractMagnetCoordinates(graphics["Points"])
                self.svg_addPath(self.svg_current_layer, pts)
            else:
                print "Don't know how to display Class \"%s\""%cls
                
            if graphics.get("Text") is not None:
                # have to write some text too ...
                coords = self.extractBoundCOordinates(graphics['Bounds'])
                self.svgSetGraffleFont(graphics.get("FontInfo"))
                
                x, y, width, height = coords
                self.svg_addText(self.svg_current_layer, rtftext = graphics.get("Text").get("Text",""),
                                 x = x, y = y, width = width, height = height)
            self.style.popScope()
            
            
    def svgAddGraffleShapedGraphic(self, graphic):
        shape = graphic['Shape']
        
        extra_opts = {}
        if graphic.get("HFlip","NO")=="YES":
            extra_opts["HFlip"] = True
        if graphic.get("VFlip","NO")=="YES":
            extra_opts["VFlip"] = True
        if graphic.get("Rotation") is not None:
            extra_opts["Rotation"] = float(graphic["Rotation"])
            
        if shape == 'Rectangle':
            coords = self.extractBoundCOordinates(graphic['Bounds'])
            if graphic.get("ImageID") is not None:
                # TODO: images
                image_id = graphic["ImageID"]
                image = self.imagelist[image_id]
                self.svg_addImage(self.svg_current_layer, bounds = coords, \
                                  href = image)
                print "Insert Image - " + str(image)
            else:
                # radius of corners is stored on the style in graffle
                sty = graphic.get("Style",{})
                stroke = sty.get("stroke",{})
                radius = stroke.get("CornerRadius",None)
                
                x, y   = coords[0], coords[1]
                width  = coords[2]# - coords[0]
                height = coords[3]# - coords[1]
                self.svg_addRect(self.svg_current_layer,
                                        x = x,
                                        y = y,
                                        width = width,
                                        height = height,
                                        rx=radius,
                                        ry=radius,
                                        **extra_opts)

        elif shape == "HorizontalTriangle":
            bounds = self.extractBoundCOordinates(graphic['Bounds'])
            self.svg_addHorizontalTriangle(self.svg_current_layer,
                                        bounds = bounds,
                                        **extra_opts \
                                        )
        elif shape == "RightTriangle":
            bounds = self.extractBoundCOordinates(graphic['Bounds'])
            self.svg_addRightTriangle(self.svg_current_layer,
                                        bounds = bounds,
                                        **extra_opts \
                                        )
        elif shape == "Circle":
            # Actually can be an ellipse
            bounds = self.extractBoundCOordinates(graphic["Bounds"])
            self.svg_addEllipse(self.svg_current_layer,
                                        bounds = bounds,
                                        **extra_opts \
                                        )
        else:
            print "Don't know how to display Shape %s"%str(graphic['Shape'])
            
    def extract_colour(self,col):
        # only gets rgb values (ignores a)
        return "".join( [mkHex(col["r"]), 
                        mkHex(col["g"]), 
                        mkHex(col["b"])] )
            
    def svgSetGraffleStyle(self, style):
        style_string = ""
        styles_list = []
        
        if style.get("fill") is not None:
            fill = style.get("fill")
            if fill.get("Draws","") == "NO":
                # don't display
                self.style["fill"]="none"
            else:
                grap_col = fill.get("Color")
                if grap_col is not None:
                    fill_col = self.extract_colour(grap_col)
                    self.style["fill"]="#%s"%fill_col
                
        if style.get("stroke") is not None:
            stroke = style.get("stroke")
            if stroke.get("Draws","") == "NO":
                self.style["stroke"]="none"
            else:
            
                grap_col = stroke.get("Color",{"r":0.,"g":0.,"b":0.})
                if grap_col is not None:
                    stroke_col = self.extract_colour(grap_col)
                    self.style["stroke"]="#%s"%stroke_col
            if stroke.get("HeadArrow") is not None:
                headarrow = stroke["HeadArrow"]
                if headarrow == "FilledArrow":
                    self.style["marker-end"]=":url(#Arrow1Lend)"
                    self.required_defs.add("Arrow1Lend")
                elif headarrow == "0":
                    self.style["marker-end"] = "none"
                    
            if stroke.get("TailArrow") is not None:
                tailarrow = stroke["TailArrow"]
                if tailarrow == "FilledArrow":
                    self.style["marker-start"]="url(#Arrow1Lend)"
                    self.required_defs.add("Arrow1Lend")
                elif tailarrow == "0":
                    self.style["marker-start"]="none"
            if stroke.get("Width") is not None:
                width = stroke["Width"]
                self.style["stroke-width"]="%fpx"%float(width)
            
        if style.get("shadow",{}).get("Draws","") != "NO":
            # for some reason graffle has a shadow by default
            self.required_defs.add("DropShadow")
            self.style["filter"]="url(#DropShadow)"
            
    def svgSetGraffleFont(self, font):
        if font is None: return
        fontstuffs = []

        if font.get("Color") is not None:
            grap_col = font.get("Color")
            try:
                font_col = self.extract_colour(grap_col)
            except:
                font_col = "000000"
            fontstuffs.append("fill:#%s"%font_col)
            
        fontfam = font.get("Font")
        if fontfam is not None:
            fontstuffs.append("font-family: %s"%fontfam)
            
        size = font.get("Size")
        if size is not None:
            fontstuffs.append("font-size:%dpt"%int(size) )
        
        self.svg_current_font = ";".join(fontstuffs)
        
        
    def svg_add_requirements(self):
        if "Arrow1Lend" in self.required_defs:
            # TODO
            p = xml.dom.minidom.parseString("""
            <defs><marker
               orient="auto"
               refY="0.0"
               refX="0.0"
               id="Arrow1Lend"
               style="overflow:visible;">
              <path
                 id="path3666"
                 d="M 0.0,0.0 L 5.0,-5.0 L -12.5,0.0 L 5.0,5.0 L 0.0,0.0 z "
                 style="fill-rule:evenodd;stroke:#000000;stroke-width:1.0pt;marker-start:none;"
                 transform="scale(0.8) rotate(180) translate(12.5,0)" />
            </marker></defs>""")
            def_node = p.childNodes[0]
            for node in def_node.childNodes:
                self.svg_def.appendChild(node)
                
        if "Arrow1Lstart" in self.required_defs:
            p = xml.dom.minidom.parseString("""
            <defs><marker
               orient="auto"
               refY="0.0"
               refX="0.0"
               id="Arrow1Lstart"
               style="overflow:visible">
              <path
                 id="path3663"
                 d="M 0.0,0.0 L 5.0,-5.0 L -12.5,0.0 L 5.0,5.0 L 0.0,0.0 z "
                 style="fill-rule:evenodd;stroke:#000000;stroke-width:1.0pt;marker-start:none"
                 transform="scale(0.8) translate(12.5,0)" />
            </marker></defs>""")
            def_node = p.childNodes[0]
            for node in def_node.childNodes:
                self.svg_def.appendChild(node)
                
        if "DropShadow" in self.required_defs:
            p = xml.dom.minidom.parseString("""
            <defs><filter id="DropShadow" filterRes="100" x="0" y="0">
               <feGaussianBlur stdDeviation="3" result="myblur"/>
               <feOffset in="MyBlur" dx="2" dy="4" result="movedBlur"/>
               <feMerge>
                   <feMergeNode in="movedBlur"/>
                   <feMergeNode in="SourceGraphic"/>
               </feMerge>
          </filter></defs>""")
            def_node = p.childNodes[0]
            for node in def_node.childNodes:
                self.svg_def.appendChild(node)

    def svg_addEllipse(self, node, bounds, **opts):
        c = [bounds[i] + (bounds[i+2]/2.) for i in [0,1]] # centre of circle
        rx = bounds[2]/2.
        ry = bounds[3]/2.
        circle_tag = self.svg_dom.createElement("ellipse")
        circle_tag.setAttribute("id", opts.get("id",""))
        circle_tag.setAttribute("style", str(self.style.scopeStyle()))
        circle_tag.setAttribute("cx", str(c[0]))
        circle_tag.setAttribute("cy", str(c[1]))
        circle_tag.setAttribute("rx", str(rx))
        circle_tag.setAttribute("ry", str(ry))
        node.appendChild(circle_tag)

                             
    def svg_addPath(self, node, pts, **opts):
        # do geometry mapping here
        mypts = pts
        if opts.get("HFlip",False):
            mypts = geom.h_flip_points(mypts)
        if opts.get("VFlip",False):            
            mypts = geom.v_flip_points(mypts)
        if opts.get("Rotation") is not None:
            mypts = geom.rotate_points(mypts,opts["Rotation"])
            
        ptStrings = [",".join([str(b) for b in a]) for a in mypts]
        line_string = "M %s"%ptStrings[0] + " ".join(" L %s"%a for a in ptStrings[1:] )
        if opts.get("closepath",False) == True:
            line_string = line_string + " z"
        path_tag = self.svg_dom.createElement("path")
        path_tag.setAttribute("id", opts.get("id",""))
        path_tag.setAttribute("style", str(self.style.scopeStyle()))
        path_tag.setAttribute("d", line_string)
        node.appendChild(path_tag)
        
    def svg_addHorizontalTriangle(self, node, bounds, rotation = 0, **opts):
        """Graffle has the "HorizontalTriangle" Shape"""
        x,y,width,height = [float(a) for a in bounds]
        self.svg_addPath(node, [[x,y],[x+width,y+height/2], [x,y+height]], \
                        closepath=True, **opts)
                        
    def svg_addImage(self, node, bounds, **opts):
        """SVG viewers should support images - unfortunately many don't :-("""
        x,y,width,height = [float(a) for a in bounds]
        image_tag = self.svg_dom.createElement("image")
        image_tag.setAttribute("x", str(x))
        image_tag.setAttribute("y", str(y))
        image_tag.setAttribute("width", str(width))
        image_tag.setAttribute("height", str(height))
        image_tag.setAttribute("xlink:href", str(opts.get("href","")))
        image_tag.setAttribute("style", str(self.style.scopeStyle()))
        node.appendChild(image_tag)
        
    def svg_addRightTriangle(self, node, bounds, rotation = 0, **opts):
        """Graffle has the "RightTriangle" Shape"""
        x,y,width,height = [float(a) for a in bounds]
        self.svg_addPath(node, [[x,y],[x+width,y+height], [x,y+height]], \
                        closepath=True, **opts)
            
    def svg_addRect(self, node, **opts):
        """Add an svg rect"""
        if opts is None:
            opts = {}
        rect_tag = self.svg_dom.createElement("rect")
        rect_tag.setAttribute("id",opts.get("id",""))
        rect_tag.setAttribute("width",str(opts["width"]))
        rect_tag.setAttribute("height",str(opts["height"]))
        rect_tag.setAttribute("x",str(opts.get("x","0")))
        rect_tag.setAttribute("y",str(opts.get("y","0")))
        if opts.get("rx") is not None:
            rect_tag.setAttribute("rx",str(opts["rx"]))
            rect_tag.setAttribute("ry",str(opts["ry"]))
            
        rect_tag.setAttribute("style", str(self.style.scopeStyle()))
        node.appendChild(rect_tag)
        
        
    def svg_addText(self,node,**opts):
        """Add an svg text element"""
        text_tag = self.svg_dom.createElement("text")
        text_tag.setAttribute("id",opts.get("id",""))
        text_tag.setAttribute("x",str(opts.get("x","0")))
        text_tag.setAttribute("y",str(opts.get("y","0")))
        text_tag.setAttribute("style", ";".join( \
                                [str(self.style.scopeStyle()),self.svg_current_font]))
        node.appendChild(text_tag)
        
        # TODO: lines need to be moved down by the correct size
        
        # Generator
        lines = extractRTFString(opts["rtftext"])
        
        i = 0
        for span in lines:
            self.svg_addLine(text_tag,text = span["string"], style = span["style"],\
                    y_offset = i, line_height = 12, **opts)
            i+=1
        
    def svg_addLine(self,textnode, **opts):
        """Add a line of text"""
        tspan_node = self.svg_dom.createElement("tspan")
        tspan_node.setAttribute("id",opts.get("id",""))
        tspan_node.setAttribute("x",str(opts.get("x","0")))
        y_pos = float(opts.get("y",0)) + \
                opts.get("line_height",12) * (opts.get("y_offset",0)+1)
        if opts.get("style") is not None:
            tspan_node.setAttribute("style",str(opts["style"]))
        tspan_node.setAttribute("y",str(y_pos))
        actual_string = self.svg_dom.createTextNode(opts.get("text"," "))
        tspan_node.appendChild(actual_string)
        textnode.appendChild(tspan_node)

