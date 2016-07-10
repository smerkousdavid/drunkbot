
def execute(args: list):
    try:
        sums = 0
        for arg in args:
            sums += float(arg)
        return "Total sum is: %s" % str(sums)
    except (TypeError, IndexError, AssertionError):
        return "Values are not summable"
