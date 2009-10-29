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


class FileInfo(object):
    """Stores information about the version of a graffle document"""
    def __init__(self, gdict):
        """Grab all file info from this dict"""
        self.fmt_version = int(gdict.get("GraphDocumentVersion",-1))
        self.creator = gdict.get("Creator","")
        self.creationdate = gdict.get("CreationDate","")
        self.app_version = gdict.get("ApplicationVersion",[])
        self.modified = gdict.get("ModificationDate","")
        self.printinfo = PrintInfo(gdict.get("PrintInfo",{}))
        

class PrintInfo(object):
    """Gets the Print information from the file's dict
       - possible confusion over the formatting, so store separately."""
    def __init__(self, pinfo):
        self._print_info = pinfo
       
    bottom_margin = property(fget = lambda x: x.extract_value("NSBottomMargin",0))
    left_margin = property(fget = lambda x: x.extract_value("NSLeftMargin",0))
    right_margin = property(fget = lambda x: x.extract_value("NSRightMargin",0))
    top_margin = property(fget = lambda x: x.extract_value("NSTopMargin",0))
    orientation = property(fget = lambda x: x.extract_value("NSOrientation",1))
    paper_name = property(fget = lambda x: x.extract_value("NSPaperName",""))
    paper_size = property(fget = lambda x: x.extract_value("NSPaperSize",[100,100]))
        
    def extract_value(self, key, default):
        """input format is similar to:
        {key:[type, value]}
        """
        somelist = self._print_info.get(key)
        if somelist is None:
            return default
        typ = somelist[0]
        if typ == "int":
            return int(somelist[1])
        elif typ == "size":
            # e.g. {12,32}
            valueparts = somelist[1][1:-1].split(",")
            return [float(a) for a in valueparts]
        elif typ == "coded":
            pass
            #raise NotImplementedError("'Coded' type not implemented")
        return default
