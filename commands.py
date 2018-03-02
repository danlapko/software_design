import os
import subprocess
import sys

from parser import *


def multiplexor(cmd):
    """Associates command with appropriate Command class
    cmd: string"""
    for sbcls in Command.__subclasses__():
        if sbcls.mnemonic == cmd:
            return sbcls
    Default.cmd = cmd
    return Default


class Command:
    """Base class for each command
    mnemonig: command in string"""

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

        for file in args:
            try:
                with open(file) as f:
                    for line in f:
                        print(line, end="", file=self.OutputStream)
            except FileNotFoundError:
                print("file " + file + " not found",
                      file=self.ErrorStream)

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
