# noinspection PyBroadException
def execute(args: list):
    try:
        equal = ' '.join(args).replace('\n', '').strip().replace('^', '**')
        evaled = eval(equal)
        return "Math Output: %s" % str(evaled)
    except Exception as err:
        try:
            return "Couldn't math that operation... %s" % str(err.args[0])
        except Exception:
            return "Couldn't math that operation..."
