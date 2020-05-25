#!/usr/bin/env python3
# -*- coding: utf8; -*-
#
# Copyright (C) 2017-2018 : Kathrin Hanauer
#
# This file is part of LaFlaTeX.
#
# LaFlaTeX is free software: you can redistribute it and/or modify
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""LaFlaTeX - Flatten your LaTeX projects."""

###############################################################################

import argparse
from pathlib import Path
import handlers
import shutil

###############################################################################

###############################################################################


class Environment:
    pass

def processTexFileHandle(infile, ofile, env, cmd_handlers, inline_files):
    print("Processing latex file: {}".format(infile))
    with infile.open() as ifile:
        for line in ifile:
            for h in cmd_handlers:
                line, stop = h.apply(line, env)
                if stop:
                    break
            ofile.write(line)
            if inline_files:
                while env.files_to_process:
                    i, o = env.files_to_process.pop(0)
                    processTexFileHandle(i, ofile, env, cmd_handlers, inline_files)

def processTexFile(infile, outfile, env, cmd_handlers, inline_files):
    print("Processing latex file: {}".format(infile))
    with outfile.open('w') as ofile:
        processTexFileHandle(infile, ofile, env, cmd_handlers, inline_files)


def main():
    parser = argparse.ArgumentParser(
        description='Flatten LaTeX projects.')
    parser.add_argument('-o', '--outdir', action='store', type=str,
                        default="laflatex",
                        help='The output directory.')
    parser.add_argument('-r', '--remove', action='append', type=str,
                        metavar='STRING', default=list(),
                        help='Remove lines containing <STRING>.')
    parser.add_argument('-k', '--keep', action='append', type=str,
                        metavar='STRING', default=list(),
                        help='Keep lines containing <STRING>.')
    parser.add_argument('-i', '--inline', action='store_true',
                         default=False,
                        help='Keep lines containing <STRING>.')
    parser.add_argument('texfile', nargs='*', type=str,
                        help='The main LaTeX file. ')
    args = parser.parse_args()

    env = Environment()
    env.cwd = Path('.')
    env.files_to_copy = []
    env.files_to_process = []
    env.graphics_path = env.cwd

    outdir = Path(args.outdir)
    if not outdir.exists():
        outdir.mkdir()
    outdir = outdir.resolve()

    cmd_handlers = [
        handlers.InlineCommentHandler(),
        handlers.LineCommentHandler(),
        handlers.DocumentClassHandler(),
        handlers.GraphicsPathHandler(),
        handlers.InputHandler(args.inline),
        handlers.BibliographyHandler(),
        handlers.IncludeGraphicsHandler()
    ]

    for custom_str in args.keep:
        cmd_handlers.insert(0, handlers.CustomContentHandler(custom_str, True))

    for custom_str in args.remove:
        cmd_handlers.insert(0, handlers.CustomContentHandler(custom_str, False))

    for t in args.texfile:
        env.main = Path(t)
        env.files_to_process.append((env.main.resolve(), t))

    while env.files_to_process:
        i, o = env.files_to_process.pop(0)
        outfile = outdir / o
        processTexFile(i, outfile, env, cmd_handlers, args.inline)

    while env.files_to_copy:
        i, o = env.files_to_copy.pop(0)
        outfile = outdir / o
        try:
            shutil.copy(str(i), str(outfile))
        except IOError as e:
            print("Could not copy file {} to {}: {}".format(str(i), str(outfile), e))

if __name__ == "__main__":
    main()
