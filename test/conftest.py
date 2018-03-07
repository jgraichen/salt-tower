# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import pytest
import shutil
import tempfile

import salt.utils
import salt.template

from test.salt import __renderers__


@pytest.fixture
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

    def write(self, name, str):
        template = os.path.join(self.tmpdir, name)

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
