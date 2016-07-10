from os import environ, ctermid, close, open, O_RDONLY
from os.path import dirname, realpath, sep
from platform import architecture
from re import sub
from signal import signal, SIGINT
from subprocess import Popen, PIPE, STDOUT
from sys import platform as _platforms, exit, stdout
from discord import Client

client = None


class DrunkBotException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


# noinspection PyBroadException
def handle_exit(code, frame):
    global client
    try:
        client.close()
        if not client.is_closed():
            client.close()
        print("Clean exit attempted")
    except:
        print("Failed clean exit... Hard exiting...")
    try:
        print("Drunkbot exiting(Frame: %d)... %d" % (frame, code))
        exit(code)
    except TypeError:
        print("Drunkbot exit!!!")
        exit(1)


class System:
    def __init__(self, clients: Client):
        global client
        self.system = None
        self.frames = 2000
        self.timeout_seconds = 4
        self.verbosity = 3
        self.is_ide = "PYCHARM_HOSTED" in environ
        self.pre_imp = "Processing"
        client = clients
        if self.is_ide:
            print("Running script in IDE! simple debug enabled")
        signal(SIGINT, handle_exit)

    def report_error(self, mess, num=1):
        raise DrunkBotException("(Code %d, Verbose %d) %s" % (num, self.verbosity, mess))

    def verbo_print(self, mess, num, equal=False):
        if self.verbosity >= num if not equal else num == self.verbosity:
            print(mess)

    @staticmethod
    def print_progress(iteration, total, prefix='', suffix='', decimals=2, bar_length=100):
        filled_length = int(round(bar_length * iteration / float(total)))
        percents = round(100.00 * (iteration / float(total)), decimals)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        stdout.write('%s [%s] %s%s %s\r' % (prefix, bar, percents, '%', suffix)),
        stdout.flush()
        if iteration == total:
            print("\n")

    def term_width(self):
        env = environ

        def ioctl_win(fd):
            try:
                import fcntl, termios, struct, os
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                     '1234'))[1]
            except (OSError, ValueError, IndexError, IOError, TypeError):
                return
            return cr

        cr = ioctl_win(0) or ioctl_win(1) or ioctl_win(2)
        if not cr:
            try:
                fd = open(ctermid(), O_RDONLY)
                cr = ioctl_win(fd)
                close(fd)
            except (OSError, ValueError, IndexError, IOError, TypeError):
                pass
        if not cr:
            cr = env.get('COLUMNS', 80)  # (env.get('LINES', 25), env.get('COLUMNS', 80))
        self.verbo_print("Terminal width: %d" % int(cr), 3)
        return int(cr)  # int(cr[1]), int(cr[0])

    def command(self, com, ret_err=0, err_text=None):
        if not len(str(com)) > 0:
            return [False, ""]
        ff = False
        if ("-vf" in com and "[in]" in com and "overlay" in com) or ("http" in com and ":" in com):
            self.verbo_print("Preparing command for ffmpeg", 3)
            ff = True
        com_list = str(com)  # .strip(" ").split(" ") if not isinstance(com, list) else com
        try:
            if not ff:
                child = Popen(com_list, stderr=PIPE, stdout=PIPE, shell=True)
            else:
                child = Popen(com_list, stderr=STDOUT, stdout=PIPE, shell=True)
            communicate = (" ", " ")
            try:
                if not ff:
                    communicate = child.communicate()
                    stream = (communicate[1] + communicate[0]) if communicate[1][0] is not None else communicate[0]
                else:
                    stream = " "
                    terminal_width = self.term_width() - 20
                    # terminal_width = terminal_width if terminal_width > 50 else 50
                    self.print_progress(0, 100, "Processing", "Complete", terminal_width)
                    while True:
                        output = ""
                        while True:
                            if child.poll() is not None:
                                break
                            output += child.stdout.read(1)
                            if "\r" in output[-1:] or "\n" in output[-1:] or child.poll() is not None:
                                break
                        if output == "" and child.poll() is not None:
                            # stdout.write("")
                            stdout.flush()
                            break
                        if output:
                            out = output.strip()
                            if self.verbosity >= 3:
                                print(out)
                            stream += out
                            try:
                                if out == "\n":
                                    continue
                                if "frame" in out and "fps" in out:
                                    frame_str = out[out.index("frame") + 5:out.index("fps")]
                                    frame = float(sub("[^0-9 .]", "", str(frame_str)))
                                    if self.verbosity > 0 and float((frame / self.frames)) < 99:
                                        if not self.is_ide:
                                            self.print_progress(int((frame / self.frames) * 100),
                                                                100, self.pre_imp, "Complete", terminal_width)
                                        else:
                                            print("\r{1}: {0}%".format(int((frame / self.frames) * 100), self.pre_imp)),

                            except (ValueError, IndexError):
                                pass

            except (IndexError, ValueError):
                stream = communicate[0]
            code = child.returncode
        except OSError as err:
            if ret_err == 0:
                self.verbo_print("WATER-WARNING: %s" % str(err.strerror), 2)
            else:
                self.report_error(err.strerror)
            return [False, "HANDLE"]
        if not self.is_ide:
            print("\n")
        if err_text is not None:
            if err_text in str(stream):
                return [False, ""]
        self.verbo_print(stream, 2)
        return [code < 1, stream]

    @staticmethod
    def get_src_folder():
        return dirname(realpath(__file__)) + sep + "src"

    def get_system_folder(self):
        folder = "%slinux" % sep
        if self.system == 0:
            folder = "%slinux" % sep
        elif self.system == 1:
            folder = "%smac" % sep
        elif self.system == 2:
            folder = "%swin" % sep
        return self.get_src_folder() + folder

    def get_ffmpeg_folder(self):
        folder = self.get_system_folder()
        arch = architecture()[0]
        if "64" in arch or "x86_64" in arch:
            arch = "64%s" % sep
        else:
            if self.system == 1:
                self.report_error("32bit Mac ffmpeg is currently not supported sorry!")
                exit(1)
            arch = "32%s" % sep
        return "%s%s%s" % (folder, sep, arch if self.system != 2 else (arch + "bin" + sep))

    def ffmpeg(self, args, ret_err=0, err_text=None):
        folder = self.get_ffmpeg_folder()
        executable = "ffmpeg" if self.system != 2 else "ffmpeg.exe"
        working = folder + executable + " " + str(args)
        self.verbo_print("Working ffmpeg: %s" % working, 2)
        return self.command(working, ret_err, err_text)

    def ffprobe(self, args, ret_err=0, err_text=None):
        folder = self.get_ffmpeg_folder()
        executable = "ffprobe" if self.system != 2 else "ffprobe.exe"
        working = folder + executable + " " + str(args)
        self.verbo_print("Working ffprobe: %s" % working, 2)
        return self.command(working, ret_err, err_text)

    def exif(self, args, ret_err=0, err_text=None):
        folder = self.get_system_folder()
        executable = sep + "exiftool" if self.system != 2 else sep + "exiftool.exe"
        working = folder + executable + " " + str(args)
        self.verbo_print("Working exiftool: %s" % working, 2)
        return self.command(working, ret_err, err_text)

    def get_system(self, spec=None):
        _platform = _platforms if spec is None else spec
        if _platform == "linux" or _platform == "linux2":
            self.system = 0
            self.verbo_print("Unix system detected... %s" % str(_platform), 2)
        elif _platform == "darwin":
            self.system = 1
            self.verbo_print("Darwin system detected... %s" % str(_platform), 2)
        elif _platform == "win32":
            self.system = 2
            self.verbo_print("Windows system detected... %s" % str(_platform), 2)
        else:
            self.system = None
            self.report_error("%s system is not supported" % str(_platform))

        if self.system is not None:
            self.verbo_print("Collected system information", 1, True)

        return self.system
