# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name


def test_render(render):
    template = """
        #!yaml | filter grain=id
        test_*:
          key: 1

        test_master:
          key: 2

        something else:
          key: 3
    """

    assert render(template) == {"key": 1}


def test_render_default_minion_id(render):
    template = """
        #!yaml | filter
        test_master:
          key: 1

        something else:
          key: 2
    """

    assert render(template) == {"key": 1}


def test_render_grain(env, render):
    env.grains.update({"os_family": "Debian"})

    template = """
        #!yaml | filter grain=os_family
        Debian:
          key: 1

        something else:
          key: 2
    """

    assert render(template) == {"key": 1}


def test_render_pillar(render):
    template = """
        #!yaml | filter pillar=some:key
        value:
          match: True
    """

    context = {"pillar": {"some": {"key": "value"}}}

    assert render(template, context=context) == {"match": True}


def test_render_default(render):
    template = """
        #!yaml | filter pillar=some:key default='matching value'
        '*value':
          match: True
    """

    assert render(template) == {"match": True}
