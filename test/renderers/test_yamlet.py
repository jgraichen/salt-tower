# -*- coding: utf-8 -*-

import pytest
import textwrap

from salt.utils.odict import OrderedDict


@pytest.fixture
def result(env):
    def fn():
        return env.compile_template('init.sls', default='yamlet')

    return fn


def test_render(env, result):
    env.write('init.sls',
        '''
        base:
          key: 'text'
          list: [1, 2]
        ''')

    expected = {
        'base': {
            'key': 'text',
            'list': [1, 2]
        }
    }

    assert result() == expected


def test_ordereddict(env, result):
    env.write('init.sls',
        '''
        base:
          key: 'text'
          list: [1, 2]
        ''')

    assert type(result()) == OrderedDict


def test_tag_read(env, result):
    env.write('init.sls', 'key: !read other_file.txt')
    env.write('other_file.txt', 'content')

    assert result() == {'key': b'content'}


def test_tag_include(env, result):
    env.write('init.sls', 'key: !include template.sls')
    env.write('template.sls', 'another: value')

    assert result() == {'key': {'another': 'value'}}


def test_include_yamlet_jinja(env, result):
    env.write('init.sls', 'key: !include template.sls')
    env.write('template.sls',
        '''
        read: !read file.txt
        id: {{ grains["id"] }}
        ''')
    env.write('file.txt', 'txt')

    assert result() == {'key': {
        'read': b'txt',
        'id': 'test_master'
    }}


def test_include_mapping(env, result):
    env.write('init.sls',
        '''
        key: !include
            source: template.sls
        ''')

    env.write('template.sls', 'another: value')

    assert result() == {'key': {'another': 'value'}}


def test_include_mapping_context(env, result):
    env.write('init.sls',
        '''
        key: !include
          source: template.sls
          context:
            value: 5
        ''')

    env.write('template.sls',
        '''
        val: {{ value }}
        ''')

    assert result() == {'key': {'val': 5}}


def test_include_shebang(env, result):
    '''
    The !include tag must respect a shebang in the given template.

    It itself does not strip the shebang line (use the text renderer) for that
    but it must handle IO-like objects such as returned by the jinja renderer.
    '''
    env.write('init.sls',
        '''
        key: !include template.sls
        ''')

    env.write('template.sls', textwrap.dedent(
        '''
        #!jinja
        val: str
        ''').strip())

    assert result() == {'key': '#!jinja\nval: str'}
