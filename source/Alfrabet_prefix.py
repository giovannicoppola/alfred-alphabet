#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Alfred-Alphabet (Alfrabet)
# The by-prefix view: one row per prefix/modifier, one circle per letter


import sys
from Alfrabet_functions import *


query = sys.argv[1]


def main():
    fetchByPrefix()


if __name__ == '__main__':
    main ()
