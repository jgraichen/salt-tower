# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
Extended YAML renderer for salt.

For YAML usage information see :ref:`Understanding YAML <yaml>`.

Special extensions are added to

* include other render files at arbitrary positions
* include plain or binary files at arbitrary positions

"""
from __future__ import absolute_import

import copy
import io
import os

from yaml.constructor import ConstructorError
from yaml.nodes import ScalarNode, MappingNode

import salt.loader
import salt.template

from salt.utils.yamlloader import SaltYamlSafeLoader, load
from salt.utils.odict import OrderedDict

try:
    from salt.utils.files import fopen
except ImportError:
    from salt.utils import fopen


class YamletLoader(SaltYamlSafeLoader):  # pylint: disable=too-many-ancestors
    def __init__(self, stream, renderers, context=None, tmplpath=None, **_kwargs):
        SaltYamlSafeLoader.__init__(self, stream, dictclass=OrderedDict)

        if context is None:
            self.context = {}
        else:
            self.context = context

        self.tmplpath = tmplpath
        self.renderers = renderers
        self.add_constructor("!read", type(self)._yamlet_read)
        self.add_constructor("!include", type(self)._yamlet_include)

    def _yamlet_read(self, node):
        if isinstance(node, ScalarNode):
            return self._read(node.value)

        raise ConstructorError(
            None,
            None,
            f"expected a scalar node, but found {node.id}",
            node.start_mark,
        )

    def _yamlet_include(self, node):
        if isinstance(node, ScalarNode):
            return self._compile(node.value)

        if isinstance(node, MappingNode):
            return self._compile(**self.construct_mapping(node, True))

        raise ConstructorError(
            None,
            None,
            f"expected a scalar or mapping node, but found {node.id}",
            node.start_mark,
        )

    def _read(self, source):
        source = self._resolve(source)

        with fopen(source, "rb") as file:
            return file.read()

    def _compile(self, source, default="jinja|yamlet", context=None):
        source = self._resolve(source)

        ctx = copy.copy(self.context)

        if context:
            ctx.update(context)

        ctx["tmplpath"] = source
        ctx["tmpldir"] = os.path.dirname(source)

        ret = salt.template.compile_template(
            template=source,
            renderers=self.renderers,
            default=default,
            blacklist=None,
            whitelist=None,
            context=ctx,
        )

        if isinstance(ret, io.IOBase):
            ret = ret.read()

        return ret

    def _resolve(self, path):
        if self.tmplpath:
            base = os.path.dirname(self.tmplpath)

            return os.path.realpath(os.path.join(base, path))

        return path


def get_yaml_loader(**kwargs):
    def yaml_loader(stream):
        return YamletLoader(stream, **kwargs)

    return yaml_loader


def render(source, _saltenv, _sls, **kwargs):
    """
    Processes YAML data in a string or file objects.

    :rtype: A Python data structure
    """
    if not isinstance(source, str):
        source = source.read()

    return load(source, Loader=get_yaml_loader(**kwargs))
