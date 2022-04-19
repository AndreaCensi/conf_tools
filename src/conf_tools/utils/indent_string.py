from zuper_commons.text import joinlines


def indent(s, prefix):
    lines = s.splitlines()
    lines = ["%s%s" % (prefix, line.rstrip()) for line in lines]
    return joinlines(lines)
