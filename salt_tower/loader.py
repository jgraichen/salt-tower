# -*- coding: utf-8 -*-

import os

PKG_DIR = os.path.abspath(os.path.dirname(__file__))


def pillar_dirs():
    yield os.path.join(PKG_DIR, 'pillar')

def renderers_dirs():
    yield os.path.join(PKG_DIR, 'renderers')
