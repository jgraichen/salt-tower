# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import

import copy
import logging
import os
import string

from glob import glob
from functools import partial

import salt.loader
import salt.minion
import salt.template
import salt.ext.six as six


log = logging.getLogger(__name__)


def ext_pillar(minion_id, pillar, *args, **kwargs):
    env = __opts__.get('environment', None)

    if env is None:
        env = 'base'

    tower = Tower(minion_id, pillar, env)

    for top in list(args):
        if not os.path.exists(top):
            log.warn("Tower top file `{0}' does not exists".format(top))
            continue

        tower.run(top)


    return tower.format(tower.pillar)


class Tower(object):
    def __init__(self, minion_id, pillar, env, *args, **kwargs):
        self.env = env
        self.pillar = pillar
        self.minion_id = minion_id

        opts = copy.copy(__opts__)
        opts['pillar'] = self.pillar

        self._renderers = salt.loader.render(opts, __salt__)
        self._formatter = Formatter(self)
        self._included = []

        if 'yamlet' in self._renderers:
            self._default_renderers = 'jinja|yamlet'
        else:
            log.warning('Yamlet renderer not available. Tower functionality will be limited.')
            self._default_renderers = 'jinja|yaml'

    def traverse(self, key, default=None, **kwargs):
        return salt.utils.traverse_dict_and_list(self.pillar, key, default, **kwargs)

    def run(self, top):
        log.debug("Process tower top file `{0}'".format(top))

        base = os.path.dirname(top)

        for item in self._load_top(top):
            if isinstance(item, six.string_types):
                self._load_item(base, item)

            elif isinstance(item, dict):
                for tgt, items in six.iteritems(item):
                    if not self._match_minion(tgt):
                        continue

                    for i in items:
                        self._load_item(base, i)

    def _match_minion(self, tgt):
        opts = {
            'grains': __grains__,
            'pillar': self.pillar,
            'id': self.minion_id
        }

        matcher = salt.minion.Matcher(opts, __salt__)

        try:
            return matcher.compound_match(tgt)
        except Exception as e:
            log.exception(e)
            return False

    def format(self, obj, *args, **kwargs):
        if isinstance(obj, dict):
            return {k: self.format(v, *args, **kwargs) for k, v in six.iteritems(obj)}
        elif isinstance(obj, list):
            return [self.format(i, *args, **kwargs) for i in obj]
        elif isinstance(obj, six.string_types):
            return self._formatter.format(obj, *args, **kwargs)
        else:
            return obj

    def _load_top(self, top):
        data = self._compile(top)

        if not isinstance(data, dict):
            log.critical("Tower top must be a dict, but is {0}."
                .format(type(data)))
            return []

        if self.env not in data:
            log.warn("Tower top `{0}' does not include env {1}, skipping."
                .format(top, self.env))
            return []

        if not isinstance(data[self.env], list):
            log.critical("Tower top `{0}' env {1} must be a list, but is {2}."
                .format(top, self.env, type(data[self.env])))
            return []

        return data[self.env]

    def _load_item(self, base, item):
        if isinstance(item, dict):
            _merge(self.pillar, item)

        elif isinstance(item, six.string_types):
            self.load(item, base)

    def lookup(self, item, base=None):
        if base:
            path = os.path.join(base, self.format(item))
        else:
            path = self.format(item)

        match = glob(path)

        if match:
            match = [i for i in match if os.path.isfile(i)]

        if match:
            log.debug('Found glob match: {}'.format(match))
            return sorted(match)

        for match in [path, '{}.sls'.format(path), '{}/init.sls'.format(path)]:
            if os.path.isfile(match):
                log.debug('Found file match: {}'.format(match))
                return [match]

        return []

    def load(self, item, base=None):
        for file in self.lookup(item, base):
            self._load_file(file, base)

    def _load_file(self, file, base=None):
        """
        Try to load fully qualified file path as a tower data file.

        It will first check if the file has already been loaded and, if not,
        if it exist in the filesystem.

        The file will be compiled and run as a salt template and is expected
        to return a dict.

        If the dict includes an `include` item or list, these includes will
        loaded before the loaded data is merged into the current pillar.
        """
        if file in self._included:
            log.warning('Skipping already included file: {}'.format(file))
            return

        if not os.path.isfile(file):
            log.warning('Skipping non-existing file: {}'.format(file))
            return

        self._included.append(file)

        data = self._compile(file, context={'base': base})

        if not isinstance(data, dict):
            log.warning('Loading {} did not return dict, but {}'.format(file, type(data)))
            return

        if 'include' in data:
            includes = data.pop('include')

            if not isinstance(includes, list):
                includes = [includes]

            for include in includes:
                self.load(include, base)

        _merge(self.pillar, data)

    def _compile(self, template, default=None, blacklist=None, whitelist=None, context={}, **kwargs):
        if default is None:
            default = self._default_renderers

        context['minion_id'] = self.minion_id
        context['pillar'] = Pillar(self.pillar)

        kwargs['tower'] = Helper(self)
        kwargs['minion_id'] = self.minion_id
        kwargs['resolve'] = partial(os.path.join, os.path.dirname(template))

        return salt.template.compile_template(
                template=template,
                renderers=self._renderers,
                default=default,
                blacklist=blacklist,
                whitelist=whitelist,
                context=context,
                **kwargs)


class Formatter(string.Formatter):
    def __init__(self, tower):
        self._tower = tower

    def get_field(self, key, args, kwargs):
        if key in kwargs:
            return (kwargs[key], None)

        value = self._tower.traverse(key, delimiter='.')

        if value is None:
            return ('{' + key + '}', None)

        return (value, None)


class Pillar(dict):
    def get(self, key, default=None, **kwargs):
        return salt.utils.traverse_dict_and_list(self, key, default, **kwargs)


class Helper(object):
    def __init__(self, tower):
        self._tower = tower

    def traverse(self, *args, **kwargs):
        return salt.utils.traverse_dict_and_list(*args, **kwargs)

    def merge(self, *args, **kwargs):
        return _merge(*args, **kwargs)

    def format(self, *args, **kwargs):
        return self._tower.format(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._tower.traverse(*args, **kwargs)

    def __len__(self):
        return len(self._tower.pillar)

    def __iter__(self):
        return iter(self._tower.pillar)

    def __getitem__(self, key):
        return self._tower.pillar[key]

    def iteritems(self):
        return self._tower.pillar.iteritems()


def _cleanup(obj):
    if obj:
        if isinstance(obj, dict):
            obj.pop('__', None)
            for k, v in six.iteritems(obj):
                obj[k] = _cleanup(v)
        elif isinstance(obj, list) and isinstance(obj[0], dict) \
                and '__' in obj[0]:
            del obj[0]
    return obj


strategies = ('overwrite', 'merge-first', 'merge-last', 'remove')


def _merge(target, *sources, **kwargs):
    for source in sources:
        if not isinstance(source, dict):
            continue

        target = _merge_dict(target, source, **kwargs)

    return target


def _merge_dict(stack, obj, strategy='merge-last'):
    strategy = obj.pop('__', strategy)
    if strategy not in strategies:
        raise Exception('Unknown strategy "{0}", should be one of {1}'.format(
            strategy, strategies))

    if strategy == 'overwrite':
        return _cleanup(obj)
    else:
        for k, v in six.iteritems(obj):
            if strategy == 'remove':
                stack.pop(k, None)
                continue
            if k in stack:
                if strategy == 'merge-first':
                    # merge-first is same as merge-last but the other way round
                    # so let's switch stack[k] and v
                    stack_k = stack[k]
                    stack[k] = _cleanup(v)
                    v = stack_k
                if isinstance(stack[k], dict) and isinstance(v, dict):
                    stack[k] = _merge_dict(stack[k], v)
                elif isinstance(stack[k], list) and isinstance(v, list):
                    stack[k] = _merge_list(stack[k], v)
                elif type(stack[k]) != type(v):
                    log.debug('Force overwrite, types differ: '
                              '\'{0}\' != \'{1}\''.format(type(stack[k]), type(v)))
                    stack[k] = _cleanup(v)
                else:
                    stack[k] = v
            else:
                stack[k] = _cleanup(v)
        return stack


def _merge_list(stack, obj):
    strategy = 'merge-last'
    if obj and isinstance(obj[0], dict) and '__' in obj[0]:
        strategy = obj[0]['__']
        del obj[0]
    if strategy not in strategies:
        raise Exception('Unknown strategy "{0}", should be one of {1}'.format(
            strategy, strategies))
    if strategy == 'overwrite':
        return obj
    elif strategy == 'remove':
        return [item for item in stack if item not in obj]
    elif strategy == 'merge-first':
        return obj + stack
    else:
        return stack + obj

