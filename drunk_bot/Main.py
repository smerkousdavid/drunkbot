import random
from datetime import datetime, timedelta
from os import listdir, environ, pathsep, sep, remove
from os.path import dirname, isfile, join
from sys import stdout
from threading import Thread
from time import time, sleep
from traceback import print_exc

import discord

from drunk_bot.ChatterBox import Chatty
from drunk_bot.Commands import Commands
from drunk_bot.Musics import process_text
from drunk_bot.Sounds import Music
from drunk_bot.Sync import Sync
from drunk_bot.YouTuber import YouTube

from drunk_bot.Systems import System

if not discord.opus.is_loaded():
    opus_libs = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']
    for opus_lib in opus_libs:
        try:
            discord.opus.load_opus(opus_lib)
            break
        except OSError:
            pass
    raise OSError("Couldn't load the opus make sure libffi is installed!!!")

notation = "!"
client = discord.Client()
commands = Commands(notation)
system = System(client)
sync = Sync()
youtube = YouTube(system, sync)
music = Music(client, system)
chatty = Chatty()

last_song = False
last_youtube = False
start_time = time()

system.verbosity = 0
is_ffmpeg_path = ("ffmpeg version" in str(system.command("ffmpeg")[1])) or \
                 ("ffmpeg version" in str(system.command("ffmpeg.exe")[1]))
system.verbosity = 3
thread = None
cool_time = time()
cool_delay = 10

startup = None
nickname = None

audio_response = "Audio command\nUsage: audio <play (file/num)|list|pause|resume|stop|volume (set)|download " \
                 "(artist name/url to mp3) (optional: numtracks)|playall|delete (song name/ind) (all)|upload " \
                 "(song name/ind) (all)>\n" \
                 "Desc: Command to mess with audio files and downloaded/loaded youtube files, ability to download " \
                 "mp3. Finally an upload option so that any user can download the music onto their computer for" \
                 "sharing!" \
                 "and play all songs that are currently downloaded"

youtube_response = "YouTube command\nUsage: youtube <video name/link> <details (describe)> <download (download)> " \
                   "<play (play)>\n" \
                   "Desc: Command to download and show details about youtube videos"

if not is_ffmpeg_path:
    print("ffmpeg not found on system using static builds... :(")
    ffmpeg_static = system.get_ffmpeg_folder()
    if ffmpeg_static[-1] == sep:
        ffmpeg_static = ffmpeg_static[:ffmpeg_static.rfind(sep)]
    print("Using static ffmpeg folder: %s" % ffmpeg_static)
    environ["PATH"] += pathsep + ffmpeg_static
else:
    print("Found ffmpeg in path using that!")

# Add chrome driver to path
environ["PATH"] += pathsep + dirname(__file__) + "/"


# noinspection PyBroadException,PyCompatibility
@client.event
async def on_message(message):
    global last_youtube, last_song, thread, cool_delay, cool_time
    print("Author: %s :Message: %s\n\n" % (message.author, message.content))

    if sync.youtube and not last_youtube:
        last_youtube = True
    elif not sync.youtube and last_youtube:
        await client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                  "Done downloading youtube video")
        last_youtube = False

    if thread is not None and not last_song:
        last_song = True
    elif thread is not None:
        if not thread.is_alive():
            await client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                      "Done downloading song/audio")
            last_song = False
            thread = None

    if message.author == client.user:
        return

    print("client id %s" % client.user.id)

    try:
        if message.content.index("%s> " % client.user.id) != -1:
            chat_ret = str(chatty.chat(str(message.content)[len("<@%s> " % client.user.id):]))
            print("Chatty return %s" % chat_ret)
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + chat_ret)
            return
    except Exception:
        pass

    response = commands.run_command(message.content)

    if response is not None:
        await client.send_typing(message.channel)
        print("Ran command successfully...")
        await client.send_message(message.channel, ("<@%s> " % message.author.id) + response)
        return

    mess = str(message.content)

    if mess.startswith(notation + "uptime"):
        time_lap = time() - start_time
        sec = timedelta(seconds=int(time_lap))
        dates = datetime(1, 1, 1) + sec
        response = "**Uptime**: %d Days, %d Hours, %s Minutes, %s Seconds" % \
                   (dates.day - 1, dates.hour, dates.minute, dates.second)
        await client.send_message(message.channel, ("<@%s> " % message.author.id) + response)
        return

    if mess.startswith(notation + "help"):

        advanced = False
        specific = None
        try:
            args = mess[len(notation + "help"):].split()
            if args[0].lower() == "advanced":
                print("Getting advanced version")
                advanced = True
            elif len(args[0]) > 0:
                specific = str(args[0])
        except:
            pass

        notes = commands.get_help()

        hard_coded = [
            ("help", "Usage: !help (advanced)\nDesc: Helps you out"),
            ("uptime", "Usage: !uptime\nDesc: Tells you how long the bot has been up"),
            ("annoy", "Usage: !annoy\nDesc: Makes an annoying sounds"),
            ("audio", audio_response),
            ("youtube", youtube_response),
        ]

        for coded in hard_coded:
            notes.append([coded[0], coded[1]])

        if advanced:
            help_list = []
            notes = sorted(notes, key=lambda x: x[0])
            for ind, com in enumerate(notes):
                help_list.append('```' + str(ind) + ": " + com[0] + "\n" + com[1] + '```')
            compiled = "**Help list (advanced):**\n**-------------------------------------**\n" + '\n'.join(help_list)
        else:
            temp_notes = []
            for com in notes:
                temp_notes.append(com[0])
            if specific is not None:
                for ind, com in enumerate(temp_notes):
                    if specific == com:
                        compiled = "**Help %s**\n```%s\n%s```" % (com, com, notes[ind][1])
                        await client.send_message(message.channel, compiled)
                        return
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Couldn't find **%s** "
                                                                                            "as a command" % specific)
                return
            print(temp_notes)
            temp_notes = sorted(temp_notes)
            compiled = ("Help list (simple)\ndo ***%shelp advanced*** for more info"
                        "\n**-------------------------------------**\n`" % notation) + (', '.join(temp_notes)) + '`'
        await client.send_message(message.channel, compiled)

    if mess.startswith(notation + "annoy"):
        await music.summon(message)
        try:
            state = music.get_voice_state(message.server)
            if int(round(time() - cool_time, 2)) > cool_delay:
                player = state.voice.create_ffmpeg_player(dirname(__file__) + "/randoms/" +
                                                          random.choice(listdir(dirname(__file__) + "/randoms/")),
                                                          after=state.toggle_next)
                player.start()
                await client.send_message(message.channel,
                                          ("<@%s> " % message.author.id) + "***Annoy!!!...  Hehe***")
                cool_time = time()
            else:
                print("Cool time not reached yet")
                await client.send_message(message.channel,
                                          ("<@%s> " % message.author.id) + "Nope not for you... you still have %d "
                                                                           "seconds left"
                                          % (cool_delay - int(round(time() - cool_time, 2))))
        except:
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + "I failed to annoy **:(**")

    if mess.startswith(notation + "audio"):
        args = []
        response = audio_response
        try:
            args = mess[len(notation + "audio"):].split()
            comm = args[0]
        except (AssertionError, IndexError, TypeError) as err:
            print("FAILED: %s" % str(err))
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + response)
            return

        if "pause" in comm:
            await music.pause(message)
        elif "resume" in comm:
            await music.resume(message)
        elif "stop" in comm:
            await music.stop(message)
        elif "volume" in comm:
            raw = args[1]
            try:
                value = int(raw)
                await music.volume(message, value)
            except Exception as err:
                print("FAILED %s" % str(err))
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + response)
        elif "skip" in comm:
            await music.skip(message)
        elif "list" in comm:
            path = dirname(__file__) + "/songs/"
            print(path)
            dir_list = listdir(path)
            files = [("[%d] : %s" % (i, f.replace('.mp3', '').replace('\n', '')))
                     for i, f in enumerate(dir_list) if isfile(join(path, f))]
            await client.send_message(message.channel,
                                      "**Songs downloaded:** \n**--------------------------------------**\n```%s```"
                                      "\n" % str(',\n'.join(files)))
        elif "playall" in comm:
            path = dirname(__file__) + "/songs/"
            print(path)
            dir_list = listdir(path)
            files = [("%s%s" % (path, f.replace('\n', ''))) for f in dir_list if isfile(join(path, f))]
            print(files)
            await music.summon(message)
            for file in files:
                await music.play_load(message, file)
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Added all songs to queue")

        elif "play" in comm:
            await music.summon(message)
            try:
                raw = args[1]
                await music.play_load(message, raw)
            except:
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Arguments incorrect...\n"
                                          + response)
        elif "download" in comm:
            song_num = 10
            try:
                artist = str(args[1])
                try:
                    song_num = int(args[2])
                except:
                    pass
            except:
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Arguments incorrect...\n"
                                          + response)
                return

            try:
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "**Downloading** songs... "
                                                                                            "Please wait")
                thread = Thread(target=process_text, args=(artist, song_num, system, sync,))
                thread.setDaemon(True)
                thread.start()
            except Exception as err:
                error = "Artist not found..." if "Expecting value" in str(err.args[0]) else str(err.args[0])
                print(error)
                await client.send_message(message.channel,
                                          "```Failed downloading song(s), Error: %s```" % error)
        elif "delete" in comm:
            try:
                raw = str(args[1])
                alls = None
                amount = 0
                try:
                    alls = str(args[2])
                except:
                    pass
                ind = None
                if raw.isdigit():
                    ind = int(raw)
                path = dirname(__file__) + "/songs/"
                print(path)
                dir_list = listdir(path)
                files = [("%s%s" % (path, f.replace('\n', ''))) for f in dir_list if isfile(join(path, f))]
                print(files)
                if ind is not None:
                    remove(files[ind])
                    amount += 1
                else:
                    for file in files:
                        name = file.replace(path, '').lower()
                        if raw.lower() in name:
                            remove(file)
                            amount += 1
                            if alls is None:
                                break
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "**Deleted**"
                                                                                            " %d song(s)...\n" %
                                          amount)
            except Exception as err:
                print("ERROR: %s" % str(err))
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Arguments incorrect...\n"
                                          + response)
        elif "upload" in comm:
            try:
                raw = str(args[1])
                alls = None
                amount = 0
                try:
                    alls = str(args[2])
                except:
                    pass
                ind = None
                if raw.isdigit():
                    ind = int(raw)
                path = dirname(__file__) + "/songs/"
                print(path)
                dir_list = listdir(path)
                files = [str(f).replace('\n', '') for f in dir_list if isfile(join(path, f))]
                print(files)
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "**Uploading** music")
                if ind is not None:
                    await client.send_file(message.channel, path + files[ind], filename=str(files[ind])
                                           .replace('.mp3', ''),
                                           content="Music uploaded by: " + ("<@%s> " % message.author.id))
                else:
                    for file in files:
                        name = file.replace(path, '').lower()
                        if raw.lower() in name:
                            await client.send_file(message.channel, path + file,
                                                   filename=file.replace('.mp3', ''))
                            amount += 1
                            if alls is None:
                                break
                    await client.send_message(message.channel, ("<@%s> " % message.author.id) + "**Uploaded**"
                                                                                                " %d song(s)...\n" %
                                              amount)
            except Exception as err:
                print("ERROR: %s" % str(err))
                print_exc(file=stdout)
                await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Arguments incorrect...\n"
                                          + response)
        else:
            print("FAILED at no command")
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + response)

    if mess.startswith(notation + "youtube"):
        # if music.get_voice_state(message.server) is None:
        await client.send_typing(message.channel)
        args = []
        try:
            args = mess[len(notation + "youtube"):].split()
            desc = False
            download = False
            play = False
            name = args[0]
        except (AssertionError, IndexError, TypeError):
            response = youtube_response
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + response)
            return
        for arg in range(1, len(args)):
            if "describe" in args[arg]:
                desc = True
            elif "download" in args[arg]:
                download = True
            elif "play" in args[arg]:
                play = True
            else:
                name += args[arg]
        try:
            if download:
                details = youtube.show_details(youtube.load_video(name))
                await client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                          details[:details.index("Desc:")] + "\n\nDownloading to videos...")
                sync.youtube = True
                if play:
                    await music.play(message, youtube.vid_url)
                thread = Thread(target=youtube.download_video, args=(name, desc,))
                thread.setDaemon(True)
                thread.start()
            else:
                await client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                          youtube.show_details(youtube.load_video(name)))
                if youtube.vid_url is None:
                    print("Failed loading video...")
                if play and youtube.vid_url is not None:
                    await music.summon(message)
                    print("Playing link %s" % youtube.vid_url)
                    await client.send_message(message.channel, ("<@%s> " % message.author.id) +
                                              "\nAdding video to music playlist use '**audio**' now")
                    await music.play(message, youtube.vid_url)
        except (IndexError, TypeError, discord.HTTPException, discord.ClientException, discord.DiscordException):
            await client.send_message(message.channel, ("<@%s> " % message.author.id) + "Failed finding/loading "
                                                                                        "youtube")


# noinspection PyCompatibility,PyBroadException
@client.event
async def on_ready():
    global startup, nickname
    print('Logged in...\nUser: %s\nId: %s\n\n\n' % (client.user.name, str(client.user.id)))
    print("Loading commands...")
    commands.load_commands()
    print("Done loading commands...\n")
    if startup is not None:
        await client.wait_until_login()
        print("Setting startup message %s" % startup)
        try:
            for channel in client.get_all_channels():
                print("Found channel %s" % str(channel))
                await client.send_message(channel, startup)
                sleep(0.1)
        except Exception:
            pass

    if nickname is not None:
        await client.wait_until_login()
        print("Setting new nickname %s" % nickname)
        try:
            for server in client.servers:
                await client.change_nickname(server.me, nickname)
                sleep(0.1)
        except Exception:
            pass


def main(start=None, name=None):
    global startup, nickname
    startup = start
    nickname = name
    print("Welcome to drunkbot!\nLogging in...")
    client.run(open("token.txt", "r").read().replace('\n', '').strip())


if __name__ == "__main__":
    main()
