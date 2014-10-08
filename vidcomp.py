#!/usr/bin/env python

import argparse, os, subprocess
from subprocess import call
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description="Python tool for comparing the output of video characterization tools")
parser.add_argument('-i', '--input', type=str, required=True, help='The full path to the file you want to analyze.')
parser.add_argument('-o', '--output', type=str, required=True, help='where to put csv report')
args = parser.parse_args()

csv_path = args.output
c = csv.writer(open(csv_path, "wb"))
c.writerow(["","FFPROBE","Mediainfo","Exiftool"])

# ===============
# FFPROBE attributes
ffprobe_format = {'format_long_name':None, 'size':None, 'duration':None, 'bit_rate':None}
ffprobe_video_track = {'codec_name':None, 'codec_tag_string':None, 'profile':None, 'display_aspect_ratio':None, 'r_frame_rate':None, 'pix_fmt':None}
ffprobe_audio_track = {'codec_name':None, 'codec_tag_string':None, 'sample_rate':None, 'bits_per_sample':None, 'channels':None}

# ===============
# EXIFTOOL attributes
'''
exiftool_format = {'File:FileType':None,'System:FileSize':None,' ??????? Duration':None, 'Composite:AvgBitrate':None}
exiftool_video_track = {'?????? CompressorName':None, '?????? BitDepth':None, }
exiftool_audio_track = {'Track ????? :AudioFormat':None,'Track ????? :AudioSampleRate':None,'Track ???? :AudioBitsPerSample':None, 'Track ???? :AudioChannels':None }

def exif_file(filename):
    cmnd = ['exiftool', '-X', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    root = ET.fromstring(out)
    # exif namesapces
    ET.register_namespace("File", "http://ns.exiftool.ca/File/1.0/")

    for neighbor in root.iter('FileType'):
        print "qsdf"

exif_file(args.input)
'''

def probe_file(filename):
    cmnd = ['ffprobe', '-show_format', '-show_streams', '-show_error', '-show_versions', '-print_format', 'xml', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    root = ET.fromstring(out)

    for elem in root.iterfind('format'):
        for item in ffprobe_format:
            ffprobe_format[item] = elem.attrib[item]

    for stream in root.iter('stream'):
    	if stream.attrib['codec_type'] == "video":
            for item in ffprobe_video_track:
                ffprobe_video_track[item] = stream.attrib[item]

        elif stream.attrib['codec_type'] == "audio":
            for item in ffprobe_audio_track:
                ffprobe_audio_track[item] = stream.attrib[item]

def mediainfo_file(filename):
    cmnd = ['mediainfo', '-f', '--language=raw', '--Output=XML', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    root = ET.fromstring(out)

    # ===============
    # Mediainfo attributes
    mediainfo_format = ['format_name', 'format_long_name', 'size', 'duration', 'bit_rate']
    mediainfo_video_track = ['codec_name', 'codec_tag_string', 'profile', 'display_aspect_ratio', 'r_frame_rate', 'pix_fmt']
    mediainfo_audio_track = ['codec_name', 'codec_tag_string', 'sample_rate', 'bits_per_sample', 'channels']

    for elem in root.iterfind('format'):
    	for item in ffprobe_format:
    		print item + ": " + elem.attrib[item]

print "---------------------------------------"
print "FFPROBE output"
probe_file(args.input)
print "---------------------------------------"
mediainfo_file(args.input)

print "container",ffprobe_format
print "video",ffprobe_video_track
print "audio",ffprobe_audio_track




