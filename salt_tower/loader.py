# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import os

PKG_DIR = os.path.abspath(os.path.dirname(__file__))


def pillar_dirs():
    return [os.path.join(PKG_DIR, "pillar")]


def renderers_dirs():
    return [os.path.join(PKG_DIR, "renderers")]
