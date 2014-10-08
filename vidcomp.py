#!/usr/bin/env python

import argparse, os, subprocess
from subprocess import call
import xml.etree.ElementTree as ET


parser = argparse.ArgumentParser(description="Python tool for comparing the output of video characterization tools")
parser.add_argument('-i', '--input', type=str, required=True, help='The full path to the file you want to analyze.')
args = parser.parse_args()


def probe_file(filename):
    cmnd = ['ffprobe', '-show_format', '-show_streams', '-show_error', '-show_versions', '-print_format', 'xml', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    root = ET.fromstring(out)

    # ===============
    # FFPROBE attributes
    ffprobe_format = ['format_name', 'format_long_name', 'size', 'duration', 'bit_rate']
    ffprobe_video_track = ['codec_name', 'codec_tag_string', 'profile', 'display_aspect_ratio', 'r_frame_rate', 'pix_fmt']
    ffprobe_audio_track = ['codec_name', 'codec_tag_string', 'sample_rate', 'bits_per_sample', 'channels']

    for elem in root.iterfind('format'):
    	for item in ffprobe_format:
    		print item + ": " + elem.attrib[item]

    for stream in root.iter('stream'):
    	if stream.attrib['codec_type'] == "video":
	    	for item in ffprobe_video_track:
	    		print item + ": " + stream.attrib[item]

probe_file(args.input)