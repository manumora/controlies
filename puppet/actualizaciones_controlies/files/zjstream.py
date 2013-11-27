
# -*- coding: ISO-8859-15 -*-
#
# pkpgcounter : a generic Page Description Language parser
#
# (c) 2003, 2004, 2005, 2006, 2007 Jerome Alet <alet@librelogiciel.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id: zjstream.py 374 2007-12-09 14:26:15Z jerome $
#

"""This modules implements a page counter for ZjStream documents."""

import struct

import pdlparser

class Parser(pdlparser.PDLParser) :
    """A parser for ZjStream documents."""
    def isValid(self) :    
        """Returns True if data is ZjStream, else False."""
        if self.firstblock[:4] == "ZJZJ" :
            self.format = "Zenographics ZjStream (little endian)"
            return self.littleEndian()
        elif self.firstblock[:4] == "JZJZ" :    
            self.format = "Zenographics ZjStream (big endian)"
            return self.bigEndian()
        elif (self.firstblock.find("\033%-12345XZJZJ") != -1) :
            self.format = "Zenographics ZjStream (little endian)"
            return self.littleEndian()
        elif (self.firstblock.find("\033%-12345XJZJZ") != -1) :
            self.format = "Zenographics ZjStream (big endian)"
            return self.bigEndian()
        else :    
            return False
        
    def littleEndian(self) :
        """Toggles to little endianness."""
        self.unpackHeader = "<IIIHH"
        return True
        
    def bigEndian(self) :
        """Toggles to big endianness."""
        self.unpackHeader = ">IIIHH"
        return True
        
    def getJobSize(self) :
        """Computes the number of pages in a ZjStream document."""
        poslittle=self.firstblock.find("\033%-12345XZJZJ")
        posbig=self.firstblock.find("\033%-12345XJZJZ")
        if posbig==-1 and poslittle==-1 :
             self.infile.seek(4, 0) # Skip ZJZJ/JZJZ header
        elif posbig==-1 :			
			 self.infile.seek(poslittle+13, 0) # Skip little endian header with PJL 
        else: 	 
             self.infile.seek(posbig+13, 0) # Skip big endian header with PJL 
		     
        startpagecount = endpagecount = 0
        unpackHeader = self.unpackHeader
        unpack = struct.unpack
        try :
            while True :
                header = self.infile.read(16)
                if not header :
                    break
                (totalChunkSize,
                 chunkType,
                 numberOfItems,
                 reserved,
                 signature) = unpack(unpackHeader, header)
                self.infile.seek(totalChunkSize - len(header), 1)
                if chunkType == 2 :    
                    #self.logdebug("startPage")
                    startpagecount += 1
                elif chunkType == 3 :
                    #self.logdebug("endPage")
                    endpagecount += 1
                #elif chunkType == 0 :
                #    self.logdebug("startDoc")
                #elif chunkType == 1 :    
                #    self.logdebug("endDoc")
                #    
                #self.logdebug("Chunk size : %s" % totalChunkSize)
                #self.logdebug("Chunk type : 0x%08x" % chunkType)
                #self.logdebug("# items : %s" % numberOfItems)
                #self.logdebug("reserved : 0x%04x" % reserved)
                #self.logdebug("signature : 0x%04x" % signature)
                #self.logdebug("\n")
        except struct.error :
            raise pdlparser.PDLParserError, "This file doesn't seem to be valid ZjStream datas."
            
        # Number of endpage commands should be sufficient,
        # but we never know : someone could try to cheat the printer
        # by starting a page but not ending it, and ejecting it manually
        # later on. Not sure if the printers would support this, but
        # taking the max value works around the problem in any case.
        self.logdebug("StartPage : %i    EndPage : %i" % (startpagecount, endpagecount))
        return max(startpagecount, endpagecount)
