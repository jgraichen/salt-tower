# -*- coding: utf-8 -*-

import pytest
import textwrap


from salt.utils.odict import OrderedDict


from test.conftest import TestRenderer


class TestYamletRender(TestRenderer):
    default_renderer = 'yamlet'

    template = textwrap.dedent('''
        base:
          key: 'text'
          list: [1, 2]
        ''')

    def test_render(self):
        data = {
            'base': {
                'key': 'text',
                'list': [1, 2]
            }
        }

        assert self.render() == data

    def test_ordereddict(self):
        assert type(self.render()) == OrderedDict


class TestYamletTags(TestRenderer):
    default_renderer = 'yamlet'

    def test_read(self):
        self.write('key: !read other_file.txt')
        self.write('content', path='other_file.txt')

        assert self.render() == {'key': 'content'}

    def test_include(self):
        self.write('key: !include template2.sls')
        self.write('another: value', path='template2.sls')

        assert self.render() == {'key': {'another': 'value'}}

    def test_include_defaults_to_yaml_jinja_renderer(self):
        '''
        Test that the default renderer is like yaml and jinja
        '''

        self.write('key: !include template2.sls')
        self.write('id: {{ grains["id"] }}', path='template2.sls')

        assert self.render() == {'key': {'id': 'test_master'}}

    def test_include_by_source(self):
        '''
        Include file using a YAML mapping node
        '''

        self.write('''
            key: !include
                source: template2.sls
            ''')

        self.write('another: value', path='template2.sls')

        assert self.render() == {'key': {'another': 'value'}}

    def test_include_by_source_with_context(self):
        '''
        Test passing context variable to included template engines e.g.
        passing a variable to jinja
        '''

        self.write('''
            key: !include
              source: template2.sls
              context:
                value: 5
            ''')

        self.write('val: "{{ value }}"', path='template2.sls')

        assert self.render() == {'key': {'val': '5'}}

    def test_include_by_source_with_default(self):
        '''
        Test setting a default renderer like only yaml without jinja
        '''

        self.write('''
            key: !include
              source: template2.sls
              default: yaml
            ''')

        self.write('val: "{{ value }}"', path='template2.sls')

        assert self.render() == {'key': {'val': '{{ value }}'}}

    def test_include_by_source_default_shebang(self):
        '''
        Ensure the shebang override a default renderer configured
        in the include tag
        '''

        self.write('''
            key: !include
              source: template2.sls
              default: yaml
              context:
                value: 5
            ''')

        self.write(textwrap.dedent('''
            #!jinja|yaml
            val: "{{ value }}"
            ''').lstrip(), path='template2.sls')

        assert self.render() == {'key': {'val': '5'}}
