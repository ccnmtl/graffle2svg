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

import gzip


class GraffleFilePack(object):
    __file = None
    
    def __init__(self,fn):
        if self.detectXMLFile(fn):
            self.__file = open(fn,"r")
        elif self.detectGZipXMLFile(fn):
            self.__file = gzip.open(fn, "rb")
            
    def read(self):
        return self.__file.read()
        
    def close(self):
        self.__file.close()
    
    def detectGZipXMLFile(self,fn):
        f = gzip.open(fn, 'rb')
        return self.detectXML(f.readline())
        
    def detectXMLFile(self,fn):
        """Is this an xml file"""
        f = open(fn,"r")
        start = f.readline()
        xml = self.detectXML(start)
        f.close()
        return xml
        
    def detectXML(self,start):
        """just look for standard part in first line"""
        if start[:5] == "<?xml":
            return True
        return False
        
        
if __name__ == "__main__":
    gfp = GraffleFilePack("gziptest.graffle")
    print gfp.read()
    
