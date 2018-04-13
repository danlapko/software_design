import os
import subprocess
import sys
import pathlib

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

        if not args:
            common_args = self.InputStream.read()
            common_args = common_args.split('\n')
            # убираем последний пустой элемент (который создал сплит '\n')
            common_args = common_args[:-1]
        else:
            common_args = args

        for file in common_args:
            try:
                with open(file) as f:
                    lines = f.read()
                    print(self.statistics(lines), file=self.OutputStream)
            except FileNotFoundError:
                print("file " + file + " not found",
                      file=self.ErrorStream)


    def statistics(self, s):
        """returns newline, word, and byte counts for string s"""
        s = s.strip()
        lines = len(s.split("\n"))
        words = len(s.split())
        bytes = len(s.encode("utf8"))
        return lines, words, bytes


class Ls(Command):
    """ Print files in current directory """

    mnemonic = "ls"

    def exec(self, args):
        args = args.strip()
        args = split_by_spaces(args)
        for i in range(len(args)):
            args[i] = strip_quotes(args[i])

        path_base = str(os.getcwd())
        if args != []:
            for file in args:
                path = path_base + "/" + str(file)

                files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

                for i in files:
                    print(i, file=self.OutputStream)
        else:
            path = path_base
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

            for i in files:
                print(i, file=self.OutputStream)


class Cd(Command):
    """ Change current directory """

    mnemonic = "cd"

    def exec(self, args):
        args = args.strip()
        args = split_by_spaces(args)
        for i in range(len(args)):
            args[i] = strip_quotes(args[i])

        print(args)

        if len(args) == 0:
            new_dir = pathlib.Path.home()
        elif len(args) == 1:
            new_dir = pathlib.Path(args[0])
        else:
            print("Too many arguments in cd command", file=self.ErrorStream)

        os.chdir(new_dir)
