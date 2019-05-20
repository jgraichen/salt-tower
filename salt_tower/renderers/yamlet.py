# -*- coding: utf-8 -*-
'''
Extended YAML renderer for salt.

For YAML usage information see :ref:`Understanding YAML <yaml>`.

Special extensions are added to

* include other render files at arbitrary positions
* include plain or binary files at arbitrary positions

'''
from __future__ import absolute_import

import io
import logging
import os
import six
import warnings

from yaml.constructor import ConstructorError
from yaml.nodes import ScalarNode, MappingNode

import salt.loader
import salt.template

from salt.utils.yamlloader import SaltYamlSafeLoader, load
from salt.utils.odict import OrderedDict
from salt.ext.six import string_types
from salt.exceptions import SaltRenderError

try:
    from salt.utils.files import fopen
except ImportError:
    from salt.utils import fopen

log = logging.getLogger(__name__)


class YamletLoader(SaltYamlSafeLoader):
    def __init__(self, stream, renderers, context={}, tmplpath=None, **kwargs):
        SaltYamlSafeLoader.__init__(self, stream, dictclass=OrderedDict)

        self.context = context
        self.tmplpath = tmplpath
        self.renderers = renderers
        self.add_constructor(u'!read', type(self)._yamlet_read)
        self.add_constructor(u'!include', type(self)._yamlet_include)

    def _yamlet_read(self, node):
        if isinstance(node, ScalarNode):
            return self._read(node.value)
        else:
            self._invalid_node(node, 'a scalar node')

    def _yamlet_include(self, node):
        if isinstance(node, ScalarNode):
            return self._compile(node.value)
        elif isinstance(node, MappingNode):
            return self._compile(**self.construct_mapping(node, True))
        else:
            self._invalid_node(node, 'a scalar or mapping node')

    def _read(self, source):
        source = self._resolve(source)

        with fopen(source, 'rb') as f:
            return f.read()

    def _compile(self, source, default='jinja|yamlet', context={}):
        source = self._resolve(source)

        context = dict(self.context, **context)
        context['tmplpath'] = source
        context['tmpldir'] = os.path.dirname(source)

        ret = salt.template.compile_template(
            template=source,
            renderers=self.renderers,
            default=default,
            blacklist=None,
            whitelist=None,
            context=context)

        if isinstance(ret, (six.StringIO, six.BytesIO, io.IOBase)):
            ret = ret.read()

        return ret

    def _resolve(self, path):
        if self.tmplpath:
            base = os.path.dirname(self.tmplpath)

            return os.path.realpath(os.path.join(base, path))

        return path

    def _invalid_node(self, node, expected):
        raise ConstructorError(
            None,
            None,
            'expected {0}, but found {1}'.format(expected, node.id),
            node.start_mark)


def get_yaml_loader(**kwargs):
    def yaml_loader(stream):
        return YamletLoader(stream, **kwargs)

    return yaml_loader


def render(source, saltenv='base', sls='', argline='', **kwargs):
    '''
    Processes YAML data in a string or file objects.

    :rtype: A Python data structure
    '''
    if not isinstance(source, string_types):
        source = source.read()

    return load(source, Loader=get_yaml_loader(**kwargs))
