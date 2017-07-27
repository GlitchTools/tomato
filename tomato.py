#!/bin/python2.7

import argparse
import re
import random
import struct
from itertools import chain

#################
### ARGUMENTS ###
#################

parser = argparse.ArgumentParser(add_help=True)
parser.add_argument("-i", "--input", help="input file")
parser.add_argument('-m', "--mode", action='store', dest='modevalue',help='choose mode')
parser.add_argument('-c', action='store', dest='countframes',help='var1', default=1)
parser.add_argument('-n', action='store', dest='positframes',help='var2', default=1)
parser.add_argument("file", help="input file")

args = parser.parse_args()

fileout = args.file
filein = args.input
mode = args.modevalue
countframes = args.countframes
positframes = args.positframes

####################
### OPENING FILE ###
####################


#open .avi file as binary stream first part in f2 and rest in idx

with open(filein,'rb') as f1:
	with open(fileout,'wb') as f2:
		while True:
			buffer = f1.read(1024)
			if buffer: 
				if buffer.find('idx1') == -1 : 
					for byte in buffer :
						f2.write(byte)
				elif buffer.find('idx1') != -1 :
					a = buffer.split('idx1', 1)
					f2.write(a[0])
					idx = a[1] + f1.read()
					break
			else :
				print('file has no index')
				break
	f2.close()

	a1 = idx

	## get the length of the index and store it
	a1, idxl = a1[4:], a1[:4]

	## get the first iframe and store it
	n = 16
	iframe, a1 = a1[:n], a1[n:] 
	
	## put all frames in array
	sframeregex = re.compile('.*wb.*')
	b = [a1[i:i+n] for i in range(0, len(a1), n) if not re.match(sframeregex,a1[i:i+n])] 
	
	## take out all of the sound frames cuz who gives a fuck
	#sframeregex = re.compile('.*wb.*')
	#b = [x for x in b if not re.match(sframeregex,x)]

	## calculate number of frames
	c = len(b)

#########################
### OPERATIONS TO IDX ###
#########################

	### MODE - SHUFFLE 
	#####################

	if mode == "shuffle":
		idx = random.sample(b,c)

	### MODE - DELETE IFRAMES
	###########################

	if mode == "ikill":
		iframeregex = re.compile(b'.*dc\x10.*')
		idx = [x for x in b if not re.match(iframeregex,x)]

	### MODE - BLOOM
	##################

	if mode == "bloom":
		## bloom options
		repeat = int(countframes)	
		frame = int(positframes)
	
		## split list
		lista = b[:frame]
		listb = b[frame:]

		## rejoin list with bloom
		idx = lista + ([b[frame]]*repeat) + listb

	### MODE - P PULSE
	##################
	
	if mode == "pulse":
		pulselen = int(countframes)
		pulseryt = int(positframes)
	
		idx = [[x for j in range(pulselen)] if not i%pulseryt else x for i,x in enumerate(b)]
		idx = [item for sublist in idx for item in sublist]
		idx = ''.join(idx)
		idx = [idx[i:i+n] for i in range(0, len(idx), n)] 
		
		
	### MODE - REVERSE
	##################
	
	##just having fun by adding this at the end of the bloom
	#d = random.sample(d,c + repeat)

########################
### FIX INDEX LENGTH ###
######################## 

	print "old index size : " + str(c + 1) + " frames"
	idxl = len(idx)*16
	print(idxl)
	print "new index size : " + str((idxl/16) + 1) + " frames"

	## convert it to packed data
	idxl = struct.pack('<I',idxl)

###################
### SAVING FILE ###
###################

	## rejoin the whole thing
	data = ''.join('idx1' + idxl + iframe + ''.join(idx)) 
	f2 = open(fileout, 'ab')
	f2.write(data)
	f2.close()
	
#	f3 = open('index.avi', 'wb')
#	f3.write(''.join(idx))
