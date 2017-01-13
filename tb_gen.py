#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from vhdl import *
from vParser import *

print """
dP     dP dP     dP  888888ba  dP
88     88 88     88  88    `8b 88
88    .8P 88aaaaa88a 88     88 88
88    d8' 88     88  88     88 88
88  .d8P  88     88  88    .8P 88
888888'   dP     dP  8888888P  88888888P
ooooooooooooooooooooooooooooooooooooooooo

d888888P  888888ba   .88888.
   88     88    `8b d8'   `88
   88    a88aaaa8P' 88        .d8888b. 88d888b.
   88     88   `8b. 88   YP88 88ooood8 88'  `88
   88     88    .88 Y8.   .88 88.  ... 88    88
   dP     88888888P  `88888'  `88888P' dP    dP
oooooooooooooooooooooooooooooooooooooooooooooooo

version: 1.0.5
author: Felipe Arango, Jordi Masip, Denys Vitali
"""


def libraryTb():
    libs, uses = [], []
    for l in vhdl.getLibs():
        libs += ['library %s;' % l.getName()]
        uses += ['use %s;' % p for p in l.getPackages()]
    return "%s%s\n\n" % ("\n".join(libs), "\n".join(uses))


def entityTb():
    entities = ['entity %s_tb is\nend %s_tb;' % (a.getEntity().getName(
    ), a.getEntity().getName()) for a in vhdl.getArchitectures()]
    return "\n".join(entities) + "\n\n"


def architectureTb():
    result = ""
    for architecture in vhdl.getArchitectures():
        entity = architecture.getEntity()
        result += 'architecture behav of %s_tb is\n\tcomponent my_%s\n' % (
            entity.getName(), entity.getName())
        result += portsTb() + dutSignalsTb() + dutTb() + clockTb()
        result += '\n\t-- Your process goes here:\nend behav;'
    return result


def portsTb():
    result = '\tport ('
    for arch in vhdl.getArchitectures():
        ent = arch.getEntity()
        ports = ['\t{0} : {1} {2};\n'.format(
            p.getName(), p.getPortType(), p.getType()) for p in ent.getPorts().values()]
        result += "\t\t".join(ports)[:-2] + ');\n\tend component;'
    return result


def dutSignalsTb():
    result = ""
    for arch in vhdl.getArchitectures():
        e = arch.getEntity()
        result += '\n\tfor dut : my_%s use entity work.%s;\n\n' % (
            e.getName(), e.getName())
        result += "\n".join(['\tsignal t_%s : %s;' %
                             (p.getName(), p.getType()) for p in e.getPorts().values()])
        result += '\n\n\tbegin\n'
    return result


def dutTb():
    result = ""
    for architecture in vhdl.getArchitectures():
        entity = architecture.getEntity()
        result += '\tdut: my_%s port map (\n' % entity.getName()
        for p in entity.getPorts().values():
            result += '\t\t%s => t_%s,\n' % (p.getName(), p.getName())
        result = result[:-2] + ");\n"
    return result


def clockTb():
    while True:
        clk = raw_input('Do you want to generate a clock? (y/n) [n]: ').lower()
        clk = "n" if clk == "" else clk
        if clk != 'y' and clk != 'n':
            print 'Error: invalid option'
            continue
        elif clk == 'y':
            while True:
                try:
                    clk_freq = float(input("Input the frequency (Hz): "))
                    half_period = (1 / clk_freq) / 2. * 10**9
                    if clk_freq > 0:
                        break
                except Exception as e:
                    print e
                    print "Error: invalid frequency"

            while True:
                try:
                    n_times = int(input("How many oscillations do you want? ")) * 2
                    if n_times > 0:
                        break
                except Exception:
                    pass
                print "Error: invalid number of oscillations"

            return "\tclk_process: process\n\tbegin\n\t\tt_clk <= '0';\n\t\twait for %.8f ns;\n\t\tfor i in 1 to %i loop\n\t\t\tt_clk <= not t_clk;\n\t\t\twait for %.8f ns;\n\t\tend loop;\n\t\twait;\n\tend process clk_process;" % (half_period, n_times, half_period)
        else:
            return ""

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Error: you have to specify a .vhd/.vhdl file"
        sys.exit(1)

    vhdl_filename = sys.argv[1].split('.')

    if vhdl_filename[-1] != 'vhd' and vhdl_filename[-1] != 'vhdl':
        print 'Error: the extension has to be .vhd or .vhdl'
        print vhdl_filename[-1]
        sys.exit(1)

    # VHDL_tb filename
    vhdl_filename = ".".join(vhdl_filename[:-1]) + '_tb.vhdl'

    # VHDL content
    vhd_file = read_file(sys.argv[1])

    # Creating VHDL obj
    vhdl = VHDL()
    [vhdl.addLibrary(l) for l in getLibs(vhd_file)]
    [vhdl.setEntity(e) for e in getEntities(vhd_file)]

    # Get each entity in 'vhdl' and adds each architecture in 'vhdl'
    for entity in vhdl.getEntities():
        arch = getArchitectureOfEntity(vhd_file, entity)
        if arch != "":
            vhdl.setArchitecture(arch)

    # Write to file
    try:
        write_file(vhdl_filename, libraryTb() +
                   entityTb() + architectureTb() + "\n\0")
        print '\nThe file "%s" has been succesfully created' % vhdl_filename
    except Exception as e:
        print "Error: Unable to create file '%s'" % vhdl_filename
