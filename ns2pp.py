#!/usr/bin/env python

"""ns2pp - ns-2 Python Parser
Script to generate bandwidth data from 'ns' trace files.
Run with --help/-h for info on usage.

ns website: http://www.isi.edu/nsnam/ns/
"""

#
# ns2pp - NS2 Python Parser
# Copyright (C) 2015  Ricardo Oliveira {rgoliveira@inf.ufrgs.br}
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import re
import argparse
from datetime import datetime

argp = argparse.ArgumentParser(
    description='ns2pp - ns-2 Python Parser.\n\n' +
                '- For each flow-node pair, a .DAT file will be generated.\n' +
                '- A gnuplot script will be generated ready to plot those .DAT ' +
                  'files.',
    epilog='ns2pp Copyright (C) 2015 Ricardo Oliveira {rgoliveira@inf.ufrgs.br}\n' +
           'This program comes with ABSOLUTELY NO WARRANTY.\n' +
           'This is free software, and you are welcome to redistribute it\n' +
           'under certain conditions.\n' +
           'See <http://www.gnu.org/licenses/> for more information.\n',
    usage="%(prog)s <tracefile> [options]",
    formatter_class=argparse.RawDescriptionHelpFormatter)
argp.add_argument('tracefile',
        type=argparse.FileType('r'),
        help="Ns2 trace file to be parsed")
argp.add_argument('-f',
        metavar='fid',
        type=int,
        nargs='+',
        help="Flow ids (if none is given, all will be generated)")
argp.add_argument('-n',
        metavar='node',
        type=int,
        nargs='+',
        help="Node ids (if none is given, all will be generated)")
argp.add_argument('-t',
        type=str,
        choices=['r','d','+','-'],
        default='r',
        help="Event type (default: r)")
argp.add_argument('-p',
        metavar="prefix",
        type=str,
        default=datetime.now().strftime("%Y%m%d-%H%M"),
        help="Prefix to be used in all output files (default: current time)")

if len(sys.argv) < 2:
    argp.print_help()
    exit(1)

args = argp.parse_args()

def get_output_filename(flow, node):
    """Generate .DAT file name based on arguments and the flow-node pair"""
    return "%s_%s_flow-%d_node-%s.dat" % (args.p, args.t,
            int(flow), int(node))

TRFIELD_EVENT    = 0
TRFIELD_TIME     = 1
TRFIELD_FROMNODE = 2
TRFIELD_TONODE   = 3
TRFIELD_PKTTYPE  = 4
TRFIELD_PKTSIZE  = 5
TRFIELD_FLAGS    = 6
TRFIELD_FLOWID   = 7
TRFIELD_SRCADDR  = 8
TRFIELD_DSTADDR  = 9
TRFIELD_SEQ      = 10
TRFIELD_PKTID    = 11

f = args.tracefile.read().splitlines()

# get only the desired events
event_list = [t for t in f if re.search('^%s'%args.t, t)]
if not event_list:
    print ""
    print "There's no event for these arguments:"
    print "    --flowid    : %s" % str(args.f or "not used")
    print "    --nodeid    : %s" % str(args.n or "nor used")
    print "    --eventtype : %s" % str(args.t)
    print ""

# for each flow-node pair, store...
time_control = {}      # current point in time (second)
bandwidth_control = {} # bandwidth since last point in time
data = {}              # every time and bandwidth values (for the .DAT files)

# main loop - process the events
for event_str in event_list:
    event = re.split('\s', event_str)
    flow, node = int(event[TRFIELD_FLOWID]), int(event[TRFIELD_TONODE])

    # filter (or not) flows and/or nodes
    allow_flow = (not args.f) or (flow in args.f)
    allow_node = (not args.n) or (node in args.n)

    if (allow_flow and allow_node):
        cur_bw = bandwidth_control.get( (flow,node), 0.0 )
        packet_size = float(event[TRFIELD_PKTSIZE]) * 8.0 # packet size in bits
        bandwidth_control[ (flow,node) ] = cur_bw + packet_size

        cur_time = time_control.get( (flow,node) , 0.0)
        if (float(event[TRFIELD_TIME]) >= cur_time + 1.0): # 1s elapsed?
            if not data.get( (flow,node) ):
                data[ (flow,node) ] = []

            data[(flow,node)].append(
                (
                  time_control.get( (flow,node) , 0.0 ),
                  bandwidth_control[ (flow,node) ]/1000000.0) # Mbits
                )

            time_control[ (flow,node) ] = cur_time + 1.0
            bandwidth_control[ (flow,node) ] = 0.0

# .DAT files generation
for key, value in data.iteritems():
    out = open(get_output_filename(key[0], key[1]), 'w')
    for v in value:
        out.write('{:}\t{:}\n'.format(v[0], v[1]))
    out.close()

# gnuplot script generation
gp = open(args.p + '_plot.gp', 'w')
gp.write("# gnuplot script auto generated by %s\n"%os.path.basename(__file__))
gp.write("set grid\n")
gp.write("set style data lines\n")
gp.write("do for [i=1:%d] { set style line i linewidth 2 }\n" % len(data))
gp.write("set ylabel \"Bandwidth (Mbps)\"\n")
gp.write("set xlabel \"Time (s)\"\n")
gp.write("plot \\\n")
i = 0
for key in data:
    i += 1
    gp.write("    \"{filename}\" title \"{label}\" ls {linestyle}".format(
             filename=get_output_filename(key[0], key[1]),
             label="Flow %d Node %d" % (key[0], key[1]),
             linestyle=i))
    if (i < len(data)):
        gp.write(", \\\n")
    else:
        gp.write("\n")
gp.write("pause -1")
print "Done!"
