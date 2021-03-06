#!/home/danila/apps/anaconda3/bin/python3.6
from io import StringIO

from commands import *

envs = dict()


def loop():
    """Main interpreter loop"""
    envs = dict()
    while True:
        line = input(">")
        try:
            process(line, envs)
        except AttributeError as e:
            print(e)


def process(line, envs):
    """Processes each incoming of interpreter
    line: incoming line
    envs: dict of environment variables
    """
    line = substitute_dollar(line, envs)
    blocks = split_by_pipeline(line)

    stream2 = StringIO("")
    for i, block in enumerate(blocks):

        assig = is_assignment(block)
        if assig:
            envs[assig[0]] = assig[1]
            continue

        cmd, args = block_to_cmd_args(block)
        cls = multiplexor(cmd)
        if cls:
            stream1 = stream2
            stream2 = StringIO("")
            execer = cls(InputStream=stream1, OutputStream=stream2,
                         env=envs)
            execer.exec(args)
            stream2.seek(0)

    print(stream2.getvalue())


# test_s = "'echo' $ \"a|$sdf$a$a  $m\" | cat aa '$asd|fgf'$h | echo $abcde'a$\"sd\"f' | pwd 'asdfasd' | cat example.txt"
# test_s = "echo 3 | cat | ls|echo $a|pwd | cat | cat |cat|cat"
# test_s = 'echo 123 | wc'
if __name__ == "__main__":
    loop()
