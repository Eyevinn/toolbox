#!/usr/bin/python2.7
#
# Copyright 2019 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Receive SRT and restream to multiple RTMP destinations
#
import argparse
import subprocess
from os.path import basename
import re
import glob

parser = argparse.ArgumentParser(description='Pull HLS and restream to multiple RTMP destinations.')
parser.add_argument('hlsurl')
parser.add_argument('output', nargs="+")
parser.add_argument('--with-programreturn', dest='programreturn', action='store_true', help='open up an SRT program return')
parser.add_argument('--returnport', dest='returnport', help='port for the SRT program return')
parser.add_argument('--srtmode', dest='srtmode', help='SRT mode for program return. Default is listener')
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

returnport = "1234"
if args.returnport:
  returnport = args.returnport

srtmode = "&mode=listener"
if args.srtmode:
  srtmode = args.srtmode

srtoutput = ""
if args.programreturn:
  srtoutput = "-f fifo -fifo_format mpegts -map 0:v:0 -map 0:a:0 -c copy srt://0.0.0.0:%s?pkt_size=1316%s" % (returnport, srtmode)

ffmpeg = "ffmpeg -fflags +genpts -re -i %s -strict -2 -y %s " % (args.hlsurl, srtoutput)

for dest in args.output:
  ffmpeg = ffmpeg + "-f fifo -fifo_format flv -map 0:v:0 -map 0:a:0 -c:v copy -vtag 7 -c:a copy -atag 10 -drop_pkts_on_overflow 1 -attempt_recovery 1 -recovery_wait_time 1 %s " % (dest)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()
