# https://mustache.github.io/mustache.5.html

from __future__ import annotations

from collections import ChainMap
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache

Escape = Callable[[str], str]


@dataclass
class Node:
    type: str
    token: str
    file: str
    line: str
    lineno: int
    children: list


class TemplateError(Exception):
    def __str__(self):
        node = self.args[0]
        return f'"{node.token}" in {node.file}:{node.lineno}'


def tokenize(s: str, path: str) -> Iterable[Node]:
    for i, line in enumerate(s.splitlines(keepends=True), start=1):
        tail = line
        while '{{' in tail:
            head, tail = tail.split('{{', 1)
            try:
                token, tail = tail.split('}}', 1)
            except ValueError as e:
                node = Node('err', tail, path, line, i, [])
                raise TemplateError(node) from e
            yield Node('text', head, path, line, i, [])
            if token and token[0] in ['!', '#', '^', '/', '>', '&']:
                yield Node(token[0], token[1:].strip(), path, line, i, [])
            else:
                yield Node('var', token.strip(), path, line, i, [])
        yield Node('text', tail, path, line, i, [])


def parse(s: str, path: str='') -> list[Node]:
    stack: list[list[Node]] = [[]]
    for node in tokenize(s, path):
        if node.type in ['#', '^']:
            stack.append([])
        elif node.type == '/':
            section = stack.pop()
            if section[0].token != node.token:
                raise TemplateError(node)
            node = section.pop(0)
            node.children = section
        stack[-1].append(node)
    if len(stack) != 1:
        raise TemplateError(stack[-1][0])
    return stack[0]


@cache
def get_template(path: str, indent: str = '') -> list[Node]:
    with open(path) as fh:
        return parse(fh.read(), path)


def is_standalone(line):
    nodes = list(tokenize(line, ''))
    return (
        len(nodes) == 3
        and not nodes[0].token.strip()
        and nodes[1].type in ['!', '#', '^', '/']
        and not nodes[2].token.strip()
    )


def render_section(node: Node, context, escape: Escape) -> str:
    value = context.get(node.token)
    if isinstance(value, list):
        output = ''
        for item in value:
            if not isinstance(item, Mapping):
                item = {'.': item}
            output += render(node.children, ChainMap(item, context), escape)
        return output
    elif callable(value):
        return value(node.children, context, escape)
    elif value:
        if not isinstance(value, Mapping):
            value = {'.': value}
        return render(node.children, ChainMap(value, context), escape)
    else:
        return ''


def render(nodes: Iterable[Node], context, escape: Escape) -> str:
    output = ''
    for node in nodes:
        try:
            if node.type == 'text':
                if not is_standalone(node.line):
                    output += node.token
            elif node.type == '#':
                output += render_section(node, context, escape)
            elif node.type == '^':
                value = context.get(node.token)
                if not value:
                    output += render(node.children, context, escape)
            elif node.type == '>':
                children = get_template(node.token)
                output += render(children, context, escape)
            elif node.type == '&':
                output += str(context.get(node.token) or '')
            elif node.type == 'var':
                output += escape(str(context.get(node.token) or ''))
        except KeyError as e:
            raise TemplateError(node) from e
    return output
