#!/usr/bin/env python

import argparse, os, subprocess, csv, json, time, datetime
from subprocess import call
import xml.etree.ElementTree as ET
from helpers import Search

parser = argparse.ArgumentParser(description="Python tool for comparing the output of video characterization tools")
parser.add_argument('-i', '--input', type=str, required=True, help='The full path to the file you want to analyze.')
parser.add_argument('-o', '--output', type=str, required=True, help='where to put csv report')
args = parser.parse_args()

ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
st = st.replace(" ","_")


path, filename = os.path.split(args.input)

csv_path = args.output+filename+"---char_compare---"+st+".csv"
c = csv.writer(open(csv_path, "wb"))

# ===============
# FFPROBE attributes
ffprobe_format_master = []
ffprobe_video_track_master = []
ffprobe_audio_track_master = []
ffprobe_version = []
# ===============
# Mediainfo attributes
mediainfo_format_master = []
mediainfo_video_track_master = []
mediainfo_audio_track_master = []
mediainfo_version = []
# ===============
# EXIFTOOL attributes
exiftool_format = {'file_format': None, 'file_size': None, 'duration': None, 'overall_bitrate': None}
exiftool_video_track = {'codec': None, 'codec_profile': None, 'dar': None, 'width': None, 'height': None,
                        'frame_rate': None, 'chroma_subsample': None, 'bit_depth': None, 'colorspace': None,
                        'pixel_format': None}
exiftool_audio_track = {'codec': None, 'codec_profile': None, 'sampling_rate': None, 'bit_depth': None,
                        'number_channels': None}


def probe_file(filename):
    cmnd = ['ffprobe', '-show_format', '-show_streams', '-show_error', '-show_versions', '-print_format', 'xml',
            filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    root = ET.fromstring(out)

    for program in root.iter('program_version'):
        ffprobe_version.append(program.attrib['version'])

    for elem in root.iterfind('format'):
        ffprobe_format = {'format_long_name': None, 'size': None, 'duration': None, 'bit_rate': None}
        for item in ffprobe_format:
            try:
                ffprobe_format[item] = elem.attrib[item]
            except KeyError:
                ffprobe_format[item] = "N/A"
        ffprobe_format_master.append(ffprobe_format)
    for stream in root.iter('stream'):
        if stream.attrib['codec_type'] == "video":
            ffprobe_video_track = {'codec_name': None, 'profile': None, 'display_aspect_ratio': None, 'width': None,
                                   'height': None, 'r_frame_rate': None, 'chroma_subsampling': None,
                                   'bits_per_raw_sample': None, 'color_space': None, 'pix_fmt': None}
            for item in ffprobe_video_track:
                try:
                    ffprobe_video_track[item] = stream.attrib[item]
                except KeyError:
                    ffprobe_video_track[item] = "N/A"
            ffprobe_video_track_master.append(ffprobe_video_track)
        elif stream.attrib['codec_type'] == "audio":
            ffprobe_audio_track = {'codec_name': None, 'sample_rate': None, 'bits_per_sample': None, 'channels': None}
            for item in ffprobe_audio_track:
                try:
                    ffprobe_audio_track[item] = stream.attrib[item]
                except KeyError:
                    ffprobe_video_track[item] = "N/A"
            ffprobe_audio_track_master.append(ffprobe_audio_track)


# ===============
# Mediainfo Harvesting
def mediainfo_file(filename):
    cmnd = ['mediainfo', '-f', '--language=raw', '--Output=XML', filename]
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    root = ET.fromstring(out)

    mediainfo_version.append(root.attrib['version'])

    for file in root.iterfind('File'):
        for track in file.iterfind('track'):
            if track.attrib['type'] == "General":
                mediainfo_format = {'Format': None, 'Codec_Profile': None, 'FileSize': None, 'Duration': None,
                                    'OverallBitRate': None}
                for item in mediainfo_format:
                    try:
                        mediainfo_format[item] = track.find(item).text
                    except AttributeError:
                        mediainfo_format[item] = "N/A"
                mediainfo_format_master.append(mediainfo_format)
            if track.attrib['type'] == "Video":
                mediainfo_video_track = {'Codec': None, 'Codec_Profile': None, 'DisplayAspectRatio_String': None,
                                         'Width': None, 'Height': None, 'FrameRate': None, 'ChromaSubsampling': None,
                                         'Resolution': None, 'ColorSpace': None, 'pix_fmt': None}
                for item in mediainfo_video_track:
                    try:
                        mediainfo_video_track[item] = track.find(item).text
                    except AttributeError:
                        mediainfo_video_track[item] = "N/A"
                mediainfo_video_track_master.append(mediainfo_video_track)
            if track.attrib['type'] == "Audio":
                mediainfo_audio_track = {'Codec': None, 'SamplingRate': None, 'BitDepth': None, 'Channel_s_': None,
                                         'StreamKindPos': None}
                for item in mediainfo_audio_track:
                    try:
                        mediainfo_audio_track[item] = track.find(item).text
                    except AttributeError:
                        mediainfo_audio_track[item] = "N/A"
                mediainfo_audio_track_master.append(mediainfo_audio_track)


def exif_file(filename, format, video, audio):
    exiftool_check_cmd = ['exiftool', '-j', filename]
    s = subprocess.Popen(exiftool_check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exiftool_out, err = s.communicate()

    exiftool_list = json.loads(exiftool_out)
    exiftool_dict = {}

    if len(exiftool_list) > 0:
        exiftool_dict = exiftool_list[0]

    # format
    format['file_format'] = Search.search_dict(exiftool_dict, 'FileType')
    format['file_size'] = Search.search_dict(exiftool_dict, 'MovieDataSize')
    format['duration'] = Search.search_dict(exiftool_dict, 'Duration')
    format['overall_bitrate'] = Search.search_dict(exiftool_dict, 'AvgBitrate')

    #video
    video['codec'] = Search.search_dict(exiftool_dict, 'CompressorID')
    video['codec_profile'] = None
    video['dar'] = Search.search_dict(exiftool_dict, 'PresentationAspectRatio')
    video['width'] = Search.search_dict(exiftool_dict, 'ImageWidth')
    video['height'] = Search.search_dict(exiftool_dict, 'ImageHeight')
    video['frame_rate'] = Search.search_dict(exiftool_dict, 'VideoFrameRate')
    video['chroma_subsample'] = None
    video['bit_depth'] = Search.search_dict(exiftool_dict, 'BitDepth')
    video['color_space'] = None
    video['pixel_format'] = None

    #audio
    audio['codec'] = Search.search_dict(exiftool_dict, 'AudioFormat')
    audio['sampling_rate'] = Search.search_dict(exiftool_dict, 'AudioSampleRate')
    audio['bit_depth'] = Search.search_dict(exiftool_dict, 'AudioBitsPerSample')
    if len(audio['bit_depth']) == 0:
        audio['bit_depth'] = Search.search_dict(exiftool_dict, 'BitsPerAudioSample')
    audio['number_channels'] = Search.search_dict(exiftool_dict, 'AudioChannels')
    if len(audio['number_channels']) == 0:
        audio['number_channels'] = Search.search_dict(exiftool_dict, 'ChannelCount')

    version = Search.search_dict(exiftool_dict, 'ExifToolVersion')[0]

    for k, v in video.iteritems():
        if v is not None:
            if len(v) > 0:
                video[k] = v[0]
            else:
                video[k] = 'N/A'
        else:
            video[k] = 'N/A'

    for k, v in audio.iteritems():
        if v is not None:
            if len(v) > 0:
                audio[k] = v[0]
            else:
                audio[k] = 'N/A'
        else:
            audio[k] = 'N/A'

    for k, v in format.iteritems():
        if v is not None:
            if len(v) > 0:
                format[k] = v[0]
            else:
                format[k] = 'N/A'
        else:
            format[k] = 'N/A'

    return format, video, audio, str(version)

# print "---------------------------------------"
print "Running FFprobe Analysis..."
probe_file(args.input)
print "Done!"
#print "---------------------------------------"

#print "container",ffprobe_format_master
#print "video",ffprobe_video_track_master
#print "audio",ffprobe_audio_track_master

#print "---------------------------------------"
print "Running Mediainfo Analysis..."
mediainfo_file(args.input)
print "Done!"
#print mediainfo_version[0]
#print "container",mediainfo_format_master
#print "video",mediainfo_video_track_master
#print "audio",mediainfo_audio_track_master

# print "---------------------------------------"
print "Running Exiftool Analysis..."
exiftool_format, exiftool_video_track, exiftool_audio_track, exif_version = exif_file(args.input, exiftool_format,
                                                                        exiftool_video_track, exiftool_audio_track)
print "Done!"
# print "container", exiftool_format
# print "video", exiftool_video_track
# print "audio", exiftool_audio_track

print "Generating CSV Report..."
c.writerow(["Report on:", args.input])
c.writerow("")
c.writerow(["", "File Format", "File Size", "Duration", "Overall bitrate"])

for i in range(0, len(mediainfo_format_master)):
    ffList = ffprobe_format_master[i]
    c.writerow(["ffprobe (" + ffprobe_version[0] + ")", ffList['format_long_name'], ffList['size'], ffList['duration'],
                ffList['bit_rate']])
    miList = mediainfo_format_master[i]
    c.writerow(["Media Info (" + mediainfo_version[0] + ")", miList['Format'], miList['FileSize'], miList['Duration'],
                miList['OverallBitRate']])
    c.writerow(["ExifTool (" + exif_version + ")", exiftool_format['file_format'], exiftool_format['file_size'], exiftool_format['duration'],
                exiftool_format['overall_bitrate']])
    c.writerow("")
for i in range(0, len(mediainfo_video_track_master)):
    c.writerow(["Video track " + str(i + 1), "Video Codec", "Codec Profile", "Display Aspect Ratio", "Width", "Height",
                "Frame Rate", "Chroma Subsampling", "Bit Depth", "Colorspace", "Pixel format"])
    ffList = ffprobe_video_track_master[i]
    c.writerow(["ffprobe (" + ffprobe_version[0] + ")", ffList['codec_name'], ffList['profile'],
                ffList['display_aspect_ratio'], ffList['width'], ffList['height'], ffList['r_frame_rate'],
                ffList['chroma_subsampling'], ffList['bits_per_raw_sample'], ffList['color_space'], ffList['pix_fmt']])
    miList = mediainfo_video_track_master[i]
    c.writerow(["Media Info (" + mediainfo_version[0] + ")", miList['Codec'], miList['Codec_Profile'],
                miList['DisplayAspectRatio_String'], miList['Width'], miList['Height'], miList['FrameRate'],
                miList['ChromaSubsampling'], miList['Resolution'], miList['ColorSpace'], miList['pix_fmt']])
    c.writerow(["ExifTool (" + exif_version + ")", exiftool_video_track['codec'], exiftool_video_track['codec_profile'],
                exiftool_video_track['dar'], exiftool_video_track['width'], exiftool_video_track['height'], exiftool_video_track['frame_rate'],
                exiftool_video_track['chroma_subsample'], exiftool_video_track['bit_depth'], exiftool_video_track['colorspace'], exiftool_video_track['pixel_format']])
    c.writerow("")
for i in range(0, len(mediainfo_audio_track_master)):
    c.writerow(["Audio track " + str(i + 1), "Audio Codec", "Sampling rate", "Bit Depth", "Number of Channels"])
    ffList = ffprobe_audio_track_master[i]
    c.writerow(
        ["ffprobe (" + ffprobe_version[0] + ")", ffList['codec_name'], ffList['sample_rate'], ffList['bits_per_sample'],
         ffList['channels']])
    miList = mediainfo_audio_track_master[i]
    c.writerow(
        ["Media Info (" + mediainfo_version[0] + ")", miList['Codec'], miList['SamplingRate'], miList['BitDepth'],
         miList['Channel_s_']])
    c.writerow(
        ["ExifTool (" + exif_version + ")", exiftool_audio_track['codec'], exiftool_audio_track['sampling_rate'], exiftool_audio_track['bit_depth'],
         exiftool_audio_track['number_channels']])
    c.writerow("")

print "Done!"
print "Find report at "+csv_path