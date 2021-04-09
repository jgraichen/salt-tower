# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name
# pylint: disable=unidiomatic-typecheck

import os
import textwrap

from salt.utils.odict import OrderedDict


def test_render(render):
    template = """
      base:
        key: 'text'
        list: [1, 2]
    """

    assert render(template, default="yamlet") == {
        "base": {"key": "text", "list": [1, 2]}
    }


def test_ordereddict(render):
    template = """
      base:
        key: 'text'
        list: [1, 2]
    """

    result = render(template, default="yamlet")
    assert type(result) == OrderedDict


def test_tag_read(env, render):
    env.write("other_file.txt", "content")

    template = """
      key: !read other_file.txt
    """

    assert render(template, default="yamlet") == {"key": b"content"}


def test_tag_read_binary(env, render):
    env.write("binary-file.bin", b"jd\x81\xed\xa2~*\xca6\xd88,\x15zr\xb6", mode="wb")

    template = """
      key: !read binary-file.bin
    """

    assert render(template, default="yamlet") == {
        "key": b"jd\x81\xed\xa2~*\xca6\xd88,\x15zr\xb6"
    }


def test_tag_include(env, render):
    env.write("template.sls", "another: value")

    assert render("key: !include template.sls", default="yamlet") == {
        "key": {"another": "value"}
    }


def test_include_yamlet_jinja(env, render):
    env.write(
        "some_yamlet.sls",
        """
            read: !read file.txt
            id: {{ grains["id"] }}
        """,
    )
    env.write("file.txt", "txt")

    template = """
        key: !include some_yamlet.sls
    """

    assert render(template, default="yamlet") == {
        "key": {"read": b"txt", "id": "test_master"}
    }


def test_include_mapping(env, render):
    env.write("template.sls", "another: value")

    template = """
        key: !include
            source: template.sls
    """

    assert render(template, default="yamlet") == {"key": {"another": "value"}}


def test_include_mapping_context(env, render):
    env.write("template.sls", "val: {{ value }}")

    template = """
        key: !include
          source: template.sls
          context:
            value: 5
    """

    assert render(template, default="yamlet") == {"key": {"val": 5}}


def test_include_shebang(env, render):
    """
    The !include tag must respect a shebang in the given template.

    It itself does not strip the shebang line (use the text renderer) for that
    but it must handle IO-like objects such as returned by the jinja renderer.
    """

    env.write("template.sls", "#!jinja\nval: {{ grains['id'] }}")

    template = """
        key: !include template.sls
    """

    assert render(template, default="yamlet") == {"key": "#!jinja\nval: test_master"}


def test_include_tmplpath(env, render, tmpdir):
    """
    The !include tag passes ``tmplpath`` and ``tmpldir`` to the template
    renderer to allow relative includes via ``tmpldir + '/file'``.
    """

    env.write(
        "file.sls",
        textwrap.dedent(
            """
            #!jinja|yaml
            tmplpath: {{ tmplpath }}
            tmpldir: {{ tmpldir }}
            """
        ).strip(),
    )

    template = """
      key: !include file.sls
    """

    assert render(template, default="yamlet") == {
        "key": {"tmplpath": os.path.join(tmpdir, "file.sls"), "tmpldir": tmpdir}
    }


def test_include_inherit_context(env, render):
    """
    The !include tag passes given ``context`` to downstream renderers.
    """

    env.write(
        "file.sls",
        textwrap.dedent(
            """
            #!jinja|text
            {{ fuubar() }}
            """
        ).strip(),
    )

    template = """
      key: !include file.sls
    """

    def fuubar():
        return "fuubar"

    assert render(template, default="yamlet", context={"fuubar": fuubar}) == {
        "key": "fuubar"
    }


def test_include_does_not_mutate_context(env, render):
    """
    The !include tag passes given ``context`` to downstream renderers.

    They usual mutate their ``context`` object, but yamlet passes a copy.
    Therefore the original ``context`` object is not modified.
    """

    env.write("file.sls", "")

    context = {"key": "abc"}
    template = """
      key: !include file.sls
    """

    render(template, default="yamlet", context=context)

    assert context == {"key": "abc"}
