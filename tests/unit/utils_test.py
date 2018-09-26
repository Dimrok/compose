# encoding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from compose import utils


class TestJsonSplitter(object):

    def test_json_splitter_no_object(self):
        data = '{"foo": "bar'
        assert utils.json_splitter(data) is None

    def test_json_splitter_with_object(self):
        data = '{"foo": "bar"}\n  \n{"next": "obj"}'
        assert utils.json_splitter(data) == ({'foo': 'bar'}, '{"next": "obj"}')

    def test_json_splitter_leading_whitespace(self):
        data = '\n   \r{"foo": "bar"}\n\n   {"next": "obj"}'
        assert utils.json_splitter(data) == ({'foo': 'bar'}, '{"next": "obj"}')


class TestStreamAsText(object):

    def test_stream_with_non_utf_unicode_character(self):
        stream = [b'\xed\xf3\xf3']
        output, = utils.stream_as_text(stream)
        assert output == '���'

    def test_stream_with_utf_character(self):
        stream = ['ěĝ'.encode('utf-8')]
        output, = utils.stream_as_text(stream)
        assert output == 'ěĝ'


class TestJsonStream(object):

    def test_with_falsy_entries(self):
        stream = [
            '{"one": "two"}\n{}\n',
            "[1, 2, 3]\n[]\n",
        ]
        output = list(utils.json_stream(stream))
        assert output == [
            {'one': 'two'},
            {},
            [1, 2, 3],
            [],
        ]

    def test_with_leading_whitespace(self):
        stream = [
            '\n  \r\n  {"one": "two"}{"x": 1}',
            '  {"three": "four"}\t\t{"x": 2}'
        ]
        output = list(utils.json_stream(stream))
        assert output == [
            {'one': 'two'},
            {'x': 1},
            {'three': 'four'},
            {'x': 2}
        ]


class TestParseBytes(object):
    def test_parse_bytes(self):
        assert utils.parse_bytes('123kb') == 123 * 1024
        assert utils.parse_bytes(123) == 123
        assert utils.parse_bytes('foobar') is None
        assert utils.parse_bytes('123') == 123


class TestRandomIDs(object):
    def test_truncate_id(self):
        # Assert it takes up to the first twelve.
        assert utils.truncate_id('0123456789ABCDEF') == '0123456789AB'
        assert utils.truncate_id('01') == '01'
        # Assert it takes up to the first twelve after the semicolon.
        assert utils.truncate_id('01:2345') == '2345'
        assert utils.truncate_id('0:123456789ABCDEF') == '123456789ABC'
        assert utils.truncate_id('sha256:4e38e38c8ce0b8d90'
                                 '41a9c4fefe786631d1416225'
                                 'e13b0bfe8cfa2321aec4bba') == '4e38e38c8ce0'
        # This makes no sense.
        # XXX: This should be an error.
        assert utils.truncate_id('0:1:23456789ABCDEF') == '1:23456789AB'

    def test_generate_random_id(self):
        def is_a_decimal_integer(value):
            try:
                int(value)
                return True
            except ValueError:
                return False

        for _ in range(100):
            random_id = utils.generate_random_id()
            # Make sure the ID is in an hexadecimal form.
            assert int(random_id, base=16)
            # Make sure the ID is not a decimal integer.
            assert not is_a_decimal_integer(random_id)
