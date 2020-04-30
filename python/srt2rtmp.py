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

parser = argparse.ArgumentParser(description='Receive SRT and restream to multiple RTMP destinations')
parser.add_argument('inputaddress')
parser.add_argument('output', nargs="+")
parser.add_argument('--with-debug', dest='debug', action='store_true')
args = parser.parse_args()

ffmpeg = "ffmpeg -re -i srt://%s?pkt_size=1316&mode=listener -strict -2 -y " % (args.inputaddress)

for dest in args.output:
  ffmpeg = ffmpeg + "-f fifo -fifo_format flv -map 0:0 -map 0:1 -c copy -vtag 7 -atag 10 -drop_pkts_on_overflow 1 -attempt_recovery 1 -recovery_wait_time 1 %s " % (dest)

if args.debug:
  print "%s" % ffmpeg
  print ffmpeg.split()

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()