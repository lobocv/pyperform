__author__ = 'calvin'

import sys
import re
from math import log10

if sys.version[0] == '3':
    import io as StringIO               # Python 3.x
else:
    import cStringIO as StringIO        # Python 2.x
    range = xrange


classdef_regex = re.compile(r"\S*def .*#!|class .*#!")
tagged_line_regex = re.compile(r".*#!")


def convert_time_units(t):
    """ Convert time in seconds into reasonable time units. """
    order = log10(t)
    if -9 < order < -6:
        time_units = 'ns'
        factor = 1000000000
    elif -6 < order < -3:
        time_units = 'us'
        factor = 1000000
    elif -3 <= order < -1:
        time_units = 'ms'
        factor = 1000.
    elif -1 <= order:
        time_units = 's'
        factor = 1
    return "{:.3f} {}".format(factor * t, time_units)


def globalize_indentation(src):
    """ Strip the indentation level so the code runs in the global scope. """
    lines = src.splitlines()
    indent = len(lines[0]) - len(lines[0].strip(' '))
    func_src = ''
    for ii, l in enumerate(src.splitlines()):
        line = l[indent:]
        func_src += line + '\n'
    return func_src


def remove_decorators(src):
    """ Remove decorators from the source code """
    src = src.strip()
    src_lines = src.splitlines()
    multi_line = False
    n_deleted = 0
    for n in range(len(src_lines)):
        line = src_lines[n - n_deleted].strip()
        if (line.startswith('@') and 'Benchmark' in line) or multi_line:
            del src_lines[n - n_deleted]
            n_deleted += 1
            if line.endswith(')'):
                multi_line = False
            else:
                multi_line = True
    setup_src = '\n'.join(src_lines)
    return setup_src


def get_tagged_imports(fp):
    imports = []
    inside_def = False
    def_lines = []
    def_indent = 0
    with open(fp, 'r') as f:
        lastLine = f.readline()
        for line in f:

            tagged_class_or_def = re.findall(classdef_regex, lastLine)
            tagged_line = re.findall(tagged_line_regex, lastLine)

            # Find the indentation level of the function/class definition and capture all source code lines
            # until we get a line that is the same indentation level (end of function/class definition).
            if tagged_class_or_def or inside_def:
                if tagged_class_or_def and def_lines:
                    imports.append(''.join(def_lines))
                    def_lines = []
                    inside_def = False

                if inside_def:
                    # For lines within the definition
                    indent = len(lastLine) - len(lastLine.lstrip(' '))
                    if indent == def_indent and lastLine != '\n':
                        imports.append(''.join(def_lines))
                        def_lines = []
                        inside_def = False
                        def_indent = 0
                        if tagged_line:
                            imports.append(lastLine)
                    else:
                        if lastLine != '\n':
                            def_lines.append(lastLine)
                else:
                    # For the definition line
                    inside_def = True
                    def_indent = len(lastLine) - len(lastLine.lstrip(' '))
                    def_lines.append(lastLine)
            elif tagged_line:
                imports.append(lastLine)

            lastLine = line

    # Examine the last line
    tagged_line = re.findall(tagged_line_regex, lastLine)
    if inside_def:
        def_lines.append(line)
        imports.append(''.join(def_lines))
    elif tagged_line:
        imports.append(line)

    src = '\n'.join(imports) + '\n'
    return src


def generate_call_statement(func, is_class_method, *args, **kwargs):
    # Create the call statement
    if is_class_method:
        stmt = 'instance.' + func.__name__ + '('
    else:
        stmt = func.__name__ + '('
    for arg in args:
        stmt += arg.__repr__() + ', '
    for kw, val in kwargs.items():
        stmt += '{0}={1}, '.format(kw, val.__repr__())
    stmt = stmt.strip(', ')
    stmt += ')'
    return stmt
