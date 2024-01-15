from typing import Literal, List, Union, TYPE_CHECKING
from types import SimpleNamespace
import logging
import argparse
import sys
import time

from line_protocol.protocol import LineMaster

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    parser.add_argument('--port', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--dump-traffic')
    args = parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())
