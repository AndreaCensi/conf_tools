  
#screen_columns = None
def get_screen_columns():
#    m = sys.modules['compmake.utils.visualization'] # FIXME
#    if m.screen_columns is None:
    max_x, max_y = getTerminalSize() #@UnusedVariable
#        m.screen_columns = max_x
    return max_x
#    return m.screen_columns

def getTerminalSize():
    '''
    max_x, max_y = getTerminalSize()
    '''
    import os
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            env = os.environ
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])

    
