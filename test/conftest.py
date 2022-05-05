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
    import salt.features

    SALT_FEATURES_AVAILABLE = True
except ImportError:
    SALT_FEATURES_AVAILABLE = False


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def env(tmpdir):
    return Environment(tmpdir)


@pytest.fixture
def features():
    return {
        # This feature will become the default in the Phoshorus release.
        "enable_slsvars_fixes": True,
    }


@pytest.fixture(autouse=SALT_FEATURES_AVAILABLE)
def setup_features(features):
    # pylint: disable=no-member
    salt.features.features.setup = True
    salt.features.features.features = features


@pytest.fixture
def render(env):
    return env.render


class Environment:
    def __init__(self, tmpd):
        self.tmpd = tmpd

        self.opts = salt.config.client_config(os.path.join(ROOT, "test/master.yml"))
        self.opts["cachedir"] = os.path.join(tmpd, "cache")

        if os.getenv("USE_PACKAGE", "") == "":
            self.opts["module_dirs"] = [ROOT]

        self.opts["pillar_roots"] = {
            "base": [os.path.join(ROOT, "test/fixtures/pillar")]
        }

        self.pillar = {}
        self.grains = {"id": self.opts["id"]}
        self.opts["grains"] = self.grains
        self.opts["pillar"] = self.pillar

    def setup(self, files):
        for k, v in files.items():
            self.write(k, textwrap.dedent(v).strip())

    def write(self, name, content, mode="w"):
        template = self.tmpd / name
        template.write(content, mode, ensure=True)

    def build(self):
        return Master(self.tmpd, self.opts)

    def compile_template(self, *args, **kwargs):
        return self.build().compile_template(*args, **kwargs)

    def ext_pillar(self, *args, **kwargs):
        return self.build().ext_pillar(*args, **kwargs)

    def render(self, *args, **kwargs):
        return self.build().render(*args, **kwargs)


class Master:
    def __init__(self, tmpd, opts):
        self.tmpd = tmpd
        self.opts = opts
        self.minion_mods = salt.loader.minion_mods(self.opts)
        self.renderers = salt.loader.render(self.opts, self.minion_mods)
        self.pillars = salt.loader.pillars(self.opts, self.minion_mods)

    def compile_template(self, template, default="jinja|yaml", **kwargs):
        template = os.path.join(self.tmpd, template)
        return salt.template.compile_template(
            template,
            self.renderers,
            default,
            self.opts["renderer_blacklist"],
            self.opts["renderer_whitelist"],
            **kwargs,
        )

    def ext_pillar(self, **kwargs):
        args = kwargs.pop("args", [os.path.join(self.tmpd, "tower.sls")])
        pillar = self.opts["pillar"]
        minion_id = kwargs.pop("minion_id", self.opts["id"])

        if isinstance(args, dict):
            return self.pillars["tower"](minion_id, pillar, **args)
        if isinstance(args, list):
            return self.pillars["tower"](minion_id, pillar, *args)
        return self.pillars["tower"](minion_id, pillar, args)

    def render(self, content, mode="w", **kwargs):
        path = self.tmpd / "unnamed.sls"
        path.write(textwrap.dedent(content).lstrip(), mode, ensure=True)
        return self.compile_template(path, **kwargs)
