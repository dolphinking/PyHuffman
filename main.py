import huffman
import sys


def main( ):
    if len( sys.argv ) < 2:
        print "Usage:"
        print sys.argv[ 0 ] + " <filename>"


    if len( sys.argv ) > 1:
        filename = sys.argv[ 1 ]
    else: # lets hard code a case for testing...
        filename = "test.txt" # for debug...

    print "Compressing " + filename + "..."

    huff = huffman.Huffman( )
    huff.encode( filename, filename + ".out" )


    print "Decompressing " + filename + ".out..."
    huff.decode( filename + ".out", filename + ".org"  )
    
    

main( )
