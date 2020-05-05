#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Receive HLS and stream over SRT
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Pull HLS and restream over SRT.')
parser.add_argument('hlsurl')
parser.add_argument('address')
parser.add_argument('--srtmode', dest='srtmode', help='SRT mode [caller|listener]. Default is listener')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

srtmode = "&mode=listener"
if args.srtmode == "caller":
  srtmode = ""

srtoutput = "-f fifo -fifo_format mpegts -map 0:v:0 -map 0:a:0 -c copy srt://%s?pkt_size=1316%s" % (args.address, srtmode)

ffmpeg = "ffmpeg -fflags +genpts -re -i %s -strict -2 -y %s " % (args.hlsurl, srtoutput)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()
