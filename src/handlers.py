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

"""Handlers for LaTeX commands."""

############################################################
import re
############################################################


def escape4re(string):
    return string.translate(str.maketrans({"\\": r"\\",
                                           "[": r"\[",
                                           "]": r"\]",
                                           "{": r"\{",
                                           "}": r"\}",
                                           "^": r"\^",
                                           "$": r"\$",
                                           ".": r"\."}))

############################################################


class LatexCmdHandler:
    def __init__(self):
        self._name = "CommandHandler"

    def __str__(self):
        return self._name


class LatexRegexCmdHandler(LatexCmdHandler):
    def __init__(self):
        super().__init__()
        self._pattern_optarg = "((?:\[[^\]]*\])?)"
        self._pattern_arg = "\{([^\}]*)\}"
        self._pattern_backslash = "\\\\"
        self._patterns = []
        self._regexes = []

    def _setPattern(self, pattern):
        self._pattern = pattern
        self._regex = re.compile(pattern)

    def _addPattern(self, pattern):
        self._patterns.append(pattern)
        self._regexes.append(re.compile(pattern))


class DocumentClassHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'DocumentClassHandler'
        pattern = (self._pattern_backslash + "documentclass" +
                   self._pattern_optarg + self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        cls = m.group(2)
        print("Found documentclass with name {}.".format(cls))
        cls_file = cls + '.cls'
        cls_path = env.cwd / cls_file
        if cls_path.exists():
            env.files_to_copy.append((cls_path.resolve(), cls_file))
        return (line, False)


class GraphicsPathHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'GraphicsPathHandler'
        self._pattern_arg = "\{+([^\}]*)\}+"
        pattern = (self._pattern_backslash + "graphicspath" +
                   self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        gp = m.group(1)
        print("Found graphicspath with value {}.".format(gp))
        gp_path = env.cwd / gp
        env.graphics_path = gp_path.resolve()
        # print("Setting graphics path to {}.".format(gp_path))
        return ('', False)


class InputHandler(LatexRegexCmdHandler):
    def __init__(self, inline):
        super().__init__()
        self._name = 'InputHandler'
        self._inline = inline
        pattern = (self._pattern_backslash + "(input|include)" +
                   self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        inp = m.group(2)
        print("Found input/include with value {}.".format(inp))
        input_file = inp if inp.endswith(".tex") else inp + ".tex"
        input_path = env.cwd / input_file
        inp_masked = inp.replace('/', '_')
        inp_masked_file = (inp_masked if inp_masked.endswith(".tex") else
                           inp_masked + ".tex")
        env.files_to_process.append((input_path.resolve(), "" if self._inline else inp_masked_file))
        sub = "" if self._inline else '\\\\\\1{' + inp_masked + '}'
        n_input = self._regex.sub(sub, line)
        return (None if self._inline else n_input, self._inline)


class BibliographyHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'BibliographyHandler'
        pattern = (self._pattern_backslash + "bibliography" +
                   self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        print("Found bibliography.")
        bib_file = env.main.stem + '.bbl'
        bib_path = env.cwd / bib_file
        env.files_to_copy.append((bib_path.resolve(), bib_file))
        sub = '\\\\bibliography{' + env.main.stem + '}'
        n_bib = self._regex.sub(sub, line)
        return (n_bib, False)


class IncludeGraphicsHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'IncludeGraphicsHandler'
        pattern = (self._pattern_backslash + "includegraphics" +
                   self._pattern_optarg + self._pattern_arg)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        ig = m.group(2)
        print("Found includegraphics with value {}.".format(ig))
        graphics_file = ig if ig.lower().endswith((".pdf", ".png", ".eps", ".jpg", ".jpeg")) else ig + ".pdf"
        graphics_path = env.graphics_path / graphics_file
        ig_masked = ig.replace('/', '_').replace('..', 'dd')
        graphics_file_masked = (ig_masked if ig_masked.lower().endswith((".pdf", ".png", ".eps", ".jpg", ".jpeg"))
                                else ig_masked + ".pdf")
        env.files_to_copy.append((graphics_path.resolve(),
                                  graphics_file_masked))
        sub = '\\\\includegraphics\\1{' + ig_masked + '}'
        n_ig = self._regex.sub(sub, line)
        return (n_ig, False)


class InlineCommentHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'InlineCommentHandler'
        pattern = '^([^%]*[^' + self._pattern_backslash + '])%(.*)$'
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.match(line)
        if m is None:
            return (line, False)
        sub = '\\1%'
        n_cmd = self._regex.sub(sub, line)
        return (n_cmd, False)


class LineCommentHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'LineCommentHandler'
        pattern = '^%(.*)'
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        return (None, True)


class CustomContentHandler(LatexRegexCmdHandler):
    def __init__(self, content, keep):
        super().__init__()
        self._name = 'CustomContentHandler'
        self._content = content
        self._keep = keep
        pattern = escape4re(content)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        print('Found line containing {}, {} it.'.format(
            self._content, 'keeping' if self._keep else 'removing'))
        return (line, True) if self._keep else ('', True)


class CustomUncommentHandler(LatexRegexCmdHandler):
    def __init__(self, content):
        super().__init__()
        self._name = 'CustomUncommentHandler'
        self._content = content
        pattern = escape4re(content)
        pattern = '^%(.*)' + escape4re(content)
        # print(pattern)
        self._setPattern(pattern)

    def apply(self, line, env):
        m = self._regex.match(line)
        if m is None:
            return (line, False)
        print('Found line containing {}, uncommenting it.'.format(
            self._content))
        sub = '\\1%'
        n_cmd = self._regex.sub(sub, line)
        return (n_cmd, False)


class GeneralFileHandler(LatexRegexCmdHandler):
    def __init__(self, path):
        super().__init__()
        self._name = 'GeneralFileHandler'
        pattern = escape4re(path)
        #print(pattern)
        self._setPattern(pattern)
        self._path = path
        self._masked = path.replace('/', '_')

    def apply(self, line, env):
        m = self._regex.search(line)
        if m is None:
            return (line, False)
        print("Found mentioning of path {}, will be replaced by {}.".format(
            self._path, self._masked))
        path = env.cwd / self._path
        env.files_to_process.append((path.resolve(), self._masked))
        nf = self._regex.sub(self._masked, line)
        return (nf, False)

class CommentEnvironmentHandler(LatexRegexCmdHandler):
    def __init__(self):
        super().__init__()
        self._name = 'CommentsEnvironmentHandler'
        self._addPattern("^" + self._pattern_backslash + "usepackage\{comment\}")
        self._addPattern(self._pattern_backslash + "begin\{comment\}")
        self._addPattern(self._pattern_backslash + "end\{comment\}")
        self.waitForBegin()

    def waitForBegin(self):
        self._active = False
        self._regex = self._regexes[1]

    def waitForEnd(self):
        self._active = True
        self._regex = self._regexes[2]

    def apply(self, line, env):
        m = self._regexes[0].search(line)
        if m:
            return (None, True)
        m = self._regex.search(line)
        if m is None:
            return (None, True) if self._active else (line, False)
        if self._active:
            print("Found end of comments environment.")
            self.waitForBegin()
        else:
            print("Found begin of comments environment.")
            self.waitForEnd()
        return (None, True)
