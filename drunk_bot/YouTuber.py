import re
from os import remove
from os.path import dirname, isfile
from re import findall
from urllib.parse import urlencode
from urllib.request import urlopen
from uuid import uuid4

from drunk_bot.Sync import Sync
from pafy import new

from drunk_bot.Systems import System


class YouTube:
    def __init__(self, system: System, sync: Sync):
        self.video = None
        self.vid_url = ""
        self.hik = "tmpload"
        self.vid_path = "videos"
        self.song_path = "songs"
        self.system = system
        self.system.verbosity = 2
        self.system.get_system()
        self.system.get_src_folder()
        self.sync = sync

    @staticmethod
    def get_url_by_name(name_of_song, num=0):
        html_content = urlopen("http://www.youtube.com/results?" + urlencode({"search_query": name_of_song}))
        search_results = findall(r'href=\"/watch\?v=(.{11})', html_content.read().decode())
        return "http://www.youtube.com/watch?v=%s" % str(search_results[num])

    def video_url(self, context: str, num=0):
        if "http" in context and "://" in context:
            return context.replace('\n', '').strip()
        else:
            return self.get_url_by_name(context.replace('\n', '').strip(), num)

    def load_video(self, context, num=0):
        self.vid_url = self.video_url(context, num)
        print("Video url is: %s" % self.vid_url)
        self.video = new(self.vid_url)
        return self.video.title, self.video.rating, self.video.length, self.video.description, self.video.getbest()

    def show_details(self, details: tuple):
        return "\n**Title:**:= %s\n" \
               "**Rating:** %s/5\n" \
               "**Length:** %s(s)\n\n" \
               "**Desc:** %s\n" \
               "***Video:*** %s" % (details[0], str(details[1])[0:3], details[2], details[3], self.vid_url)

    def convert_video(self, path, new_name, song_name):
        if isfile(new_name):
            remove(new_name)
        if isfile(song_name):
            remove(song_name)
        correct, get_raw = self.system.ffmpeg("-i \"%s\" \"%s\"" % (path, new_name))
        print("ffmpeg output: %s" % str(get_raw))
        correct, get_raw = self.system.ffmpeg("-i \"%s\" \"%s\"" % (new_name, song_name))
        print("ffmpeg output: %s" % str(get_raw))
        remove(path)
        self.sync.youtube = False
        return correct

    def download_video(self, context, desc=False, num=0, tosend=None):
        self.sync.youtube = True
        details = self.load_video(context, num)
        if desc:
            if tosend is not None:
                tosend(self.show_details(details))
        name = str(uuid4())
        path = dirname(__file__) + "/" + self.hik + "/" + name + "." + details[-1].extension
        details[-1].download(filepath=path, quiet=False)
        new_name = re.sub('[^0-9a-zA-Z()_. -]+', '', details[0])
        return self.convert_video(path, dirname(__file__) + "/" + self.vid_path + "/" + new_name + ".mp4",
                                  dirname(__file__) + "/" + self.song_path + "/" + new_name + ".mp3")
