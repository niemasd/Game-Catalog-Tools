#! /usr/bin/env python3
'''
Check a given directory against a given DAT file
'''

# imports
from gzip import open as gopen
from os.path import isdir, isfile
from pathlib import Path
import argparse

# parse user args
def parse_args():
    # define and parse args
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dat', required=True, type=str, help="Input DAT File (No-Intro or Redump)")
    parser.add_argument('-g', '--games', required=True, type=str, help="Input Games Folder")
    parser.add_argument('-o', '--output', required=False, type=str, default='stdout', help="Output Results (TSV)")
    args = parser.parse_args()

    # check args for validity and return
    if not isfile(args.dat):
        raise ValueError("File not found: %s" % args.dat)
    if not isdir(args.games):
        raise ValueError("Folder not found: %s" % args.games)
    if (args.output != 'stdout') and (isfile(args.output) or isdir(args.output)):
        raise ValueError("Output exists: %s" % args.output)
    return args

# main program
def main():
    # set things up
    args = parse_args()
    dat_path = Path(args.dat).absolute()
    games_path = Path(args.games).absolute()
    if args.output.lower().strip() == 'stdout':
        from sys import stdout as out_f
    elif args.output.strip().lower().endswith('.gz'):
        out_f = gopen(args.output, 'wt')
    else:
        out_f = open(args.output, 'w')

    # check games
    out_f.write('Database Entry: %s\tGame: %s\n' % (dat_path, games_path))
    pass # TODO

    # finish up
    out_f.close()

# run tool
if __name__ == "__main__":
    main()
