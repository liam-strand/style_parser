import argparse
import re
import sys

import termcolor as tc

from signature import *


def main():

    args = parse_arguments()

    with open(args.filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    decls = get_function_decls(lines, 0)

    defs = find_definitions(lines, decls)

    functions = []

    for i, d in [(k, lines[k]) for k in defs]:
        p_len = parse_length(i, d, lines)
        functions.append((p_len, i, d))

    print_results(functions, args.filename, args.max_length)

def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename", type=str)
    parser.add_argument("--max_length", "-l", type=int, default=30)

    args = parser.parse_args()

    return args

def generate_report(filename: str, max_length = 30) -> tuple:
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    decls = get_function_decls(lines, 0)

    defs = find_definitions(lines, decls)

    functions = []

    for i, d in [(k, lines[k]) for k in defs]:
        p_len = parse_length(i, d, lines)
        functions.append((p_len, i, d))

    return calculate_score(functions, max_length)

def print_results(lines: list, filename: str, max: int) -> None:
    print(f"{filename.split('/')[-1].split('.')[0]}")

    for l in lines:
        body = l[2] if type(l[2]) == str else " ".join(l[2])
        body = body.rstrip("{\n")
        line_num = l[1]
        if l[0] > max:
            tc.cprint(f"{l[0]:<3} {line_num:<4} {body:<70}", "red", file=sys.stderr)
        else:
            print(f"{l[0]:<3} {line_num:<4} {body:<70}", file=sys.stderr)

    total, count, score = calculate_score(lines, max)    

    print(f"total={total}\nover={count}\nscore={score:.1f}")
    print("-=-=-=-=-=-=-=-=-=-=-=-=-", file=sys.stderr)

def calculate_score(lines: list, max: int) -> tuple:
    lines_over = 0
    count = 0

    for l in lines:
        if l[0] > max:
            lines_over += l[0] - max
            count += 1

    total = len(lines)

    s1 = 100 - lines_over
    s2 = (1 - (count / total)) * 100
    score = 0.5 * (s1 + s2)

    return (total, count, score)

def get_function_decls(lines: list, start: int) -> list:

    found_lines = []
    output_lines = []

    for i, line in enumerate(lines):
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


def parse_length(home: int, first: str, all_lines: list) -> int:

    start = int(home)
    while True:
        if squash_whitespace(all_lines[start]).endswith("{"):
            break
        start += 1

    nesting = 0
    comment_level = 0
    function_len = 0

    for line in all_lines[start:]:
        # print(line)
        function_len += 1
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

    # print("=+========+")

    return function_len - 2


if __name__ == "__main__":
    main()
