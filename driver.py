from check_length_nesting import generate_report
import argparse
import termcolor as tc
import multiprocessing as mp
import sys
import os.path


def main():

    args = get_args()

    files = get_files(args.path)

    zipped = generate_zip(files, args.output, args.length, args.depth)

    if args.verbose:
        with mp.Pool(args.nproc) as pool:
            lines = pool.map(long_output, zipped)
    else:
        with mp.Pool(args.nproc) as pool:
            lines = pool.map(short_output, zipped)

    if args.output:
        with open(args.output, "w") as f:
            for line in sorted(lines):
                f.write(line + "\n")
    else:
        for line in sorted(lines):
            print(line)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        help="path to the directory with cpp files",
        type=str,
        default=".",
    )
    parser.add_argument(
        "-n", "--nproc", help="number of processes to use", type=int, default=1
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
        default=False,
    )
    parser.add_argument("-o", "--output", help="output file", type=str, default=None)
    parser.add_argument(
        "-l", "--length", help="maximum function length", type=int, default=30
    )
    parser.add_argument(
        "-d", "--depth", help="maximum function depth", type=int, default=4
    )
    return parser.parse_args()


def short_output(file_zipped: list) -> str:

    file, output, max_len, max_depth = file_zipped

    ll, ls, ld, ds, _, _, filename = generate_report(file, max_len, max_depth)

    if output == None:
        output_str = tc.colored("")
        output_str += f"{filename.split('/')[-2]:<10} "
        if ll == 0:
            output_str += f"{ll:>2} {ls:>5.1f} "
        else:
            output_str += tc.colored(f"{ll:>2} {ls:>5.1f} ", "red", attrs=["bold"])

        if ld == 0:
            output_str += f"{ld:>2} {ds:>5.1f} "
        else:
            output_str += tc.colored(f"{ld:>2} {ds:>5.1f}", "red", attrs=["bold"])
    else:
        output_str = ""
        output_str = (
            f"{filename.split('/')[-2]:<10} {ll:>2} {ls:>5.1f} {ld:>2} {ds:>5.1f} "
        )

    return output_str


def long_output(file_zipped: list) -> str:
    file, output, max_len, max_depth = file_zipped
    ll, ls, ld, ds, functions, all_lines, filename = generate_report(
        file, max_len, max_depth
    )

    if output:
        output_str = (
            f"{filename.split('/')[-2]:<10} {ll:>2} {ls:>5.1f} {ld:>2} {ds:>5.1f}\n"
        )
        for fn in functions:
            body = get_function_body(fn, all_lines)
            output_str += f"{fn[0]:<3} {fn[1]:<2} {fn[2]:<4} {body}\n"
    else:
        output_str = tc.colored(
            f"{filename.split('/')[-2]:<10} {ll:>2} {ls:>5.1f} {ld:>2} {ds:>5.1f}\n"
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

            body = get_function_body(fn, all_lines)

            if fn[0] > max_len or fn[1] > max_depth:
                output_str += tc.colored(f"{fn[2]:<4} {body}\n", "red", attrs=["bold"])
            else:
                output_str += f"{fn[2]:<4} {body}\n"
    return output_str.strip()


def get_function_body(function: tuple, all_lines: list) -> str:
    body = function[3].strip()
    if not (body.endswith(";") or body.endswith("{")):
        idx = function[2]
        while not (body.endswith(";") or body.endswith("{")):
            idx += 1
            body += " " + all_lines[idx].strip()

    body = body.rstrip(";{ ")

    return body


def generate_zip(files: list, output: str, max_len: int, max_depth: int) -> list:
    zipped = []

    for file in files:
        zipped.append((file, output, max_len, max_depth))

    return zipped


def get_files(start_path: str) -> list:
    files = []

    for dirpath, _, filenames in os.walk(start_path):
        for filename in [f for f in filenames if f.endswith(".cpp")]:
            files.append(os.path.join(dirpath, filename))

    return files


if __name__ == "__main__":
    main()
