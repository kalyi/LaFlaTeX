#!/usr/bin/env python3
# -*- coding: utf8; -*-
#
# Copyright (C) 2017 : Kathrin Hanauer
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


def processTexFile(infile, outfile, env, cmd_handlers):
    print("Processing latex file: {}".format(infile))
    with infile.open() as ifile, outfile.open('w') as ofile:
        for line in ifile:
            for h in cmd_handlers:
                line = h.apply(line, env)
            ofile.write(line)


def main():
    parser = argparse.ArgumentParser(
        description='Flatten LaTeX projects.')
    parser.add_argument('-o', '--outdir', action='store', type=str,
                        default="laflatex",
                        help='The output directory.')
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

    cmd_handlers = [handlers.DocumentClassHandler(),
                    handlers.GraphicsPathHandler(),
                    handlers.InputHandler(),
                    handlers.BibliographyHandler(),
                    handlers.IncludeGraphicsHandler(),
                    handlers.InlineCommentHandler(),
                    handlers.LineCommentHandler()]

    for t in args.texfile:
        env.main = Path(t)
        env.files_to_process.append((env.main.resolve(), t))

    while env.files_to_process:
        i, o = env.files_to_process.pop(0)
        outfile = outdir / o
        processTexFile(i, outfile, env, cmd_handlers)

    while env.files_to_copy:
        i, o = env.files_to_copy.pop(0)
        outfile = outdir / o
        shutil.copy(str(i), str(outfile))

if __name__ == "__main__":
    main()
