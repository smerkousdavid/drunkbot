import re


class Commands:
    def __init__(self, notation):
        self.file_loc = "Commands.txt"
        self.file = open(self.file_loc, "r")
        self.lines = self.file.readlines()

        self.c_sof = "<#"
        self.c_eof = "<#END#"
        self.c_e = "#>"
        self.commands = []

        self.touch_command = notation

    @staticmethod
    def find_meta(meta, full):
        meta_match = re.search(
            r"^{meta} = ['\"]([^'\"]*)['\"]".format(meta=meta),
            full, re.M
        )
        if meta_match:
            return meta_match.group(1)
        return None

    def load_commands(self):
        start_num = 1
        chunks = []
        for ind, line in enumerate(self.lines):
            if "%s%d%s" % (self.c_sof, start_num, self.c_e) in line:
                liner = ind + 1
                lines = []
                cur_line = self.lines[liner]
                while "%s%d%s" % (self.c_eof, start_num, self.c_e) not in cur_line:
                    cur_line = self.lines[liner]
                    lines.append(cur_line) if not "%s%d%s" % (self.c_eof, start_num, self.c_e) in cur_line else None
                    liner += 1
                chunks.append(lines)
                start_num += 1

        for chunk in chunks:
            full = ''.join(chunk)
            name = str(chunk[0]).replace('\n', '').strip(' ')
            try:
                arg_max = int(self.find_meta("max_args", full))
            except (TypeError, IndexError):
                arg_max = -1
            try:
                desc = str(self.find_meta("desc", full))
            except (TypeError, IndexError):
                desc = "There is no description for %s" % name
            try:
                usage = str(self.find_meta("usage", full))
            except (TypeError, IndexError):
                usage = "No usage for %s" % name
            try:
                arg_min = int(self.find_meta("min_args", full))
            except (TypeError, IndexError):
                arg_min = 0
            try:
                execs = str(self.find_meta("exec", full))
            except (TypeError, IndexError):
                execs = "return None"

            self.commands.append([name, arg_min, desc, usage, arg_max, execs])
            # print(self.commands)

    @staticmethod
    def usage_print(command):
        name = command[0]
        desc = command[2]
        usage = command[3]
        compiled = "Command: *%s*\nUsage: *%s*\n\n%s" % (name, usage, desc)
        return compiled

    def get_help(self):
        command_list = []
        for command in self.commands:

            compiled = "Usage: %s\n" \
                       "Desc: %s" % (command[3], command[2])
            command_list.append([command[0], compiled])
        return command_list

    def run_command(self, message: str):
        for command in self.commands:
            if message.startswith(self.touch_command + command[0]):
                new_message = message[len(self.touch_command + command[0]):]
                arg = new_message.split()
                print("Running command... %s\nArgs: %s" % (command[0], arg))
                if len(arg) > command[4] != -1:
                    print("Too many args for command")
                    return "`Err: Too many args`\n" + self.usage_print(command)
                if len(arg) < command[1]:
                    print("Not enough args for command")
                    return "`Err: Not enough args`\n" + self.usage_print(command)
                to_import = "from drunk_bot.command_package import %s" % command[5]
                exec(to_import)
                cmd = "%s.execute(%s)" % (command[5], str(arg))
                ret_val = eval(cmd)
                return ret_val
        return None
