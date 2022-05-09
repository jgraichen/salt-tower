# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=redefined-outer-name

import os

import pytest
import salt
from salt.exceptions import SaltRenderError


def test_common_wildcard(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - common/*
            """,
            "common/test.sls": """
            common: True
            """,
        }
    )

    assert env.ext_pillar() == {"common": True}


def test_missing_file(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - common.sls
            """,
        }
    )

    assert env.ext_pillar() == {}


def test_missing_file_raises(env):
    env.opts.update({"salt_tower.raise_on_missing_files": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - common.sls
            """,
        }
    )

    with pytest.raises(FileNotFoundError, match=r"common.sls"):
        env.ext_pillar()


def test_missing_file_raises_wildcard(env):
    env.opts.update({"salt_tower.raise_on_missing_files": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - common/*
            """,
        }
    )

    with pytest.raises(FileNotFoundError, match=r"common/\*"):
        env.ext_pillar()


def test_missing_file_raises_wildcard_present(env):
    env.opts.update({"salt_tower.raise_on_missing_files": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - common/*
            """,
            "common/file.sls": """
            key: 1
            """,
        }
    )

    assert env.ext_pillar() == {"key": 1}


def test_missing_file_raises_optional(env):
    env.opts.update({"salt_tower.raise_on_missing_files": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - !optional common.sls
                - "minion":
                    - !optional common.sls
            """,
        }
    )

    assert env.ext_pillar() == {}


def test_missing_file_raises_wildcard_optional(env):
    env.opts.update({"salt_tower.raise_on_missing_files": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - !optional common/*
                - "minion":
                    - !optional common/*
            """,
        }
    )

    assert env.ext_pillar() == {}


def test_jinja(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - {{ grains['id'] }}.sls
            """,
            "test_master.sls": """
            minion:
                id: {{ grains['id'] }}
            """,
        }
    )

    assert env.ext_pillar() == {"minion": {"id": "test_master"}}


def test_match_minion_id(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - test_*:
                    - match: minion_id
            """
        }
    )

    assert env.ext_pillar() == {"match": "minion_id"}


def test_match_extended_regex(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - E@[tes]{4}_master$:
                    - match: regexp
            """
        }
    )

    assert env.ext_pillar() == {"match": "regexp"}


def test_match_pillar_data(env):
    env.pillar.update({"pillar_key": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - I@pillar_key:True:
                    - match: pillar
            """
        }
    )

    assert env.ext_pillar() == {
        "pillar_key": True,
        "match": "pillar",
    }


def test_match_tower_pillar_key(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - minion: {id: 'value'}
                - I@minion:id:*:
                    - match: tower_pillar
            """
        }
    )

    assert env.ext_pillar() == {"minion": {"id": "value"}, "match": "tower_pillar"}


def test_match_grains(env):
    env.grains.update({"virtual": False})
    env.setup(
        {
            "tower.sls": """
            base:
                - G@virtual:*:
                    - match: grains
            """
        }
    )

    assert env.ext_pillar() == {"match": "grains"}


@pytest.mark.skip(reason="Global format currently disable as it's a high-risk feature")
def test_late_bind(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - minion: {id: 'my-minion-id'}
                    - late_bind: {minion_id: '{minion.id}'}
            """
        }
    )

    assert env.ext_pillar() == {
        "minion": {"id": "my-minion-id"},
        "late_bind": {"minion_id": "my-minion-id"},
    }


def test_late_bind_not_matching(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - late_bind: '{fuubar}'
            """
        }
    )

    assert env.ext_pillar() == {"late_bind": "{fuubar}"}


def test_late_bind_invalid(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - late_bind: "{^$://DJF$$}"
            """
        }
    )

    assert env.ext_pillar() == {"late_bind": "{^$://DJF$$}"}


def test_default_renderers(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - pillar.sls
            """,
            "pillar.sls": """
            yaml: 'yes'
            jinja: '{{ "yes" }}'
            """,
        }
    )

    assert env.ext_pillar() == {"yaml": "yes", "jinja": "yes"}


def test_renderers_shebang_py(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - pillar.sls
            """,
            "pillar.sls": """
            #!py

            def run():
                return {'py': 'yes'}
            """,
        }
    )

    assert env.ext_pillar() == {"py": "yes"}


def test_include(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - common
            """,
            "common.sls": """
            include:
                - else.sls
            """,
            "else.sls": """
            else: True
            """,
        }
    )

    assert env.ext_pillar() == {"else": True}


def test_include_relative(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - path/to/file
            """,
            "path/to/file.sls": """
            include:
                - ./else.sls
            """,
            "path/to/else.sls": """
            else: True
            """,
        }
    )

    assert env.ext_pillar() == {"else": True}


def test_include_relative_up(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - path/to/file
            """,
            "path/to/file.sls": """
            include:
                - ../else.sls
            """,
            "path/else.sls": """
            else: True
            """,
        }
    )

    assert env.ext_pillar() == {"else": True}


def test_include_nested(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - a/common
            """,
            "a/common.sls": """
            include:
                - b/file.sls
            """,
            "b/file.sls": """
            test: True
            """,
        }
    )

    assert env.ext_pillar() == {"test": True}


def test_include_nested_init(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - a/common
            """,
            "a/common.sls": """
            include:
                - b
            """,
            "b/init.sls": """
            test: True
            """,
        }
    )

    assert env.ext_pillar() == {"test": True}


def test_include_nested_glob(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - a/common
            """,
            "a/common.sls": """
            include:
                - b/*.sls
            """,
            "b/one.sls": """
            one: True
            """,
            "b/two.sls": """
            two: True
            """,
        }
    )

    assert env.ext_pillar() == {"one": True, "two": True}


def test_include_recursive(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - common
            """,
            "common.sls": """
            include: [else.sls]
            order: [1]
            """,
            "else.sls": """
            include: [common.sls]
            order: [2]
            """,
        }
    )

    assert env.ext_pillar() == {"order": [2, 1]}


def test_context_tmpl(env, tmpdir):
    env.setup(
        {
            "tower.sls": """
            base:
                - template.sls
            """,
            "template.sls": """
            tmplpath: {{ tmplpath }}
            tmpldir: {{ tmpldir }}
            """,
        }
    )

    assert env.ext_pillar() == {
        "tmplpath": os.path.join(tmpdir, "template.sls"),
        "tmpldir": tmpdir,
    }


def test_context_minion_id(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - template.sls
            """,
            "template.sls": """
            minion_id: {{ minion_id }}
            """,
        }
    )

    assert env.ext_pillar() == {"minion_id": "test_master"}


def test_context_basedir(env):
    """
    Test path lookup behavior of the yamlet renderer in a tower.

    The !include tag should lookup non-relative paths from the tower
    root.
    """
    env.setup(
        {
            "tower.sls": """
            base:
                - common/init.sls
            """,
            "common/init.sls": """
            conf: !include {{ basedir }}/files/conf.txt
            """,
            "files/conf.txt": """
            Some config file...
            """,
        }
    )

    assert env.ext_pillar() == {"conf": "Some config file..."}


def test_error_invalid_file(env):
    """
    Rendering errors shall not be ignored but raised. Otherwise an
    incomplete or wrong pillar dataset might be returned and the error
    would go unnoticed.
    """
    env.setup(
        {
            "tower.sls": """
            base:
                - common/init.sls
            """,
            "common/init.sls": """
            {% abc %}
            """,
        }
    )

    with pytest.raises(SaltRenderError):
        env.ext_pillar()


def test_render_func(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - index
            """,
            "index.sls": """
            key: !include test/conf.j2
            """,
            "test/conf.j2": """
            #! jinja | text strip
            {{ render('test/conf2.j2') }}
            """,
            "test/conf2.j2": """
            This is a test.
            """,
        }
    )

    assert env.ext_pillar() == {"key": "This is a test."}


def test_render_func_relative(env):
    """
    Relative paths must be specified using the `tmpldir` variable.
    """
    env.setup(
        {
            "tower.sls": """
            base:
                - index
            """,
            "index.sls": """
            key: !include test/conf.j2
            """,
            "test/conf.j2": """
            #! jinja | text strip
            {{ render(tmpldir + '/conf2.j2') }}
            """,
            "test/conf2.j2": """
            This is a test.
            """,
        }
    )

    assert env.ext_pillar() == {"key": "This is a test."}


def test_render_func_in_top(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - key: !include test/conf.j2
            """,
            "test/conf.j2": """
            #! jinja | text strip
            {{ render(tmpldir + '/conf2.j2') }}
            """,
            "test/conf2.j2": """
            This is a test.
            """,
        }
    )

    assert env.ext_pillar() == {"key": "This is a test."}


def test_render_func_context(env):
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - key: !include context/test.py
            """,
            "context/test.py": """
            #!py
            import os.path
            def run():
                return context["render"](
                    os.path.join(context["tmplpath"], "../template.j2"),
                    context={**context, "message": "Hello World!"}
                )
            """,
            "context/template.j2": """
            #!jinja|text strip
            {{ message }}
            """,
        }
    )

    assert env.ext_pillar() == {"key": "Hello World!"}


def test_render_include_dir_mode_sls(env):
    env.opts.update({"salt_tower.include_directory_mode": "all-sls"})
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - role/openssh
            """,
            "role/openssh/10-config.sls": """
            openssh:
                config: 1
            """,
            "role/openssh/20-extension.sls": """
            openssh:
                extension: 1
            """,
        }
    )

    assert env.ext_pillar() == {"openssh": {"config": 1, "extension": 1}}


def test_tower_jinja_import(env):
    """
    The JINJA renderer will always lookup relative files (e.g. from
    import or include) using either the states roots or the pillar roots
    directories if a `saltenv` is set (which is the case when
    renderering pillars).

    Unfortunately it is *not* possible to pass any customization to the
    renderer, e.g. passing an own function to resolve files therefore it
    currently is impossible to load files from the tower directory
    *unless* it also is a pillars root directory.

    This tests ensures that the renderers are called *without* a saltenv
    and do lookup files relative to the current template file.
    """
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - context/init.sls
            """,
            "context/init.sls": """
            #!jinja|yaml
            {%- import_yaml "data.yaml" as data %}
            foo: {{ data.key }}
            """,
            "context/data.yaml": """
            key: 1
            """,
        }
    )

    assert env.ext_pillar() == {"foo": 1}


@pytest.mark.skipif(salt.version.__version__ < "2018", reason="requires salt 2018+")
def test_tower_jinja_import_roots(env):
    """
    Test that the rendering engines are called with all flags to import
    files from the pillar roots instead of the states root. This
    behavior is disabled by default, but can be enabled by a config
    flag.

    Some rendering engines will behave differently now and lookup files
    in the salt masters pillar_roots instead of realtive to the current
    file. The exact behavor depends on salt internals and cannot be
    customized.
    """
    env.opts.update({"salt_tower.unstable_enable_saltenv": True})
    env.setup(
        {
            "tower.sls": """
            base:
                - '*':
                    - context/init.sls
            """,
            "context/init.sls": """
            #!jinja|yaml
            {%- import_yaml "data.yaml" as data %}
            foo: {{ data.source }}
            """,
        }
    )

    assert env.ext_pillar() == {"foo": "pillar_root"}
