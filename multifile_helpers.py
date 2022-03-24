


def pair_files(files: list) -> tuple:
    headers = []
    sources = []
    for f in files:
        if f.endswith(".h"):
            headers.append(f)
        else:
            sources.append(f)

    pairs = []
    singles = []
    for source in sources:
        header = source.replace(".cpp", ".h")
        if header in headers:
            pairs.append((source, header))
        else:
            singles.append(source)

    return pairs, singles
