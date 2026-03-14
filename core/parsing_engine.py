import re
import json

from jsonpath_ng import parse as jsonpath_parse
from lxml import etree

try:
    from bs4 import BeautifulSoup
except:
    BeautifulSoup = None


class ParsingEngine:

    # ------------------------------------------------
    # LR PARSER
    # ------------------------------------------------

    @staticmethod
    def lr_parse(text, left, right):

        results = []
        start = 0

        while True:

            left_pos = text.find(left, start)

            if left_pos == -1:
                break

            left_pos += len(left)

            right_pos = text.find(right, left_pos)

            if right_pos == -1:
                break

            value = text[left_pos:right_pos]

            results.append(value)

            start = right_pos + len(right)

        return results

    # ------------------------------------------------
    # REGEX PARSER
    # ------------------------------------------------

    @staticmethod
    def regex_parse(text, pattern, index=0):

        try:

            matches = re.findall(pattern, text)

            if not matches:
                return None

            if isinstance(matches[0], tuple):
                matches = [m[0] for m in matches]

            return matches[index] if index < len(matches) else None

        except:
            return None

    # ------------------------------------------------
    # RECURSIVE REGEX
    # ------------------------------------------------

    @staticmethod
    def recursive_regex(text, pattern):

        results = []

        try:

            matches = re.finditer(pattern, text)

            for m in matches:
                results.append(m.group(1) if m.groups() else m.group())

        except:
            pass

        return results

    # ------------------------------------------------
    # MULTI CAPTURE REGEX
    # ------------------------------------------------

    @staticmethod
    def multi_capture_regex(text, pattern):

        try:

            matches = re.findall(pattern, text)

            return matches

        except:
            return []

    # ------------------------------------------------
    # JSON PARSER (KEY SEARCH)
    # ------------------------------------------------

    @staticmethod
    def json_key_search(data, key):

        if isinstance(data, dict):

            for k, v in data.items():

                if k == key:
                    return v

                result = ParsingEngine.json_key_search(v, key)

                if result is not None:
                    return result

        elif isinstance(data, list):

            for item in data:

                result = ParsingEngine.json_key_search(item, key)

                if result is not None:
                    return result

        return None

    @staticmethod
    def json_parse(text, key):

        try:

            data = json.loads(text)

            return ParsingEngine.json_key_search(data, key)

        except:
            return None

    # ------------------------------------------------
    # JSONPATH PARSER
    # ------------------------------------------------

    @staticmethod
    def jsonpath_parse(text, expression):

        try:

            data = json.loads(text)

            expr = jsonpath_parse(expression)

            matches = [match.value for match in expr.find(data)]

            return matches

        except:
            return []

    # ------------------------------------------------
    # CSS PARSER
    # ------------------------------------------------

    @staticmethod
    def css_parse(html, selector, attribute=None, index=0):

        if BeautifulSoup is None:
            return None

        try:

            # wrap fragment HTML so parsing is stable
            if "<html" not in html.lower():
                html = f"<html><body>{html}</body></html>"

            soup = BeautifulSoup(html, "html.parser")

            # let CSS selector engine handle everything
            elements = soup.select(selector)

            if not elements:
                return None

            if index >= len(elements):
                return None

            el = elements[index]

            if attribute:
                return el.get(attribute)

            return el.text.strip()

        except Exception:
            return None

    # ------------------------------------------------
    # XPATH PARSER
    # ------------------------------------------------

    @staticmethod
    def xpath_parse(html, xpath):

        try:

            parser = etree.HTMLParser()

            tree = etree.fromstring(html, parser)

            result = tree.xpath(xpath)

            if not result:
                return None

            if isinstance(result[0], str):
                return result[0]

            return result[0].text

        except:
            return None

    # ------------------------------------------------
    # TOKEN DETECTION
    # ------------------------------------------------

    @staticmethod
    def detect_tokens(text):

        tokens = {}

        patterns = {

            "jwt": r"eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",

            "access_token": r'access[_\-]?token["\']?\s*[:=]\s*["\']([^"\']+)',

            "session": r'session[_\-]?id["\']?\s*[:=]\s*["\']([^"\']+)',

            "csrf": r'csrf[_\-]?token["\']?\s*[:=]\s*["\']([^"\']+)',

            "api_key": r'api[_\-]?key["\']?\s*[:=]\s*["\']([^"\']+)'

        }

        for name, pattern in patterns.items():

            match = re.search(pattern, text, re.I)

            if match:

                tokens[name] = match.group(1) if match.groups() else match.group()

        return tokens

    # ------------------------------------------------
    # UNIVERSAL PARSER
    # ------------------------------------------------

    @staticmethod
    def parse(mode, source, value1=None, value2=None, index=0):

        mode = mode.lower()

        if mode == "lr":
            results = ParsingEngine.lr_parse(source, value1, value2)
            return results[index] if results else None

        if mode == "regex":
            return ParsingEngine.regex_parse(source, value1, index)

        if mode == "json":
            return ParsingEngine.json_parse(source, value1)

        if mode == "jsonpath":
            return ParsingEngine.jsonpath_parse(source, value1)

        if mode == "css":
            return ParsingEngine.css_parse(source, value1, value2, index)

        if mode == "xpath":
            return ParsingEngine.xpath_parse(source, value1)

        return None