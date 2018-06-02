import os
import subprocess
import sys
import shlex

import argparse

from utils import MyArgparser
from parser import *


def multiplexor(cmd):
    """Associates command with appropriate Command class
    cmd: string"""
    for sub_class in Command.__subclasses__():
        if sub_class.mnemonic == cmd:
            return sub_class
    Default.cmd = cmd
    return Default


class Command:
    """Base class for each command
    mnemonic: command in string"""

    mnemonic = ""

    def __init__(self, InputStream=sys.stdin, OutputStream=sys.stdout,
                 ErrorStream=sys.stderr, env=None):
        self.InputStream = InputStream
        self.OutputStream = OutputStream
        self.ErrorStream = ErrorStream
        self.env = env

    def exec(self, args):
        pass


class Default(Command):
    """Is selected when no other class can be choosed
    cmd: command in string"""

    cmd = ""

    def exec(self, args):
        """trying to find and execute command in subprocess
        args: command args in string"""
        try:
            command = [self.cmd]
            if args.strip():
                command.append(args.strip())

            p = subprocess.run(command,
                               env=self.env, stdout=subprocess.PIPE,
                               input=self.InputStream.read(), encoding='ascii')
            print(p.stdout, file=self.OutputStream)

        except Exception as e:
            print("command " + self.cmd + ":", e, file=self.ErrorStream)


class Echo(Command):
    """Echo command prints its args"""

    mnemonic = "echo"

    def exec(self, args):
        """executes echo
        args: command args in string"""
        args = args.strip()
        args = strip_quotes(args)

        print(args, file=self.OutputStream)


class Cat(Command):
    """Prints files content or stdin content"""

    mnemonic = "cat"

    def exec(self, args):
        """executes exec
                args: spaced list of filenames in string"""
        args = args.strip()
        args = split_by_spaces(args)
        for i in range(len(args)):
            args[i] = strip_quotes(args[i])

        for file_name in args:
            try:
                with open(file_name) as f:
                    for line in f:
                        print(line, end="", file=self.OutputStream)
            except FileNotFoundError:
                raise AttributeError("file " + file_name + " not found")

        if not args:
            for line in self.InputStream:
                print(line, end="", file=self.OutputStream)


class Exit(Command):
    """Exit command"""
    mnemonic = "exit"

    def exec(self, args):
        exit(0)


class Pwd(Command):
    """Print working directory command"""
    mnemonic = "pwd"

    def exec(self, args):
        print(os.getcwd(), file=self.OutputStream)


class Wc(Command):
    """Prints newline, word, and byte counts for each file in args"""

    mnemonic = "wc"

    def exec(self, args):
        args = args.strip()
        args = split_by_spaces(args)
        for i in range(len(args)):
            args[i] = strip_quotes(args[i])

        for file in args:
            try:
                with open(file) as f:
                    lines = f.read()
                    print(self.statistics(lines), file=self.OutputStream)
            except FileNotFoundError:
                print("file " + file + " not found",
                      file=self.ErrorStream)

        if not args:
            lines = self.InputStream.read()
            print(self.statistics(lines), file=self.OutputStream)

    def statistics(self, s):
        """returns newline, word, and byte counts for string s"""
        s = s.strip()
        lines = len(s.split("\n"))
        words = len(s.split())
        bytes = len(s.encode("utf8"))
        return lines, words, bytes


class Grep(Command):
    """`grep` command: find strings in a file.
        Usage:
            grep [-A <n>] [-i] [-w] PATTERN FILE
        Arguments:
            PATTERN     regular expression pattern to search for
            FILE    path to file where the search is performed
        Options:
            -i               ignore case when searching
            -w               search for the whole word
            -A <n>           print n lines after match [default: 0]
        """

    mnemonic = "grep"

    def exec(self, args):
        parser = MyArgparser(add_help=False, usage=argparse.SUPPRESS)
        parser.add_argument("-i", action="store_true")
        parser.add_argument("-w", action="store_true")
        parser.add_argument("-A", type=int, default=0)
        parser.add_argument("pattern", type=str)
        parser.add_argument("file", type=str, nargs='?', default="")
        parsed_args = parser.parse_args(shlex.split(args))

        num_lines_after = parsed_args.A
        need_whole_words = parsed_args.w
        need_ignore_case = parsed_args.i
        decompiled_pattern = parsed_args.pattern
        file_name = parsed_args.file

        if file_name:
            try:
                with open(file_name) as f:
                    lines = f.read().splitlines()
            except FileNotFoundError:
                raise AttributeError("file " + file_name + " not found")

        else:
            lines = self.InputStream.read().splitlines()

        re_flags = 0
        if need_ignore_case:
            re_flags |= re.IGNORECASE
        if need_whole_words:
            decompiled_pattern = '\\b{}\\b'.format(decompiled_pattern)

        compiled_pattern = re.compile(decompiled_pattern, re_flags)

        left_to_write = 0
        for i, line in enumerate(lines):
            if re.search(compiled_pattern, line):
                left_to_write = num_lines_after + 1

            if left_to_write > 0:
                print(line, file=self.OutputStream)
                left_to_write -= 1
