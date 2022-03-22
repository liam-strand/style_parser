import termcolor as tc


def short_function_color_printer(
    long_funcs: int,
    length_score: int,
    deep_funcs: int,
    deep_score: int,
    max_len: int,
    max_depth: int,
    functions: list,
    all_lines: list,
    filename: str,
) -> str:
    """Get a report on a file and print it's summarized results.

    The output string is of the form:
    <dirname> <long_function_count> <length_score> <deep_function_count> <deep_score>

    When configured for printing to stdout, fields that exceed the maximum values
    are printed in red.
    """

    output_str = tc.colored("")
    output_str += f"{extract_filename(filename):<30} "
    if long_funcs == 0:
        output_str += f"{long_funcs:>2} {length_score:>5.1f} "
    else:
        output_str += tc.colored(
            f"{long_funcs:>2} {length_score:>5.1f} ", "red", attrs=["bold"]
        )

    if deep_funcs == 0:
        output_str += f"{deep_funcs:>2} {deep_score:>5.1f} "
    else:
        output_str += tc.colored(
            f"{deep_funcs:>2} {deep_score:>5.1f}", "red", attrs=["bold"]
        )

    return output_str


def short_function_bw_printer(
    long_funcs: int,
    length_score: int,
    deep_funcs: int,
    deep_score: int,
    max_len: int,
    max_depth: int,
    functions: list,
    all_lines: list,
    filename: str,
) -> str:
    """Get a report on a file and print it's summarized results.

    The output string is of the form:
    <dirname> <long_function_count> <length_score> <deep_function_count> <deep_score>

    When configured for printing to stdout, fields that exceed the maximum values
    are printed in red.
    """

    return f"{extract_filename(filename):<30} {long_funcs:>2} {length_score:>5.1f} {deep_funcs:>2} {deep_score:>5.1f}"


def long_function_color_printer(
    long_funcs: int,
    length_score: int,
    deep_funcs: int,
    deep_score: int,
    max_len: int,
    max_depth: int,
    functions: list,
    all_lines: list,
    filename: str,
) -> str:
    """Get a report on a file and return its longform result.

    The output string is of the form:
    <dirname> <long_function_count> <length_score> <deep_function_count> <deep_score>
    followed by newline-seperated strings for each function with each line of the form
    <length> <depth> <position> <signature>

    When configured for printing to stdout, fields that exceed the maximum values
    are printed in red.
    """

    output_str = tc.colored(
        f"{extract_filename(filename):<30} {long_funcs:>2} {length_score:>5.1f} {deep_funcs:>2} {deep_score:>5.1f}\n"
    )
    for fn in functions:
        if fn[0] > max_len:
            output_str += tc.colored(f"{fn[0]:<3} ", "red", attrs=["bold"])
        else:
            output_str += f"{fn[0]:<3} "
        if fn[1] > max_depth:
            output_str += tc.colored(f"{fn[1]:<2} ", "red", attrs=["bold"])
        else:
            output_str += f"{fn[1]:<2} "

        sig = get_function_sig(fn, all_lines)

        if fn[0] > max_len or fn[1] > max_depth:
            output_str += tc.colored(f"{fn[2]:<4} {sig}\n", "red", attrs=["bold"])
        else:
            output_str += f"{fn[2]:<4} {sig}\n"
    return output_str.strip()


def long_function_bw_printer(
    long_funcs: int,
    length_score: int,
    deep_funcs: int,
    deep_score: int,
    max_len: int,
    max_depth: int,
    functions: list,
    all_lines: list,
    filename: str,
) -> str:
    """Get a report on a file and return its longform result.

    The output string is of the form:
    <dirname> <long_function_count> <length_score> <deep_function_count> <deep_score>
    followed by newline-seperated strings for each function with each line of the form
    <length> <depth> <position> <signature>

    When configured for printing to stdout, fields that exceed the maximum values
    are printed in red.
    """

    # If we are writing to a file, we do not want to color the text
    output_str = f"{extract_filename(filename):<30} {long_funcs:>2} {length_score:>5.1f} {deep_funcs:>2} {deep_score:>5.1f}\n"
    for fn in functions:
        sig = get_function_sig(fn, all_lines)
        output_str += f"{fn[0]:<3} {fn[1]:<2} {fn[2]:<4} {sig}\n"

    return output_str.strip()


def get_function_sig(function: tuple, all_lines: list) -> str:
    """Takes a function object and returns the full signature as it is presented in the file.

    The provided function tuple is of the form (length, depth, position, Signature)
    and the provided all_lines list is a list of strings representing the file.
    """

    # Usually just this first line is enough
    sig = function[3].strip()

    # Keep reading and adding until we reach the end of the signature
    if not (sig.endswith(";") or sig.endswith("{")):
        idx = function[2]
        while not (sig.endswith(";") or sig.endswith("{")):
            idx += 1
            sig += " " + all_lines[idx].strip()

    # Lots of cleanup because students can be silly :)
    sig = sig.split("{")[0].split("//")[0].strip()

    return sig


def extract_filename(raw_filename: str) -> str:
    """TODO: Docstring for extract_filename."""

    return "/".join(raw_filename.split("/")[-2:])
