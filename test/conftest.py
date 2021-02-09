# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

from __future__ import absolute_import

import os
import shutil
import tempfile
import textwrap

import pytest

import salt.config
import salt.loader

try:
    from salt.utils.files import fopen
except ImportError:
    from salt.utils import fopen

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

__opts__ = salt.config.client_config(os.path.join(ROOT, "test/master.yml"))
__opts__["cachedir"] = os.path.join(ROOT, "tmp/cache")

__grains__ = salt.loader.grains(__opts__)
__opts__["grains"] = __grains__
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


@pytest.fixture
def render(env):
    def _render(input_data, **kwargs):
        input_data = textwrap.dedent(input_data).lstrip()

        env.write('unnamed.sls', input_data)
        return env.compile_template('unnamed.sls', **kwargs)

    return _render


class Environment(object):
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def setup(self, files):
        for k, v in files.items():
            self.write(k, textwrap.dedent(v).strip())

    def write(self, name, content, mode="w"):
        template = os.path.join(self.tmpdir, name)
        dirname = os.path.dirname(template)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        with fopen(template, mode) as f:
            f.write(content)

    def compile_template(self, template, default="yaml|jinja", **kwargs):
        template = os.path.join(self.tmpdir, template)

        return salt.template.compile_template(
            template=template,
            renderers=__renderers__,
            default=default,
            blacklist=None,
            whitelist=None,
            **kwargs,
        )

    def ext_pillar(self, **kwargs):
        minion_id = kwargs.pop("minion_id", __opts__["id"])
        pillar = kwargs.pop("pillar", {})
        args = kwargs.pop("args", [os.path.join(self.tmpdir, "tower.sls")])

        if isinstance(args, dict):
            return __pillars__["tower"](minion_id, pillar, **args)
        if isinstance(args, list):
            return __pillars__["tower"](minion_id, pillar, *args)
        return __pillars__["tower"](minion_id, pillar, args)
