import os
import struct

class HuffmanNode:      
	frequency = 0
	byte = None
	left = None
	right = None
	parent = None
	
	def __init__( self ):
                self.frequency = 0
                self.byte = None
                self.left = None
                self.right = None
                self.parent = None

	def __init__( self, byte, frequency, left, right, parent ):
                self.frequency = frequency
                self.byte = byte
                self.left = left
                self.right = right
                self.parent = parent


        def isLeaf( self ):
                return self.left == None and self.right == None

huffmanNodeCompare = lambda x, y : x.frequency - y.frequency # sort from less frequent to most frequent

class Huffman:
        BUFFER_SIZE = 4096
	frequencyTable = {}
	byteToLeafNodeTable = {}
	

	def __init__(self):
                self.frequencyTable = {}
                self.byteToLeafNodeTable = {}


        #
        # Build frequency table
        #
        def _buildFrequencyTable( self, file ):
                bytes = file.read( self.BUFFER_SIZE )
		while bytes != "":
                        for b in bytes:
                                if self.frequencyTable.has_key( b ):
                                        self.frequencyTable[ b ] += 1
                                else:
                                        self.frequencyTable[ b ] = 1
                        bytes = file.read( self.BUFFER_SIZE )       

        #
        # Build a huffman tree.
        #
        def _buildTree( self ):
                assert len( self.frequencyTable ) > 0 # ensure we have built a frequecy table

                nodes = []
                for byte in self.frequencyTable.keys( ):
                        leafNode = HuffmanNode( byte, self.frequencyTable[ byte ], None, None, None )
                        nodes.append( leafNode )
                        self.byteToLeafNodeTable[ byte ] = leafNode # we need this data structure later...
				
                nodes.sort( huffmanNodeCompare )

                while len(nodes) > 1:
                        h1 = nodes.pop( 0 )
                        h2 = nodes.pop( 0 )
                        h = HuffmanNode(None, h1.frequency + h2.frequency, h1, h2, None ) # h1 < h2                        
                        h1.parent = h
                        h2.parent = h # assign the parent to the leaf nodes
                        nodes.append( h )
                        nodes.sort( huffmanNodeCompare )

                return nodes[ 0 ] # this is the root
	
	
        #
        # Save the frequency table to a file
        #
        def _saveFrequencyTable( self, file ):
                assert len( self.frequencyTable ) > 0 # ensure we have built a frequecy table

                file.write( struct.pack( "<I", len( self.frequencyTable ) ) ) # save the table's size
                
                for byte in self.frequencyTable.keys( ): # save the table now
                        file.write( byte )
                        file.write( struct.pack( "<I", self.frequencyTable[ byte ] ) )


        #
        # Load the frequency from a file
        #
        def _loadFrequencyTable( self, file ):                
                frequencyTableSize = struct.unpack( "<I", file.read( 4 ) )[ 0 ] # load the table's size, 32-bit int

                
                while frequencyTableSize > 0:
                        theByte = file.read( 1 )
                        theFrequency = struct.unpack( "<I", file.read( 4 ) )[ 0 ]
                        self.frequencyTable[ theByte ] = theFrequency
                        frequencyTableSize -= 1
                #print self.frequencyTable


        #
        # Huffman encode a file.
        #
	def encode( self, filename, encodedFilename ):
        	originalFile = open( filename, 'rb' )
        	encodedFile = open( encodedFilename, 'wb' )

		
		self._buildFrequencyTable( originalFile )
		
		# return to beginning of file to start encoding
		originalFile.seek( 0, os.SEEK_SET )
		

                # build a huffman tree from the frequency table
                root = self._buildTree( )

                # save the frequency table to disk
                self._saveFrequencyTable( encodedFile )

                # lets encode...
                #'''
		bytes = originalFile.read( self.BUFFER_SIZE )
                bitString = 0x00
                i = 0

		while len( bytes ) > 0:
                        for b in bytes:
                                # bof build bit string
                                h = self.byteToLeafNodeTable[ b ]

                                # use a stack to reverse the bits
                                bitStringStack = []
                                while h.parent != None:
                                        if h.parent.right == h:
                                                bitStringStack.append( 1 )
                                        else:
                                                bitStringStack.append( 0 )
                                        h = h.parent
                                
                                while len( bitStringStack ) > 0:
                                        bit = bitStringStack.pop( )
                                        if bit == 1:
                                                bitString |= ( 1 << (7 - i) )
                                        i += 1

                                        # If we exceed a byte we need to write this byte to disk
                                        # and reset our counter and bitstring.
                                        if i > 7: # if we exceed a byte, dump the byte and reset
                                                encodedFile.write( chr( bitString ) )
                                                #print "         BYTE: 0x%(bits)02X" % { "bits" : bitString }
                                                bitString = 0x00
                                                i = 0
                                                
                                # eof build bit string
                                




                        bytes = originalFile.read( self.BUFFER_SIZE )

                if i > 0 and i < 8:
                        encodedFile.write( chr( bitString ) )
                        #print "LEFTOVER BYTE: 0x%(bits)02X" % { "bits" : bitString }
                        bitString = 0x00
                        i = 0
		
		#'''
		originalFile.close( )
		encodedFile.close( )

                
        #
        # Huffman decode a file.
        #
	def decode( self, encodedfilename, filename ):
        	originalFile = open( encodedfilename, 'rb' )
        	decodedFile = open( filename, 'wb' )

        	# load the frequency table from disk
                self._loadFrequencyTable( originalFile )
                
                # build a huffman tree from the frequency table
                root = self._buildTree( )

                # lets decode...
		bytes = originalFile.read( self.BUFFER_SIZE )

                h = root
                
		while len( bytes ) > 0:
                        for b in bytes:
                                bitString = ord( b )
                                i = 0
                                while i < 8:
                                        if i > 7:
                                                break
                                        # bof translate bit string to byte
                                        if not h.isLeaf( ): # loop until we find a leaf node                                                        
                                                if (bitString & ( 1 << (7 - i) )) > 0: # is bit set?
                                                        h = h.right
                                                else:
                                                        h = h.left
                                                i += 1
                                        else:       
                                                decodedFile.write( h.byte )
                                                #print "DEBUG: " + h.byte
                                                h = root
                                        
                                        
                        bytes = originalFile.read( self.BUFFER_SIZE )

                        
                                                
		
                
        	originalFile.close( )
        	decodedFile.close( )
