#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Play multiple HLS sources and renders a mosaic in MPEG-TS 
#
import argparse
import subprocess
from os.path import basename
import re
import glob
import sys
parser = argparse.ArgumentParser(description='Take multiple HLS sources and render a mosaic in MPEG-TS')
parser.add_argument('layout', help='2x2|3x3')
parser.add_argument('urlfile', help='A text file containing URLs to HLS sources. One source per line.')
parser.add_argument('--port', default='9998')
parser.add_argument('--multicast', help='Use multicast address specified here instead of SRT')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

if args.urlfile == '-':
  sources = [x.strip() for x in sys.stdin.readlines()]
else:
  with open(args.urlfile, "r") as f:
    sources = [x.strip() for x in f.readlines()]

scalex = 384
scaley = 216
width = 2
height = 2

if args.layout == '3x3':
  width = 3
  height = 3

filter_complex = 'nullsrc=size=%dx%d [tmp0]; ' % (scalex * width, scaley * height)
for i in range(0, width*height):
  filter_complex += '[%d:v] scale=%dx%d [s%d]; ' % (i, scalex, scaley, i)
x = 0
y = 0
for i in range(0, width*height):
  if i < width*height - 1:
    filter_complex += '[tmp%d][s%d] overlay=shortest=1:x=%d:y=%d [tmp%d];' % (i, i, x, y, i + 1)
  else:
    filter_complex += '[tmp%d][s%d] overlay=shortest=1:x=%d:y=%d' % (i, i, x, y)
  if x >= (scalex * width) - scalex:
    y += scaley
    x = 0
  else:
    x += scalex

#print filter_complex
inputs = ''
for s in sources:
  inputs += '-i %s ' % s

output = '"srt://0.0.0.0:%s?pkt_size=1316&mode=listener"' % args.port
if args.multicast:
  output = 'udp://%s?pkt_size=1316' % args.multicast
ffmpeg = 'ffmpeg -threads 8 -re %s -filter_complex "%s" -c:v libx264 -an -strict -2 -f mpegts %s' % (inputs, filter_complex, output)

if args.debug:
  print "%s" % ffmpeg

p1 = subprocess.Popen(ffmpeg, shell=True)
output,err = p1.communicate()