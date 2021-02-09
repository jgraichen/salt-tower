# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name


def test_render(render):
    template = """
        A small text
    """

    assert render(template, default="text") == "A small text\n"


def test_strip(render):
    template = """
        #!text strip

            Indented text

        END

    """

    assert render(template) == "Indented text\n\nEND"


def test_key(render):
    template = """
        #!text key=a:b:c
        text value
    """

    assert render(template) == {"a": {"b": {"c": "text value\n"}}}
