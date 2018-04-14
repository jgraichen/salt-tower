# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import pytest

import salt.config
import salt.loader


__root__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

__opts__ = salt.config.master_config('/dev/null')
__opts__['extension_modules'] = __root__
__opts__['log_level'] = 'debug'
__opts__['id'] = 'test_master'
__opts__['cachedir'] = 'tmp/cache'

__grains__ = salt.loader.grains(__opts__)
__opts__['grains'] = __grains__

__utils__ = salt.loader.utils(__opts__)
__salt__ = salt.loader.minion_mods(__opts__, utils=__utils__)
__renderers__ = salt.loader.render(__opts__, __salt__)
