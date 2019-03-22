#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Receive RTMP and stream over SRT
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Receive RTMP and stream over SRT')
parser.add_argument('inputstream')
parser.add_argument('outputaddress')
parser.add_argument('--inputtype', default='rtmp', help='type of input [rtmp|mpegts], default is rtmp')
parser.add_argument('--listener', action='store_true', help='run as SRT listener')
parser.add_argument('--passthrough', action='store_true', help='passthrough input and skip encoding process')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

listenermode = ''
if args.listener:
  listenermode = '&mode=listener'

outputcoding = '-acodec copy -vcodec libx264 -preset veryfast -pix_fmt yuv420p'
if args.passthrough:
  outputcoding = '-acodec copy -vcodec copy'

inp = 'rtmp://0.0.0.0/live/%s' % args.inputstream
if args.inputtype == 'mpegts':
  inp = 'udp://%s?pkt_size=1316' % args.inputstream

ffmpeg = "ffmpeg -fflags +genpts -listen 1 -re -i %s %s -strict -2 -y -f mpegts srt://%s?pkt_size=1316%s" % (inp, outputcoding, args.outputaddress, listenermode)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()