from zuper_commons.text import joinlines


def indent(s, prefix):
    lines = s.splitlines()
    lines = ["{}{}".format(prefix, line.rstrip()) for line in lines]
    return joinlines(lines)
