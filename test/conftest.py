# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import pytest
import shutil
import six
import tempfile
import textwrap

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


import salt.config
import salt.loader

__opts__ = salt.config.client_config(os.path.join(root, 'test/master.yml'))
__opts__['extension_modules'] = root
__opts__['cachedir'] = os.path.join(root, 'tmp/cache')

__grains__ = salt.loader.grains(__opts__)
__opts__['grains'] = __grains__
__utils__ = salt.loader.utils(__opts__)
__salt__ = salt.loader.minion_mods(__opts__, utils=__utils__)


__renderers__ = salt.loader.render(__opts__, __salt__)
__pillars__ = salt.loader.pillars(__opts__, __salt__)


@pytest.fixture()
def tmpdir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)


@pytest.fixture
def env(tmpdir):
    return Environment(tmpdir)


class Environment(object):
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def setup(self, files):
        for k, v in six.iteritems(files):
            self.write(k, textwrap.dedent(v).strip())

    def write(self, name, str):
        template = os.path.join(self.tmpdir, name)
        dirname = os.path.dirname(template)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        with salt.utils.fopen(template, 'w') as f:
            f.write(str)

    def compile_template(self, template, default='yaml|jinja', **kwargs):
        template = os.path.join(self.tmpdir, template)

        return salt.template.compile_template(
            template=template,
            renderers=__renderers__,
            default=default,
            blacklist=None,
            whitelist=None,
            **kwargs)

    def ext_pillar(self, **kwargs):
        minion_id = kwargs.pop('minion_id', __opts__['id'])
        pillar = kwargs.pop('pillar', {})
        args = kwargs.pop('args', [os.path.join(self.tmpdir, 'tower.sls')])

        if isinstance(args, dict):
            return __pillars__['tower'](minion_id, pillar, **args)
        elif isinstance(args, list):
            return __pillars__['tower'](minion_id, pillar, *args)
        else:
            return __pillars__['tower'](minion_id, pillar, args)
