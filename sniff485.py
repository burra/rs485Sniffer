#! /usr/bin/env python3
"""sniff485

Usage:
    sniff485 [-b <dur>] [-r] [<device>] [<baud>]

Options:
    -h --help    Show this screen.
    -b           Set batched burst secs (defaults to 3 secs)
    -r           Reset the position count every input burst (def'd by -b)

<device> is the /dev/XXX pathname to the RS-485 serial adapter,
        defaults to "/dev/rs485"
<baud> is the baud rate to sniff the bus at.  Defaults to 115200.

  If -r is specified, then the position offset count is reset for
  every input burst.

CLI utility to sniff bytes on a serial interface and then print
out the hex and ASCII interpretations.

Written by: Mike Petonic [2017-01-29 SUN 09:56]
"""

import serial
import time
import hexdump
import sys
from docopt import docopt

def_device = 'COM4'
def_baud = 9600

defBurstInt = 3.0           # One second default timeout

serialTimeout = 0.1           # Different than the burst


# Make this a global variable
arguments = None

# open serial


def main():
    global arguments            # Use the global so main can see it

    buff = b''
    buffpos = 0
    lasttime = time.time()

    ################################################################
    # Parse the command-line arguments provided.
    #
    # Given command: ./sniff485.py -b 12 -r
    #   arguments are:
    # {'-b': True, '-r': True, '<baud>': None, '<device>': None, '<dur>': '12'}
    #
    # Given command: ./sniff485.py -r
    #   arguments are:
    # {'-b': False, '-r': True, '<baud>': None, '<device>': None, '<dur>': None}
    ################################################################

    baud = def_baud

    s_baud = arguments['<baud>']
    if s_baud:
        try:
            baud = int(s_baud)
        except ValueError:
            print("Baud must be an INT, not <{}>".
                  format(s_baud),
                  file=sys.stderr)
            sys.exit(1)

    device = def_device
    s_device = arguments['<device>']
    if s_device:
        device = s_device
        # We'll do the open check later.
        #

    burstinterval = defBurstInt
    s_burst = arguments['-b']
    if arguments['-b']:
        try:
            burstinterval = float(arguments['<dur>'])
        except (ValueError, FloatingPointError):
            print("BurstInt must be an FLOAT, not <{}>".
                  format(s_burst),
                  file=sys.stderr)
            sys.exit(1)

    resetCount = True if arguments['-r'] else False

    ################################################################
    # Initialize the serial device
    ################################################################

    try:
        ser = serial.Serial(
            port=device,
            baudrate=baud,
            timeout=0.1         # Different than the burst interval
        )
    except IOError as e:
        print("sniff485: IO error opening <{}>: {}".
              format(device, e),
              file=sys.stderr)
        sys.exit(2)

    ################################################################
    # Enter infinite loop.  Exit with keyboard interrupt (^c)
    ################################################################

    while True:
        inp = ser.read()
        if len(inp):
            buff += inp
            lasttime = time.time()
        if ((time.time() - lasttime) > burstinterval):
            if len(buff):
                outstring = hexdump.hexdump(buff, result='return')
                print("{:08x}: {}".format(       # Don't print meaningless address
                    buffpos, outstring[10:]))
                buffpos += len(buff)
                buff = b''
                lasttime = time.time()
                if resetCount:
                    buffpos = 0
                    print("")





if __name__ == '__main__':
    arguments = docopt(__doc__, version='sniff485 v1.0')
    main()
