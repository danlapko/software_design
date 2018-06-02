import unittest

from io import StringIO

from parser import *
from commands import *


class ParserTestCase(unittest.TestCase):
    def test_clip_both_quotes(self):
        s1 = "'asdfsf\"asd\' \"jks jf\"ks\' '"
        ref1 = ([(0, 11), (11, 23), (23, 26)], True,
                [(0, 13), (13, 20), (20, 26)], False,
                [(0, 11), (11, 13), (13, 20), (20, 23), (23, 26)], True)

        s2 = "\"'\" '\"'  '\" \"'  \" ' '\""
        ref2 = ([(0, 4), (4, 6), (6, 9), (9, 13), (13, 22)], False,
                [(0, 2), (2, 16), (16, 22)], True,
                [(0, 2), (2, 4), (4, 6), (6, 9), (9, 13), (13, 16), (16, 22)],
                True)

        assert clip_both_quotes(s1) == ref1
        assert clip_both_quotes(s2) == ref2

    def test_strip_quotes(self):
        s1 = "'asdfsf\"asd\' \"jks jf\"ks\' '"
        ref1 = "asdfsf\"asd jks jfks "
        s2 = "\"'\""
        ref2 = "'"

        assert strip_quotes(s1) == ref1
        assert strip_quotes(s2) == ref2

    def test_split_by_spaces(self):
        s1 = "aaaa 'aaa aa 'aaa b\"bb\""
        ref1 = ['aaaa', "'aaa aa 'aaa", 'b"bb"']
        assert split_by_spaces(s1) == ref1

    def test_substitute_dollar(self):
        env = {"a": 'A',
               "b": 'B',
               "c": 'C'}
        s1 = "$abc-$a.bs'$b'$c'$____' $ $c $"
        ref1 = "-A.bs'$b'C'$____'  C "
        assert substitute_dollar(s1, env) == ref1

    def test_split_by_pipeline(s):
        s1 = "'echo' $ \"a|$sdf$a$a  $m\" | cat aa '$asd|fgf'$h | echo"
        assert split_by_pipeline(s1) == ['\'echo\' $ "a|$sdf$a$a  $m" ',
                                         " cat aa '$asd|fgf'$h ", ' echo']

    def test_block_to_cmd_args(self):
        s1 = "'ec'\"ho\" 123 $a"
        ref1 = ('echo', ' 123 $a')
        assert ref1 == block_to_cmd_args(s1)

    def test_is_assigment(self):
        s1 = "jasldj \"=b\"=2"
        ref1 = False
        assert is_assignment(s1) == ref1

        s2 = "jasldj\"=b\"=2"
        ref2 = False
        assert is_assignment(s2) == ref2

        s3 = "mmm=2"
        ref3 = ["mmm", '2']
        assert is_assignment(s3) == ref3


class CommandsTestCase(unittest.TestCase):
    def setUp(self):
        self.env = {"a": 'A',
                    "b": 'B',
                    "c": 'C',
                    "e": 'ex',
                    "i": "it"}

    def test_multiplexor(self):
        s1 = "ls"
        s2 = "echo"
        s3 = "cat"
        s4 = "exit"
        s5 = "pwd"

        assert multiplexor(s1) == Default
        assert multiplexor(s2) == Echo
        assert multiplexor(s3) == Cat
        assert multiplexor(s4) == Exit
        assert multiplexor(s5) == Pwd

    def test_Default(self):
        args = "example.txt"

        stream1 = StringIO()
        stream2 = StringIO()
        d = Default(stream1, stream2)

        d.cmd = "ls"
        d.exec(args)
        ref1 = "example.txt\n\n"

        assert stream2.getvalue() == ref1

    def test_Echo(self):
        args = "example.txt"

        stream1 = StringIO()
        stream2 = StringIO()
        d = Echo(stream1, stream2)

        d.exec(args)
        ref1 = "example.txt\n"

        assert stream2.getvalue() == ref1

    def test_Cat(self):
        args = "example.txt "

        stream1 = StringIO()
        stream2 = StringIO()
        d = Cat(stream1, stream2)

        d.exec(args)
        ref1 = "lsdjf" \
               "\njsldfja" \
               "\nf dfhjasdf " \
               "\nasdfj\n"

        assert stream2.getvalue() == ref1

    def test_Wc(self):
        args = "example.txt "

        stream1 = StringIO()
        stream2 = StringIO()
        d = Wc(stream1, stream2)

        d.exec(args)
        ref1 = '(4, 5, 31)\n'

        assert stream2.getvalue() == ref1

    def test_Grep_simple(self):
        # ----- SIMPLE ------
        stream1 = StringIO()
        stream2 = StringIO()
        d = Grep(stream1, stream2)
        args = 'so grep_example.txt '
        d.exec(args)
        ref1 = 'so much "is " a\n'
        assert ref1 == stream2.getvalue()

    def test_Grep_ignore_case(self):
        # ----- IGNORE CASE ------
        stream1 = StringIO()
        stream2 = StringIO()
        d = Grep(stream1, stream2)
        args = '-i bye grep_example.txt '
        d.exec(args)
        ref2 = 'bye world A\nBYE world\n'
        assert ref2 == stream2.getvalue()

    def test_Grep_word(self):
        # ----- WORD ------
        stream1 = StringIO()
        stream2 = StringIO()
        d = Grep(stream1, stream2)
        args = '-w fi grep_example.txt '
        d.exec(args)
        ref3 = 'for mega-grep fi\n'
        assert ref3 == stream2.getvalue()

    def test_Grep_A_opption(self):
        # ----- -A ------
        stream1 = StringIO()
        stream2 = StringIO()
        d = Grep(stream1, stream2)
        args = '-A 2 world grep_example.txt '
        d.exec(args)
        ref4 = 'bye world A\nBYE world\n1\n2\n'
        assert ref4 == stream2.getvalue()

    def test_Grep_all_flags(self):
        # ----- ALL TOGETHER ------
        stream1 = StringIO()
        stream2 = StringIO()
        d = Grep(stream1, stream2)
        args = '-i -w -A 1 "a" grep_example.txt '
        d.exec(args)
        ref5 = 'so much "is " a\n\nbye world A\nBYE world\n'
        assert ref5 == stream2.getvalue()

    def test_Grep_regexps(self):
        # ----- REGEXPS ------
        stream1 = StringIO()
        stream2 = StringIO()
        d = Grep(stream1, stream2)
        args = '"or\s.ega" grep_example.txt '
        d.exec(args)
        ref5 = 'for mega-grep fi\n'
        assert ref5 == stream2.getvalue()


if __name__ == '__main__':
    unittest.main()
