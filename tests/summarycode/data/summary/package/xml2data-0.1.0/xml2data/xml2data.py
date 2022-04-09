# -*- coding: utf-8 -*-


import urllib2
import re
from StringIO import StringIO

from lxml import etree, cssselect
import chardet


def urlload(url, template, param=None):
    res = urllib2.urlopen(url, param)
    document = ''.join(res)
    encoding = ''
    ct = res.info().get('Content-Type')
    if ct is not None:
        m = re.search(r';\s*charset=[\'\"]?(?P<encoding>\S+?)[\'\"]?\s*$', ct)
        encoding = m.group('encoding') if m is not None else ''
    encoding = encoding or chardet.detect(document)['encoding']
    document = document.decode(encoding, 'ignore')
    return Parser.parse(template, document)


def load(s, template):
    return loads(''.join(s), template)


def loads(s, template):
    if isinstance(s, str):
        encoding = chardet.detect(s)['encoding']
        s = s.decode(encoding)
    return Parser.parse(template, s)


class Parser:

    @classmethod
    def parse(cls, template, document=None):
        xml = document
        if xml is not None and not isinstance(xml, etree.ElementBase):
            xml = etree.parse(StringIO(document), etree.HTMLParser())
        (d, c) = cls._parse(template, xml)
        if c.lstrip() != '':  # if non-parsed data remain
            raise Xml2DataSyntaxError()
        return d

    @classmethod
    def _parse(cls, content, xml=None):
        """ parse a given content of the template.
            it returns a tuple (parsed data, remaining content).
        """
        c = content.lstrip()
        for f in (cls._parse_num, cls._parse_str) + ( 
                  lambda c_: cls._parse_dict(c_, xml),) + (
                  (lambda c_: cls._parse_selector(c_, xml),) if xml is not None else ()):
            try:
                return f(c)
            except Xml2DataSyntaxError:
                continue
        raise Xml2DataSyntaxError()

    @classmethod
    def _parse_str(cls, content):
       c = content.lstrip()
       q = ('\'' if c[0] == '\'' else
            '\"' if c[0] == '\"' else None)
       if q is None:
           raise Xml2DataSyntaxError()
       s = 1
       while True:
           i = c.find(q, s)
           if i == -1:
               raise Xml2DataSyntaxError()
           is_valid_quote = True
           for j in range(i - 1, 0, -2):
               if c[j] != '\\':
                   break
               if c[j] == '\\' and c[j - 1: j + 1] != '\\\\':
                   is_valid_quote = False
                   c = c[0:j] + c[j + 1:]
                   s = i
                   break
           if is_valid_quote:
               return (c[1:i], c[i + 1:])

    @classmethod
    def _parse_num(cls, content):
        c = content.lstrip()
        m = re.match(r'[\-\+]?\d+', c)
        if m is None:
            raise Xml2DataSyntaxError()
        return (int(m.group()), c[m.end():])

    @classmethod
    def _parse_dict(cls, content, *args):
        c = content.lstrip()

        if c[0] != '{':
            raise Xml2DataSyntaxError()

        d = {}
        c = c[1:].lstrip()
        while c[0] != '}':
            (k, c) = cls._parse(c, *args)

            c = c.lstrip()
            if c[0] != ':':
                raise Xml2DataSyntaxError()

            c = c[1:].lstrip()
            (v, c) = cls._parse(c, *args)

            c = c.lstrip()
            if not (c[0] == ',' or c[0] == '}'):
                raise Xml2DataSyntaxError()

            try:
                d[k] = v
            except TypeError:
                pass
            except:
                raise Xml2DataSyntaxError()

            if c[0] == ',':
                c = c[1:].lstrip()

        return (d, c[1:])

    # not used
    @classmethod
    def _parse_regular_list(cls, content, *args):
        c = content.lstrip()
        if c[0] != '[':
            raise Xml2DataSyntaxError()

        d = []
        c = c[1:].lstrip()
        while c[0] != ']':
            (v, c) = cls._parse(c, *args)

            c = c.lstrip()
            if not (c[0] == ',' or c[0] == ']'):
                raise Xml2DataSyntaxError()

            d.append(v)

            if c[0] == ',':
                c = c[1:].lstrip()

        return (d, c[1:])

    @classmethod
    def _parse_selector(cls, content, xml):

        # get end position of css-selector
        def get_selector_unit_end_pos(c_):
            i = -1
            length = len(c_)
            while (i + 1) < length:
                i += 1
                a = c_[i]
                if a == '[':
                    pos_eq = c_.find('=', i + 1)
                    pos_br = c_.find(']', i + 1)
                    j = pos_br
                    if pos_eq != -1 and pos_eq < pos_br:
                        (_, r) = cls._parse_str(c_[pos_eq + 1:])
                        j = length - len(r)
                    i = c_.find(']', j)  # end position of a bracket inside css-selector
                    if i == -1:
                        raise Xml2DataSyntaxError()
                elif a == ']' or a == ',' or a == '}':
                    return i
            return -1

        c = content.lstrip()

        is_list = False
        if c[0] == '[':
            is_list = True
            c = c[1:]

        end = get_selector_unit_end_pos(c)

        # handle [...] including left side of @-op
        map_index = c.find('@')
        mapped = c[map_index + 1:] if map_index != -1 and map_index < end else None
        if not is_list and mapped is not None:
            raise Xml2DataSyntaxError()
        if is_list and mapped is None:
            raise Xml2DataSyntaxError()
        if is_list:
            remaining_content = cls._parse(mapped, etree.Element('root'))[1].lstrip()
            if remaining_content[0] != ']':
                raise Xml2DataSyntaxError()
            sel = cssselect.CSSSelector(c[:map_index])
            return ([cls._parse(mapped, e)[0] for e in sel(xml)],
                    remaining_content[1:])

        # handle regular selector, which is both side of $-op
        remaining_content = c[end:] if end != -1 else ''
        c = c[:end] if end != -1 else c
        func_index = c.find('$')
        func = c[func_index + 1:].strip() if func_index != -1 else 'text'
        s = c[:func_index].lstrip() if func_index != -1 else c.lstrip()
        elem = xml
        if len(s) > 0:
            sel = cssselect.CSSSelector(s)
            elem = sel(xml)
            try:
                elem = elem[0]
            except IndexError:
                elem = None
        r = None
        if elem is not None:
            if func == 'text':
                r = etree.tostring(elem, method='text', with_tail=False, encoding='utf-8')
            elif func == 'immediate_text':
                r = elem.text
            elif func == 'html':
                r = etree.tostring(elem, with_tail=False, encoding='utf-8')
            else:
                m = re.match(r'\[\s*(?P<attr>\S+)\s*\]', func)
                if m is not None:
                    r = elem.get(m.group('attr'))
            if r is not None:
                r = r.strip()
        return (r, remaining_content)


class Xml2DataSyntaxError(SyntaxError):
    pass


if __name__ == '__main__':
    pass
