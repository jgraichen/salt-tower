# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

from __future__ import absolute_import

import os
import textwrap

import pytest

import salt.config
import salt.loader

try:
    from salt.utils.files import fopen
except ImportError:
    from salt.utils import fopen

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def opts(tmpdir):
    opts = salt.config.client_config(os.path.join(ROOT, "test/master.yml"))
    opts["cachedir"] = os.path.join(tmpdir, "cache")
    opts["pillar_roots"] = {"base": [os.path.join(ROOT, "test/fixtures/pillar")]}
    opts["grains"] = {"id": opts["id"]}
    return opts


@pytest.fixture
def renderers(opts):
    return salt.loader.render(opts, {})


@pytest.fixture
def pillars(opts):
    return salt.loader.pillars(opts, {})




@pytest.fixture
def env(tmpdir, opts, renderers, pillars):
    return Environment(tmpdir, opts, renderers, pillars)


@pytest.fixture
def render(env):
    def _render(input_data, **kwargs):
        input_data = textwrap.dedent(input_data).lstrip()

        env.write("unnamed.sls", input_data)
        return env.compile_template("unnamed.sls", **kwargs)

    return _render


class Environment:
    def __init__(self, basedir, opts, renderers, pillars):
        self._base = basedir
        self._opts = opts
        self._renderers = renderers
        self._pillars = pillars

    def setup(self, files):
        for k, v in files.items():
            self.write(k, textwrap.dedent(v).strip())

    def write(self, name, content, mode="w"):
        template = os.path.join(self._base, name)
        dirname = os.path.dirname(template)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        with fopen(template, mode) as f:
            f.write(content)

    def compile_template(self, template, default="yaml|jinja", **kwargs):
        template = os.path.join(self._base, template)

        return salt.template.compile_template(
            template=template,
            renderers=self._renderers,
            default=default,
            blacklist=None,
            whitelist=None,
            **kwargs,
        )

    def ext_pillar(self, **kwargs):
        minion_id = kwargs.pop("minion_id", self._opts["id"])
        pillar = kwargs.pop("pillar", {})
        args = kwargs.pop("args", [os.path.join(self._base, "tower.sls")])

        if isinstance(args, dict):
            return self._pillars["tower"](minion_id, pillar, **args)
        if isinstance(args, list):
            return self._pillars["tower"](minion_id, pillar, *args)
        return self._pillars["tower"](minion_id, pillar, args)
