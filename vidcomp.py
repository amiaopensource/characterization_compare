#!/usr/bin/env python

import argparse, os, subprocess, csv
from subprocess import call
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description="Python tool for comparing the output of video characterization tools")
parser.add_argument('-i', '--input', type=str, required=True, help='The full path to the file you want to analyze.')
parser.add_argument('-o', '--output', type=str, required=True, help='where to put csv report')
args = parser.parse_args()

csv_path = args.output
c = csv.writer(open(csv_path, "wb"))

# ===============
# FFPROBE attributes
ffprobe_format_master = []
ffprobe_video_track_master = []
ffprobe_audio_track_master = []
# ===============
# Mediainfo attributes
mediainfo_format_master = []
mediainfo_video_track_master = []
mediainfo_audio_track_master = []
mediainfo_version = []

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
        ffprobe_format = {'format_long_name':None, 'size':None, 'duration':None, 'bit_rate':None}
        for item in ffprobe_format:
            ffprobe_format[item] = elem.attrib[item]
        ffprobe_format_master.append(ffprobe_format)
    for stream in root.iter('stream'):
    	if stream.attrib['codec_type'] == "video":
            ffprobe_video_track = {'codec_name':None, 'codec_tag_string':None, 'profile':None, 'display_aspect_ratio':None, 'r_frame_rate':None, 'pix_fmt':None}
            for item in ffprobe_video_track:
                ffprobe_video_track[item] = stream.attrib[item]
            ffprobe_video_track_master.append(ffprobe_video_track)
        elif stream.attrib['codec_type'] == "audio":
            ffprobe_audio_track = {'codec_name':None, 'codec_tag_string':None, 'sample_rate':None, 'bits_per_sample':None, 'channels':None}
            for item in ffprobe_audio_track:
                ffprobe_audio_track[item] = stream.attrib[item]
            ffprobe_audio_track_master.append(ffprobe_audio_track)
            
# ===============
# Mediainfo Harvesting
def mediainfo_file(filename):
    cmnd = ['mediainfo', '-f', '--language=raw', '--Output=XML', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err =  p.communicate()
    root = ET.fromstring(out)

    mediainfo_version.append(root.attrib['version'])

    for file in root.iterfind('File'):
    	for track in file.iterfind('track'):
    	    if track.attrib['type'] == "General":
    	        mediainfo_format = {'Format':None, 'Format_Profile':None, 'FileSize':None, 'Duration_String':None, 'OverallBitRate_String':None}
    	        for item in mediainfo_format:
    	            try:
    	                mediainfo_format[item] = track.find(item).text
    	            except AttributeError:
    	                mediainfo_format[item] = "N/A"
    	        mediainfo_format_master.append(mediainfo_format)
    	    if track.attrib['type'] == "Video":
    	        mediainfo_video_track = {'Format':None, 'CodecID':None, 'Format_Profile':None, 'DisplayAspectRatio':None, 'FrameRate':None, 'ChromaSubsampling':None, 'Resolution':None, 'ColorSpace':None}
    	        for item in mediainfo_video_track:
    	            try:
    	                mediainfo_video_track[item] = track.find(item).text
    	            except AttributeError:
    	                 mediainfo_video_track[item] = "N/A"
    	        mediainfo_video_track_master.append(mediainfo_video_track)
    	    if track.attrib['type'] == "Audio":
    	        mediainfo_audio_track = {'Format':None, 'CodecID':None, 'Format_Profile':None, 'SamplingRate':None, 'AudioBitsPerSample':None, 'Channel_s_':None,'StreamKindPos':None}
    	        for item in mediainfo_audio_track:
    	            try:
    	                 mediainfo_audio_track[item] = track.find(item).text
    	            except AttributeError:
    	                mediainfo_audio_track[item] = "N/A"
    	        mediainfo_audio_track_master.append(mediainfo_audio_track)
    	        
    	            
        
#print "---------------------------------------"
#print "FFPROBE output"
probe_file(args.input)
#print "---------------------------------------"
 
#print "container",ffprobe_format_master
#print "video",ffprobe_video_track_master
#print "audio",ffprobe_audio_track_master

#print "---------------------------------------"
#print "Mediainfo output"
mediainfo_file(args.input)
#print mediainfo_version[0]
#print "container",mediainfo_format_master
#print "video",mediainfo_video_track_master
#print "audio",mediainfo_audio_track_master


c.writerow(["","File Format","File Size","Duration","Overall bitrate"])
for i in range(0,len(mediainfo_format_master)):
    ffList = ffprobe_format_master[i]
    c.writerow(["ffprobe",ffList['format_long_name'],ffList['size'],ffList['duration'],ffList['bit_rate']])
    miList = mediainfo_format_master[i]
    c.writerow(["Media Info (" + mediainfo_version[0] + ")",miList['Format'],miList['FileSize'],miList['Duration_String'],miList['OverallBitRate_String']])
    c.writerow("")
for i in range(0,len(mediainfo_video_track_master)):
    c.writerow(["Video track " + str(i + 1),"Video Codec","Codec ID","Codec Profile","Display Aspect Ratio","Frame Rate","Chroma Subsamplling","Bit Depth","Colorspace","Pixel format"])
    ffList = ffprobe_video_track_master[i]
    c.writerow(["ffprobe",ffList['codec_name'],ffList['codec_tag_string'],ffList['profile'],ffList['display_aspect_ratio'],ffList['r_frame_rate'],ffList['pix_fmt']])
    miList = mediainfo_video_track_master[i]
    c.writerow(["Media Info (" + mediainfo_version[0] + ")" ,miList['Format'],miList['CodecID'],miList['Format_Profile'],miList['DisplayAspectRatio'],miList['FrameRate'],miList['ChromaSubsampling'],miList['Resolution'],miList['ColorSpace']])
    c.writerow("")
for i in range(0,len(mediainfo_audio_track_master)):
    c.writerow(["Audio track " + str(i + 1),"Audio Codec","Codec ID","Codec Profile","Sampling rate","Bit Depth","Number of Channels"])
    ffList = ffprobe_audio_track_master[i]
    c.writerow(["ffprobe",ffList['codec_name'],ffList['codec_tag_string'],'N/A',ffList['sample_rate'],ffList['bits_per_sample'],ffList['channels']])
    miList = mediainfo_audio_track_master[i]
    c.writerow(["Media Info (" + mediainfo_version[0] + ")",miList['Format'],miList['CodecID'],miList['Format_Profile'],miList['SamplingRate'],miList['AudioBitsPerSample'],miList['Channel_s_']])
    c.writerow("")


print "DONE!"
'''

write csv row with ffprobe format items


'''


