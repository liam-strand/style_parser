from printers import (
    short_function_color_printer,
    long_function_color_printer,
    short_function_bw_printer,
    long_function_bw_printer,
)
from check_length_nesting import generate_report
import argparse
import multiprocessing as mp
import os.path
from tqdm import tqdm


def main():
    args = get_args()

    # Get all cpp files recursively starting at path
    files = get_files(args.path)

    if args.verbose and args.output is None:
        printer = long_function_color_printer
    elif args.verbose and args.output is not None:
        printer = long_function_bw_printer
    elif not args.verbose and args.output is None:
        printer = short_function_color_printer
    else:
        printer = short_function_bw_printer

    zipped = generate_zip(files, args.length, args.depth, printer)

    if args.nproc == 1:
        lines = list(tqdm(map(apply_function, zipped), total=len(zipped)))
    else:
        with mp.Pool(args.nproc) as pool:
            lines = list(tqdm(pool.imap(apply_function, zipped), total=len(zipped)))
        
    if args.output in ["-", "stdout"] or not args.output:
        for line in sorted(lines):
            print(line)
    else:
        with open(args.output, "w") as f:
            for line in sorted(lines):
                print(line, file=f)


def get_args() -> argparse.Namespace:
    """TODO: get_args() docstring"""
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

    args = parser.parse_args()

    assert(args.nproc > 0)
    assert(args.depth > 0)
    assert(args.length > 0)

    return args


def generate_zip(files: list, max_len: int, max_depth: int, printer) -> list:
    """TODO: Docstring for generate_zip."""
    zipped = []

    for file in files:
        zipped.append((file, max_len, max_depth, printer))

    return zipped


def apply_function(args: tuple) -> str:
    """TODO: Docstring for apply_function."""
    filename, max_len, max_depth, printer = args
    try:
        ll, ls, ld, ds, functions, all_lines, filename = generate_report(
            filename, max_len, max_depth
        )
    except IndexError as e:
        print(f"error: {filename} {e}")
        return f"{filename} ERROR"
    
    return printer(ll, ls, ld, ds, max_len, max_depth, functions, all_lines, filename)


def get_files(start_path: str) -> list:
    """TODO: Docstring for get_files."""
    files = []

    for dirpath, _, filenames in os.walk(start_path):
        for filename in [f for f in filenames if f.endswith(".cpp")]:
            files.append(os.path.join(dirpath, filename))

    return files


if __name__ == "__main__":
    main()
