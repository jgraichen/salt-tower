# -*- coding: utf-8 -*-

import pytest
import textwrap


from test.conftest import TestRenderer


class TestTextRenderer(TestRenderer):
    default_renderer = 'text'

    def test_render(self):
        self.write('A small text')

        assert self.render() == 'A small text'

    def test_strip(self):
        self.write(textwrap.dedent(
            '''
            #!text strip

                Indented text

            END

            '''
            ).lstrip())

        assert self.render() == 'Indented text\n\nEND'

    def test_key(self):
        self.write(textwrap.dedent(
            '''
            #!text key=a:b:c
            text value
            '''
            ).strip())

        assert self.render() == {'a': {'b': {'c': 'text value'}}}
