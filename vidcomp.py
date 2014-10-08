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
    # print out
    root = ET.fromstring(out)
    # print root
    # print root.tag
    # print root.attrib
    print root.iter
    # for child in root:
    # 	print child.tag, child.attrib


'''
list of children

ffprobe: //format[@format_name]
ffprobe: //format[@format_long_name]
ffprobe: //format[@size]
ffprobe: //format[@duration]
ffprobe: //format[@bit_rate]


'''

probe_file(args.input)