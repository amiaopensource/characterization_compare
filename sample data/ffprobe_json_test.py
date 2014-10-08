import subprocess
from Search import search_dict
import json

media_file = '/Users/eugenegekhter/dev/hls/883_1000_1405485842_00058mts_HQ.mp4'

ffprobe_check_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', '-i', media_file]
s = subprocess.Popen(ffprobe_check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

ffprobe_out, err = s.communicate()

ffprobe_dict = json.loads(ffprobe_out)
duration = search_dict(ffprobe_dict, 'duration')
print duration