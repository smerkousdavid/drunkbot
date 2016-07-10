from discord import Client


def execute(args: list):
    try:
        sums = float(args[0])
        for arg in range(1, len(args)):
            sums -= float(args[arg])
        return "Total sub is: %s" % str(sums)
    except (TypeError, IndexError, AssertionError):
        return "Values are not subtractable"
