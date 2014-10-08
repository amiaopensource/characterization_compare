#!/usr/bin/env python

import argparse, os

'''
todo

- outputs XML for each tool
- use xpath to identify each value

argumenet for file

'''

parser = argparse.ArgumentParser(description="Python tool for comparing the output of video characterization tools")
parser.add_argument('-i', '--input', type=str, required=True, help='The full path to the file you want to analyze.')
args = parser.parse_args()

# function that runs mediainfo, exif, ffprobe

