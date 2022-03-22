import re
from pprint import pprint
from signature import extract_signature


def generate_report(filename: str, max_len: int, max_depth: int) -> tuple:
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    decls = get_function_decls(lines, 0)

    if len(decls) == 0:
        return (0, 100.0, 0, 100.0, [], lines, filename)

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
        in_single_line_comment = False
        in_string = False
        in_char = False
        testing_line = ""
        for j in range(len(line)):
            (
                comment_level,
                in_single_line_comment,
                in_string,
                in_char,
            ) = track_comments_and_junk(
                line[j],
                line[j - 1],
                comment_level,
                in_single_line_comment,
                in_string,
                in_char,
            )
            if (
                not in_single_line_comment
                and not in_string
                and not in_char
                and comment_level == 0
            ):
                testing_line += line[j]

        if i >= start and re.match("([^\s]+) \w*[(]", testing_line):
            found_lines.append((i, testing_line.rstrip()))
            if start == 0 and "int main(" in testing_line:
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
        if "{" in all_lines[start]:
            break
        start += 1

    nesting = 0
    comment_level = 0
    function_len = 0

    for line in all_lines[start:]:
        function_len += 1

        comment_level, nesting = parse_line(line, comment_level, nesting)

        if nesting == 0:
            break

    return function_len - 2


def parse_depth(home: int, all_lines: list) -> int:
    start = int(home)
    while True:
        if "{" in all_lines[start]:
            break
        start += 1

    nesting = 0
    comment_level = 0
    max_nesting = 0

    for line in all_lines[start:]:
        comment_level, nesting = parse_line(line, comment_level, nesting)

        if nesting == 0:
            break

        max_nesting = max(max_nesting, nesting)

    return max_nesting - 1


def parse_line(line: str, comment_level: int, nesting: int) -> tuple:

    in_single_line_comment = False
    in_string = False
    in_char = False

    for i in range(len(line)):
        (
            comment_level,
            in_single_line_comment,
            in_string,
            in_char,
        ) = track_comments_and_junk(
            line[i],
            line[i - 1],
            comment_level,
            in_single_line_comment,
            in_string,
            in_char,
        )
        should_read = (
            not in_single_line_comment
            and not in_string
            and not in_char
            and comment_level == 0
        )

        if line[i] == "{" and should_read:
            nesting += 1
        elif line[i] == "}" and should_read:
            nesting -= 1

    return comment_level, nesting


def track_comments_and_junk(
    char: str,
    last_char: str,
    comment_level: int,
    in_single_line_comment: bool,
    in_string: bool,
    in_char: bool,
) -> tuple:
    if char == "/" and last_char == "/":
        in_single_line_comment = True
    elif last_char == "/" and char == "*":
        comment_level += 1
    elif last_char == "*" and char == "/":
        comment_level -= 1
    elif char == '"':
        in_string = not in_string
    elif char == "'":
        in_char = not in_char

    return comment_level, in_single_line_comment, in_string, in_char
