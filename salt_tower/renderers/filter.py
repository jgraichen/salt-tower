# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
The ``filter`` renderers takes a dataset and only returns the first matching
value. It can match globs on grains and pillar values.

The input must be a parsed dictionary, for example from the YAML renderer. The
first key is uses as a pattern to match the value from grains or pillar. Shell
like globs are supported as the ``fnmatch`` function is used to check the
patterns.

The ``default`` option can provide a string used as the value if the grain or
pillar key does not exist.

Example: Default matching uses ``minion_id``:

.. code-block:: yaml

    #!yaml | filter

    minion-1:
      some:
        data: for minion-1

    other-minion:
      some:
        data: for other minion

    minions*:
      some:
        data: for mulitple minions matching key


Example: Matching using the ``os_family`` grain

.. code-block:: yaml

    #!yaml | filter grain=os_family default='default value'

    Debian:
      package_name: docker.io

    default value:
      package_name: docker-ce
"""

import logging
import shlex

from fnmatch import fnmatch

try:
    from salt.exceptions import TemplateError
except ImportError:
    from salt.exceptions import SaltException as TemplateError

try:
    from salt.utils.data import traverse_dict_and_list
except ImportError:
    from salt.utils import traverse_dict_and_list


VALID_SELECTORS = ("grain", "pillar")
LOG = logging.getLogger(__name__)


def render(  # pylint: disable=too-many-branches
    source, _saltenv, _sls, argline=None, **kwargs
):
    if not isinstance(source, dict):
        raise TypeError(f"Source must be a dict, not {type(source)}")

    selector = "grain"
    default = None
    key = "id"

    if argline:
        for arg in shlex.split(argline):
            try:
                (option, value) = arg.split("=", 2)
            except ValueError:
                option, value = arg, None

            if option in VALID_SELECTORS:
                if not value:
                    raise TemplateError(f"Selector {option!r} needs a value")
                selector = option
                key = value

            elif option == "default":
                if not value:
                    raise TemplateError(f"Option {option!r} needs a value")
                default = value

            else:
                raise TemplateError(f"Unknown option {option!r}")

    if selector == "grain":
        value = traverse_dict_and_list(__grains__, key, default)

    elif selector == "pillar":
        context = kwargs.get("context", {})
        if "pillar" in context:
            value = traverse_dict_and_list(context["pillar"], key, default)
        else:
            value = traverse_dict_and_list(__pillar__, key, default)

    if not value:
        LOG.debug("Skipping blank filter value: %r", value)
        return {}

    # Matching only works on strings
    value = str(value)

    for pattern in source:
        if fnmatch(value, pattern):
            return source[pattern]

    LOG.debug("No pattern matched value: %r", value)

    return {}
