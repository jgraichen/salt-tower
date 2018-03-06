# -*- coding: utf-8 -*-

import os
import pytest
import shutil
import tempfile

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


import salt.config
import salt.loader

__opts__ = salt.config.master_config(os.path.join('tests/minion.yml'))
__opts__['extension_modules'] = root
__opts__['log_level'] = 'debug'
__opts__['id'] = 'test_master'

__grains__ = salt.loader.grains(__opts__)
__opts__['grains'] = __grains__
__utils__ = salt.loader.utils(__opts__)
__salt__ = salt.loader.minion_mods(__opts__, utils=__utils__)


__renderers__ = salt.loader.render(__opts__, __salt__)


@pytest.fixture()
def tmpdir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)

class TestRenderer(object):
    @pytest.fixture(autouse=True)
    def setup(self, request, tmpdir):
        self.tmpdir = tmpdir

        if hasattr(self, 'template'):
            self.write(self.template)

    def write(self, content, path='template.sls'):
        with salt.utils.fopen(os.path.join(self.tmpdir, path), 'w') as f:
            f.write(content)

    def render(self, template='template.sls'):
        template = os.path.join(self.tmpdir, template)

        return salt.template.compile_template(
            template, __renderers__, self.default_renderer, '', '')
