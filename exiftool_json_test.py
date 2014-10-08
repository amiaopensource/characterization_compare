import subprocess
from helpers import Search
import json

media_file = '/Users/eugenegekhter/dev/hls/883_1000_1405485842_00058mts_HQ.mp4'

exiftool_check_cmd = ['exiftool', '-j', media_file]
s = subprocess.Popen(exiftool_check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
exiftool_out, err = s.communicate()

exiftool_list = json.loads(exiftool_out)
exiftool_dict = {}

if len(exiftool_list) > 0:
    exiftool_dict = exiftool_list[0]

print Search.search_dict(exiftool_dict, 'Duration')
