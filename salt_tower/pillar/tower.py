# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""

"""
from __future__ import absolute_import

import copy
import errno
import logging
import os
import string

from glob import glob

import salt.loader
import salt.minion
import salt.template

try:
    from salt.utils.data import traverse_dict_and_list
except ImportError:
    from salt.utils import traverse_dict_and_list

LOGGER = logging.getLogger(__name__)


if hasattr(salt.loader, "matchers"):
    # Available since salt 2019.2
    def _match_minion_impl(tgt, opts):
        matchers = salt.loader.matchers(
            dict(__opts__, **opts)
        )  # pylint: disable=no-member
        return matchers["compound_match.match"](tgt)


else:

    def _match_minion_impl(tgt, opts):
        return salt.minion.Matcher(opts, __salt__).compound_match(tgt)


def ext_pillar(minion_id, pillar, *args, **_kwargs):
    env = __opts__.get("environment", None)

    if env is None:
        env = "base"

    tower = Tower(minion_id, env, pillar)

    for top in list(args):
        if not os.path.exists(top):
            LOGGER.warning("Tower top file `%s' does not exists", top)
            continue

        tower.run(top)

    return dict(tower)


class Tower(dict):
    def __init__(self, minion_id, env, pillar):
        super(Tower, self).__init__(pillar)

        self.env = env
        self.minion_id = minion_id

        opts = copy.copy(__opts__)
        opts["pillar"] = self

        self._renderers = salt.loader.render(opts, __salt__)
        self._formatter = Formatter(self)
        self._included = []

        if "yamlet" in self._renderers:
            self._default_renderers = "jinja|yamlet"
        else:
            LOGGER.warning(
                "Yamlet renderer not available. Tower functionality will be limited."
            )
            self._default_renderers = "jinja|yaml"

    def get(self, key, default=None, **kwargs):
        return traverse_dict_and_list(self, key, default, **kwargs)

    def update(self, obj, merge=True, **kwargs):
        if merge:
            return self.merge(self, obj, **kwargs)
        return super(Tower, self).update(obj)

    def merge(self, *args, **kwargs):
        return _merge(*args, **kwargs)

    def format(self, obj, *args, **kwargs):
        if isinstance(obj, dict):
            return {k: self.format(v, *args, **kwargs) for k, v in obj.items()}

        if isinstance(obj, list):
            return [self.format(i, *args, **kwargs) for i in obj]

        if isinstance(obj, bytes):
            return obj

        if isinstance(obj, str):
            try:
                return self._formatter.format(obj, *args, **kwargs)
            except ValueError:
                return obj

        return obj

    def run(self, top):
        LOGGER.debug("Process tower top file `%s'", top)

        base = os.path.dirname(top)

        for item in self._load_top(top, base):
            if isinstance(item, str):
                self._load_item(base, item)

            elif isinstance(item, dict):
                for tgt, items in item.items():
                    if not self._match_minion(tgt):
                        continue

                    for itm in items:
                        self._load_item(base, itm)

    def _match_minion(self, tgt):
        try:
            return _match_minion_impl(
                tgt, {"grains": __grains__, "pillar": self, "id": self.minion_id}
            )
        except Exception as err:
            LOGGER.exception(err)
            return False

    def _load_top(self, top, base):
        data = self._compile(top, context={"basedir": base})

        if not isinstance(data, dict):
            LOGGER.critical("Tower top must be a dict, but is %s.", type(data))
            return []

        if self.env not in data:
            LOGGER.warning(
                "Tower top `%s' does not include env %s, skipping.", top, self.env
            )
            return []

        if not isinstance(data[self.env], list):
            LOGGER.critical(
                "Tower top `%s' env %s must be a list, but is %s.",
                top,
                self.env,
                type(data[self.env]),
            )
            return []

        return data[self.env]

    def _load_item(self, base, item):
        if isinstance(item, dict):
            self.update(item, merge=True)

        elif isinstance(item, str):
            self.load(item, base)

    def lookup(self, item, base=None, cwd=None):
        if cwd and (item.startswith("./") or item.startswith("../")):
            path = os.path.join(cwd, self.format(item))
        elif base:
            path = os.path.join(base, self.format(item))
        else:
            path = self.format(item)

        match = glob(path)

        if match:
            match = [i for i in match if os.path.isfile(i)]

        if match:
            LOGGER.debug("Found glob match: %s", match)
            return sorted(match)

        for match in [path, f"{path}.sls", f"{path}/init.sls"]:
            if os.path.isfile(match):
                LOGGER.debug("Found file match: %s", match)
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
            LOGGER.warning("Skipping already included file: %s", file)
            return

        if not os.path.isfile(file):
            LOGGER.warning("Skipping non-existing file: %s", file)
            return

        self._included.append(file)

        data = self._compile(file, context={"basedir": base})

        if not isinstance(data, dict):
            LOGGER.warning("Loading %s did not return dict, but %s", file, type(data))
            return

        if "include" in data:
            includes = data.pop("include")

            if not isinstance(includes, list):
                includes = [includes]

            for include in includes:
                self.load(include, base, cwd=os.path.dirname(file))

        self.update(data, merge=True)

    def _compile(
        self,
        template,
        default=None,
        blacklist=None,
        whitelist=None,
        context=None,
        **kwargs,
    ):
        if default is None:
            default = self._default_renderers

        ctx = {}

        if context:
            ctx.update(context)

        ctx["tmplpath"] = template
        ctx["tmpldir"] = os.path.dirname(template)
        ctx["minion_id"] = self.minion_id
        ctx["pillar"] = self
        ctx["tower"] = self

        def render(path, renderer="text"):
            if "basedir" in ctx:
                path = os.path.join(ctx["basedir"], path)

            file = os.path.abspath(path)

            if not os.path.isfile(file):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)

            return self._compile(file, renderer, None, None, ctx)

        ctx["render"] = render

        kwargs["tower"] = ctx["tower"]
        kwargs["minion_id"] = ctx["minion_id"]

        try:
            return salt.template.compile_template(
                template=template,
                renderers=self._renderers,
                default=default,
                blacklist=blacklist,
                whitelist=whitelist,
                context=ctx,
                **kwargs,
            )
        except Exception as err:
            LOGGER.critical("Unable to render template `%s'", template)
            LOGGER.exception(err)
            raise err


class Formatter(string.Formatter):
    def __init__(self, tower):
        self._tower = tower

    def get_field(self, key, args, kwargs):
        if key in kwargs:
            return (kwargs[key], None)

        value = self._tower.get(key, delimiter=".")

        if value is None:
            return ("{" + key + "}", None)

        return (value, None)


def _merge(tgt, *objects, strategy="merge-last"):
    for obj in objects:
        if isinstance(tgt, dict):
            tgt = _merge_dict(tgt, copy.deepcopy(obj), strategy)
        elif isinstance(tgt, list):
            tgt = _merge_list(tgt, copy.deepcopy(obj), strategy)
        else:
            raise TypeError(f"Cannot merge {type(tgt)}")

    return tgt


def _merge_dict(tgt, obj, strategy="merge-last"):
    if not isinstance(obj, dict):
        raise TypeError(f"Cannot merge non-dict type, but is {type(obj)}")

    if "__" in obj:
        strategy = obj.pop("__")

    if strategy == "remove":
        for k in obj:
            if k in tgt:
                tgt.pop(k)

    elif strategy == "merge-last":
        for key, val in obj.items():
            if key in tgt and isinstance(tgt[key], dict) and isinstance(val, dict):
                _merge_dict(tgt[key], val, strategy)
            elif key in tgt and isinstance(tgt[key], list) and isinstance(val, list):
                _merge_list(tgt[key], val, strategy)
            else:
                tgt[key] = val

    elif strategy == "merge-first":
        for key, val in obj.items():
            if key in tgt and isinstance(tgt[key], dict) and isinstance(val, dict):
                _merge_dict(tgt[key], val, strategy)
            elif key in tgt and isinstance(tgt[key], list) and isinstance(val, list):
                _merge_list(tgt[key], val, strategy)
            elif key not in tgt:
                tgt[key] = val

    elif strategy == "overwrite":
        tgt.clear()
        tgt.update(obj)

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return tgt


def _merge_list(tgt, lst, strategy="merge-last"):
    if not isinstance(lst, list):
        raise TypeError(f"Cannot merge non-list type, but is {type(lst)}")

    if lst and isinstance(lst[0], dict) and len(lst[0]) == 1 and "__" in lst[0]:
        strategy = lst.pop(0)["__"]

    if strategy == "remove":
        for val in lst:
            if val in tgt:
                tgt.remove(val)

    elif strategy == "merge-last":
        tgt.extend(lst)

    elif strategy == "merge-first":
        for val in lst:
            tgt.insert(0, val)

    elif strategy == "overwrite":
        del tgt[:]
        tgt.extend(lst)

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return tgt
