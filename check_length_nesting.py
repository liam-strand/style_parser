import argparse
import re
import sys

import termcolor as tc

from signature import *


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", type=str)
    parser.add_argument("--max_length", "-l", type=int, default=30)
    parser.add_argument("--max_depth", "-d", type=int, default=4)

    args = parser.parse_args()

    return args


def generate_report(filename: str, max_len=30, max_depth=4) -> tuple:
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    decls = get_function_decls(lines, 0)

    defs = find_definitions(lines, decls)

    functions = []

    for i, d in [(k, lines[k]) for k in defs]:
        p_len = parse_length(i, lines)
        p_depth = parse_depth(i, lines)
        functions.append((p_len, p_depth, i, d))

    lines_long, lines_score = calculate_line_score(functions, max_len)
    lines_deep, nestd_score = calculate_deep_score(functions, max_depth)

    return (
        lines_long,
        lines_score,
        lines_deep,
        nestd_score,
        functions,
        lines,
        filename,
    )


def calculate_line_score(lines: list, max_len: int) -> tuple:
    lines_over = 0
    count = 0

    for l in lines:
        if l[0] > max_len:
            lines_over += l[0] - max_len
            count += 1

    total = len(lines)

    s1 = 100 - lines_over
    s2 = (1 - (count / total)) * 100
    score = 0.5 * (s1 + s2)

    return (count, score)


def calculate_deep_score(lines: list, max_depth: int) -> tuple:
    count = 0
    lines_deep = 0

    for l in lines:
        if l[1] > max_depth:
            count += 1
            lines_deep += l[1] - max_depth

    total = len(lines)

    s1 = (50 - lines_deep) * 2
    s2 = (1 - (count / total)) * 100
    score = 0.5 * (s1 + s2)

    return (count, score)


def get_function_decls(lines: list, start: int) -> list:

    found_lines = []
    output_lines = []
    comment_level = 0

    for i, line in enumerate(lines):
        if "/*" in line:
            comment_level += line.count("/*")
        if "*/" in line:
            comment_level -= line.count("*/")

        if comment_level == 0 and not squash_whitespace(line).startswith("//"):
            if i >= start and re.match("([^\s]+) \w*[(]", line):
                found_lines.append((i, line.rstrip()))
                if start == 0 and line.startswith("int main("):
                    break

    for f_line in found_lines:
        tag = extract_signature(lines, f_line[0])
        if not tag in [sig[1] for sig in output_lines]:
            output_lines.append((f_line[0], tag))

    return output_lines


def squash_whitespace(s: str) -> str:
    return " ".join(s.split())


def find_definitions(lines: list, funcs: list) -> list:

    offset = max([decl[0] for decl in funcs]) - 1

    defs = get_function_decls(lines, offset)

    return [d[0] for d in defs if d[1] in [f[1] for f in funcs]]


def parse_length(home: int, all_lines: list) -> int:

    start = int(home)
    while True:
        if squash_whitespace(all_lines[start]).endswith("{"):
            break
        start += 1

    nesting = 0
    comment_level = 0
    function_len = 0

    for line in all_lines[start:]:
        function_len += 1

        if "/*" in line:
            comment_level += line.count("/*")
        if "*/" in line:
            comment_level -= line.count("*/")

        if comment_level == 0 and not squash_whitespace(line).startswith("//"):

            for char in line:
                if char == "{":
                    nesting += 1
                elif char == "}":
                    nesting -= 1
            if nesting == 0:
                break

    return function_len - 2


def parse_depth(home: int, all_lines: list) -> int:
    start = int(home)
    while True:
        if squash_whitespace(all_lines[start]).endswith("{"):
            break
        start += 1

    nesting = 0
    comment_level = 0
    max_nesting = 0

    for line in all_lines[start:]:
        if "/*" in line:
            comment_level += line.count("/*")
            continue
        if "*/" in line:
            comment_level -= line.count("*/")

        if comment_level == 0 and not squash_whitespace(line).startswith("//"):

            for char in line:
                if char == "{":
                    nesting += 1
                elif char == "}":
                    nesting -= 1
            if nesting == 0:
                break

        max_nesting = max(max_nesting, nesting)

    return max_nesting


if __name__ == "__main__":
    print("pls don't run this file", file=sys.stderr)
