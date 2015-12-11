# **ns2pp** - ns-2 Python Parser

Parser to generate bandwidth data from [ns-2](http://www.isi.edu/nsnam/ns/) trace files.

---
```
usage: ns2pp.py <tracefile> [options]

ns2pp - ns-2 Python Parser.

- For each flow-node pair, a .DAT file will be generated.
- A gnuplot script will be generated ready to plot those .DAT files.

positional arguments:
  tracefile           Ns2 trace file to be parsed

optional arguments:
  -h, --help          show this help message and exit
  -f fid [fid ...]    Flow ids (if none is given, all will be generated)
  -n node [node ...]  Node ids (if none is given, all will be generated)
  -t {r,d,+,-}        Event type (default: r)
  -p prefix           Prefix to be used in all output files (default: current
                      time)

ns2pp Copyright (C) 2015 Ricardo Oliveira {rgoliveira@inf.ufrgs.br}
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
See <http://www.gnu.org/licenses/> for more information.
```

---

### Examples:

- Generate data for all received packets:  
`python ns2pp.py tracefile.tr`

- Generate data for all dropped packets:  
`python ns2pp.py tracefile.tr -t d`

- Generate data for dropped packets, only when `flow id in [1, 3]` and `node id in [2, 5]`:  
`python ns2pp.py tracefile.tr -f 1 3 -n 2 5 -t d`
---
