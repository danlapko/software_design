import argparse


class MyArgparser(argparse.ArgumentParser):
    def error(self, message):
        raise AttributeError(message)
