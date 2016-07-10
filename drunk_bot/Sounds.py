import asyncio
from os import listdir
from os.path import dirname, isfile, join, basename
from re import sub

from drunk_bot.Systems import System


# noinspection PyBroadException
class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}*'
        try:
            duration = self.player.duration
            if duration:
                fmt += ' ... [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        except (AssertionError, AttributeError, TypeError):
            try:
                duration = self.player.duration
                if duration:
                    fmt += ' ... [length: {}(s)]'.format(str(duration))
            except Exception:
                pass
        if dirname(__file__) in self.player.title:
            self.player.title = str(basename(self.player.title)).replace('.mp3', '')
        return fmt.format(self.player)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.client = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()
        self.audio_player = self.client.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.client.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.client.send_message(self.current.channel, "Now playing " + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


# noinspection PyBroadException,PyCompatibility
class Music:
    def __init__(self, client, system: System):
        self.client = client
        self.system = system
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.client)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.client.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.client.loop.create_task(state.voice.disconnect())
            except Exception:
                pass

    async def summon(self, message):
        summoned_channel = message.author.voice_channel
        if summoned_channel is None:
            await self.client.send_message(message.channel,
                                           ("<@%s> " % message.author.id) +
                                           "**You must be in a voice channel to add the drunk in...**")
            return False

        state = self.get_voice_state(message.server)
        if state.voice is None:
            state.voice = await self.client.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)
        return True

    async def play(self, message, song: str):
        state = self.get_voice_state(message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        '''
        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return
        '''

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           "Error playing audio query")
        else:
            player.volume = 0.6
            entry = VoiceEntry(message, player)
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) + "Added  " + str(entry))
            await state.songs.put(entry)

    @staticmethod
    def clean_path(path: str):
        maps = [("(", "\("), (")", "\)")]
        for mape in maps:
            path = path.replace(mape[0], mape[1])
        return path

    async def play_load(self, message, song: str):
        state = self.get_voice_state(message.server)
        path = dirname(__file__) + "/songs/"
        print(path)
        dir_list = listdir(path)
        files = [("%s%s" % (path, f)) for f in dir_list if isfile(join(path, f))]
        songer = None
        try:
            ind = int(song)
            songer = files[ind]
        except (ValueError, TypeError, AssertionError):
            print("Not just a number trying name...")
            for file in files:
                name = file.replace(path, '').lower()
                if song.lower() in name:
                    songer = file
                    break

        if songer is None:
            if dirname(__file__) in song and ".mp3" in song:
                songer = song

        if songer is None:
            print("Song is none...")
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           "Couldn't find that song")
            return
        try:
            player = state.voice.create_ffmpeg_player(songer, after=state.toggle_next)
        except Exception as e:
            print("FAILED at soundes %s" % str(e))
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           "Error playing audio query")
        else:
            player.volume = 0.6
            player.title = songer.replace(path, '').replace('.mp3', '')
            '''
            try:
                player.title = player.title[:player.title.rfind('.')]
            except:
                player.title.replace('.mp3', '')
            '''
            video_length = None
            try:
                correct, get_raw = self.system.ffprobe("-v quiet -of csv=p=0 -show_entries" +
                                                       " format=duration '%s'" % str(songer))
                if not correct:
                    self.system.verbo_print("Couldn't get video length setting default...", 1)
                    video_length = 2000
                digits = sub("[^0-9 .]", "", str(get_raw))
                video_length = round(float(digits) + 1)
            except Exception:
                pass
            if video_length is not None:
                player.duration = video_length
            entry = VoiceEntry(message, player)
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) + "Added  " + str(entry))
            await state.songs.put(entry)

    async def volume(self, message, value: int):
        state = self.get_voice_state(message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.client.send_message(message.channel,  ("<@%s> " % message.author.id) +
                                           "Setting volume to {:.0%}".format(player.volume))

    async def pause(self, message):
        state = self.get_voice_state(message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           "Paused %s" % str(state.current))

    async def resume(self, message):
        state = self.get_voice_state(message.server)
        if state.is_playing():
            player = state.player
            player.resume()
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           "Resumed %s" % str(state.current))

    async def stop(self, message):
        server = message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           "Stopped %s" % str(state.current))

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    async def skip(self, message):
        state = self.get_voice_state(message.server)
        if not state.is_playing():
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           'Not playing any music right now...')
            return

        voter = message.author
        if voter == state.current.requester:
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           'Requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                               'Skip vote passed (3), skipping song...')
                state.skip()
            else:
                await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                               'Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                           'You have already voted...')

    async def playing(self, ctx):
        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.client.say('No audio files being played...')
        else:
            skip_count = len(state.skip_votes)
            await self.client.say('Playing {} ... skips: {}/3'.format(state.current, skip_count))
