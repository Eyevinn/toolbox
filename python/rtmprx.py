#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Receive RTMP and restream over Multicast
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Receive RTMP and restream over Multicast')
parser.add_argument('inputstream')
parser.add_argument('outputaddress')
parser.add_argument('--passthrough', action='store_true', help='passthrough input and skip encoding process')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

outputcoding = '-acodec copy -vcodec libx264 -preset veryfast -pix_fmt yuv420p'
if args.passthrough:
  outputcoding = '-acodec copy -vcodec copy'

ffmpeg = "ffmpeg -fflags +genpts -listen 1 -re -i rtmp://0.0.0.0/live/%s %s -strict -2 -y -f mpegts udp://%s?pkt_size=1316" % (args.inputstream, outputcoding, args.outputaddress)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()