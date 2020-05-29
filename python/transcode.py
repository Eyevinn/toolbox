#!/usr/bin/python2.7
#
# Copyright 2020 Eyevinn Technology. All rights reserved
# Use of this source code is governed by a MIT License
# that can be found in the LICENSE file.
# Author: Jonas Rydholm Birme (Eyevinn Technology)
#
# Transcode an MP4 to multiple ABR-aligned MP4 files that can be packaged in various streaming formats
#
import argparse
import subprocess
from os.path import basename
from os.path import splitext
import re
import glob

parser = argparse.ArgumentParser(description='Transcode an MP4 file to multiple ABR-aligned MP4 files (AVC/AAC)')
parser.add_argument('inputfile')
parser.add_argument('--outdir', default='./', help="directory for the generated files. Default is current working directory.")
parser.add_argument('--framerate', default=30, help="framerate of input file. Default to 30")

args = parser.parse_args()

ladder = [
  (426, 240, 320),
  (854, 480, 960),
  (1280, 720, 1725),
]

ffmpeg = "ffmpeg -y -i /media/%s " % args.inputfile
for p in ladder:
  outputfile = "/media/%s-%s.mp4" % (splitext(args.inputfile)[0], p[2])
  ffmpeg = ffmpeg + "-pix_fmt yuv420p -r %s -c:v libx264 -sc_threshold 0 -profile:v main -bf 1 -refs 3 -vf scale=w=%s:h=%s -b:v %sk -maxrate %sk -bufsize %sk -keyint_min %s -g %s -strict experimental -acodec aac -b:a 96k -f mp4 %s " % (args.framerate, p[0], p[1], p[2], p[2], p[2], args.framerate, (args.framerate * 2), outputfile)
print ffmpeg

p1 = subprocess.Popen(ffmpeg.split())
output,err = p1.communicate()
