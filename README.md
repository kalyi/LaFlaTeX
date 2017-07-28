# LaFlaTeX
Flatten your LaTeX projects.

## What it does
Many people (including me) prefer to organize their latex projects using different subdirectories.
For submission, however, the project is often required to have a flat structure.

LaFlaTeX starts from your main LaTeX file(s), copies each along with all referenced files
to a new directory, and adapts the references to the new flat structure.
It also removes comments from the sources as well as lines containing one of
a set of specifiable strings (such as "remove for submission").
In case that you use a custom class file that is located at the root of your project,
it tries to detect that and also copies the class file.

It currently supports the following LaTeX commands:
``\documentclass``, ``\include``, ``\input``, ``\graphicspath``, and ``\includegraphics``.

## How to use
```
$ ./laflatex.py -h
usage: laflatex.py [-h] [-o OUTDIR] [-r STRING] [texfile [texfile ...]]

Flatten LaTeX projects.

positional arguments:
  texfile               The main LaTeX file.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTDIR, --outdir OUTDIR
                        The output directory.
  -r STRING, --remove STRING
                        Remove lines containing <STRING>.
```
