#! /usr/bin/env python3
'''
Check a given directory against a given DAT file
'''

# imports
from gzip import open as gopen
from os.path import isdir, isfile
from pathlib import Path, PurePath
from xml.etree import ElementTree
import argparse

# parse user args
def parse_args():
    # define and parse args
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dat', required=True, type=str, help="Input DAT File (No-Intro or Redump)")
    parser.add_argument('-g', '--games', required=True, type=str, help="Input Games Folder")
    parser.add_argument('-o', '--output', required=False, type=str, default='stdout', help="Output Results (TSV)")
    parser.add_argument('--show_match', action='store_true', help="Show Matches in Output")
    parser.add_argument('--game_name', action='store_true', help="Use Game Names Instead of ROM Names")
    args = parser.parse_args()

    # check args for validity and return
    if not isfile(args.dat):
        raise ValueError("File not found: %s" % args.dat)
    if not isdir(args.games):
        raise ValueError("Folder not found: %s" % args.games)
    if (args.output != 'stdout') and (isfile(args.output) or isdir(args.output)):
        raise ValueError("Output exists: %s" % args.output)
    return args

# open file for reading/writing
def open_file(fn, mode='rt'):
    if isinstance(fn, PurePath):
        fn = str(fn.resolve()) # get absolute path as string
    if not isinstance(fn, str):
        raise ValueError("Invalid type for path (%s): %s" % (type(fn), str(fn)))
    if fn == 'stdout':
        from sys import stdout as f
    elif fn == 'stdin':
        from sys import stdin as f
    elif fn == 'stderr':
        from sys import stderr as f
    elif fn.lower().endswith('.gz'):
        f = gopen(fn, mode)
    else:
        f = open(fn, mode)
    return f

# load DAT file as list of dict
def load_dat(fn, game_name=False):
    data = list()
    with open_file(fn, 'rt') as f:
        for game in ElementTree.fromstring(f.read()).findall('game'):
            if game_name:
                if 'name' not in game.attrib:
                    raise ValueError("Invalid DAT: %s" % fn)
                curr = {'name': game.attrib['name'], 'size': sum(int(rom.attrib['size']) for rom in game.findall('rom') if 'size' in rom.attrib)}
                data.append(curr)
            else:
                for rom in game.findall('rom'):
                    if 'name' not in rom.attrib:
                        raise ValueError("Invalid DAT: %s" % fn)
                    curr = {'name': rom.attrib['name']}
                    for k in ['size', 'crc', 'md5', 'sha1', 'sha256']:
                        if k in rom.attrib:
                            curr[k] = rom.attrib[k]
                    data.append(curr)
    return data

# match ROMs from games path to DAT file
def match_roms(data, games_path):
    rom_match = {'.'.join(d['name'].split('.')[:-1]) : None for d in data}; missing = set()
    for path in games_path.rglob('*'):
        if path.is_file():
            if path.stem in rom_match and rom_match[path.stem] is None:
                rom_match[path.stem] = path
            else:
                missing.add(path)
    return rom_match, missing

# main program
def main():
    # set things up
    args = parse_args()
    dat_path = Path(args.dat).resolve()
    games_path = Path(args.games).resolve()
    out_f = open_file(args.output, 'wt')

    # check games
    data = load_dat(dat_path, game_name=args.game_name)
    rom_match, missing = match_roms(data, games_path)
    out_f.write('Database Entry: %s\tGame: %s\n' % (dat_path, games_path))
    for db_name in sorted(rom_match.keys()):
        if rom_match[db_name] is None or args.show_match:
            out_f.write('%s\t%s\n' % (db_name, rom_match[db_name]))
    for path in sorted(missing):
        out_f.write('None\t%s\n' % path)
    out_f.close()

# run tool
if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
