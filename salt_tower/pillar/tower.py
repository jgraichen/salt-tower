# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import

import collections
import copy
import logging
import os
import string
import errno

from glob import glob

import salt.loader
import salt.minion
import salt.template
import salt.ext.six as six

try:
    from salt.utils.data import traverse_dict_and_list
except ImportError:
    from salt.utils import traverse_dict_and_list

log = logging.getLogger(__name__)


if hasattr(salt.loader, 'matchers'):
    # Available since salt 2019.2
    def _match_minion_impl(tgt, opts):
        matchers = salt.loader.matchers(dict(__opts__, **opts)) # pylint: disable=no-member
        return matchers['compound_match.match'](tgt)

else:
    def _match_minion_impl(tgt, opts):
        return salt.minion.Matcher(opts, __salt__).compound_match(tgt)


def ext_pillar(minion_id, pillar, *args, **_kwargs):
    env = __opts__.get('environment', None)

    if env is None:
        env = 'base'

    tower = Tower(minion_id, env, pillar)

    for top in list(args):
        if not os.path.exists(top):
            log.warning("Tower top file `%s' does not exists", top)
            continue

        tower.run(top)

    return dict(tower)


class Tower(dict):
    def __init__(self, minion_id, env, pillar):
        super(Tower, self).__init__(pillar)

        self.env = env
        self.minion_id = minion_id

        opts = copy.copy(__opts__)
        opts['pillar'] = self

        self._renderers = salt.loader.render(opts, __salt__)
        self._formatter = Formatter(self)
        self._included = []

        if 'yamlet' in self._renderers:
            self._default_renderers = 'jinja|yamlet'
        else:
            log.warning('Yamlet renderer not available. Tower functionality will be limited.')
            self._default_renderers = 'jinja|yaml'

    def get(self, key, default=None, **kwargs):
        return traverse_dict_and_list(self, key, default, **kwargs)

    def update(self, obj, merge=True, **kwargs):
        if merge:
            return self.merge(self, obj, **kwargs)
        return super(Tower, self).update(obj)

    def merge(self, *args, **kwargs):
        return _merge(*args, **kwargs)

    def format(self, obj, *args, **kwargs):
        if isinstance(obj, collections.Mapping):
            return {k: self.format(v, *args, **kwargs) for k, v in six.iteritems(obj)}

        if isinstance(obj, list):
            return [self.format(i, *args, **kwargs) for i in obj]

        if isinstance(obj, six.string_types):
            if six.PY3 and isinstance(obj, bytes):
                return obj

            try:
                return self._formatter.format(obj, *args, **kwargs)
            except ValueError:
                return obj

        return obj

    def run(self, top):
        log.debug("Process tower top file `%s'", top)

        base = os.path.dirname(top)

        for item in self._load_top(top):
            if isinstance(item, six.string_types):
                self._load_item(base, item)

            elif isinstance(item, collections.Mapping):
                for tgt, items in six.iteritems(item):
                    if not self._match_minion(tgt):
                        continue

                    for itm in items:
                        self._load_item(base, itm)

    def _match_minion(self, tgt):
        try:
            return _match_minion_impl(tgt, {
                'grains': __grains__,
                'pillar': self,
                'id': self.minion_id
            })
        except Exception as err:
            log.exception(err)
            return False


    def _load_top(self, top):
        data = self._compile(top)

        if not isinstance(data, collections.Mapping):
            log.critical("Tower top must be a dict, but is %s.", type(data))
            return []

        if self.env not in data:
            log.warning("Tower top `%s' does not include env %s, skipping.", top, self.env)
            return []

        if not isinstance(data[self.env], list):
            log.critical("Tower top `%s' env %s must be a list, but is %s.",
                         top, self.env, type(data[self.env]))
            return []

        return data[self.env]

    def _load_item(self, base, item):
        if isinstance(item, collections.Mapping):
            self.update(item, merge=True)

        elif isinstance(item, six.string_types):
            self.load(item, base)

    def lookup(self, item, base=None, cwd=None):
        if cwd and (item.startswith('./') or item.startswith('../')):
            path = os.path.join(cwd, self.format(item))
        elif base:
            path = os.path.join(base, self.format(item))
        else:
            path = self.format(item)

        match = glob(path)

        if match:
            match = [i for i in match if os.path.isfile(i)]

        if match:
            log.debug('Found glob match: %s', match)
            return sorted(match)

        for match in [path, '{}.sls'.format(path), '{}/init.sls'.format(path)]:
            if os.path.isfile(match):
                log.debug('Found file match: %s', match)
                return [match]

        return []

    def load(self, item, base=None, cwd=None):
        for file in self.lookup(item, base, cwd):
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
            log.warning('Skipping already included file: %s', file)
            return

        if not os.path.isfile(file):
            log.warning('Skipping non-existing file: %s', file)
            return

        self._included.append(file)

        data = self._compile(file, context={'basedir': base})

        if not isinstance(data, collections.Mapping):
            log.warning('Loading %s did not return dict, but %s', file, type(data))
            return

        if 'include' in data:
            includes = data.pop('include')

            if not isinstance(includes, list):
                includes = [includes]

            for include in includes:
                self.load(include, base, cwd=os.path.dirname(file))

        self.update(data, merge=True)

    def _compile(self, template, default=None, blacklist=None, whitelist=None, context=None, **kwargs):
        if default is None:
            default = self._default_renderers

        if context is None:
            context = {}

        context['tmplpath'] = template
        context['tmpldir'] = os.path.dirname(template)
        context['minion_id'] = self.minion_id
        context['pillar'] = self
        context['tower'] = self

        def render(tmpl, renderer='text'):
            file = os.path.join(context.get('base'), tmpl)
            file = os.path.abspath(file)

            if not os.path.isfile(file):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)

            return self._compile(file, renderer, None, None, context)

        context['render'] = render

        kwargs['tower'] = context['tower']
        kwargs['minion_id'] = context['minion_id']

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

        value = self._tower.get(key, delimiter='.')

        if value is None:
            return ('{' + key + '}', None)

        return (value, None)


def _merge(tgt, *objects):
    for obj in objects:
        if isinstance(tgt, collections.Mapping):
            tgt = _merge_dict(tgt, obj)
        elif isinstance(tgt, list):
            tgt = _merge_list(tgt, obj)
        else:
            raise TypeError('Cannot merge {}'.format(type(tgt)))

    return tgt


def _merge_dict(tgt, obj):
    if not isinstance(obj, collections.Mapping):
        raise TypeError(
            'Cannot merge non-dict type, but is {}'.format(type(obj)))

    for key, val in six.iteritems(obj):
        if key in tgt:
            if isinstance(tgt[key], collections.Mapping) \
                    and isinstance(val, collections.Mapping):
                _merge(tgt[key], val)
            elif isinstance(tgt[key], list) and isinstance(val, list):
                _merge_list(tgt[key], val)
            else:
                tgt[key] = copy.deepcopy(val)
        else:
            tgt[key] = copy.deepcopy(val)

    return tgt


def _merge_list(tgt, lst, strategy='merge-last'):
    if not isinstance(lst, list):
        raise TypeError(
            'Cannot merge non-list type, but is {}'.format(type(lst)))

    if lst and isinstance(lst[0], dict) \
            and len(lst[0]) == 1 \
            and '__' in lst[0]:
        strategy = lst.pop(0)['__']

    if strategy == 'remove':
        for val in lst:
            if val in tgt:
                tgt.remove(val)

    elif strategy == 'merge-last':
        tgt.extend(copy.deepcopy(lst))

    elif strategy == 'merge-first':
        for val in lst:
            tgt.insert(0, copy.deepcopy(val))

    elif strategy == 'overwrite':
        del tgt[:]
        tgt.extend(copy.deepcopy(lst))

    else:
        raise ValueError('Unknown strategy: {}'.format(strategy))

    return tgt
