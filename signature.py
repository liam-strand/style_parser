import re


class Signature:
    def __init__(self, return_type: str, name: str, params: list):
        self.return_type = return_type
        self.name = name
        self.params = params

    def __repr__(self):
        s = f"{self.return_type} {self.name}("
        for i, param in enumerate(self.params):
            if i != 0:
                s += ", "

            s += f"{param.p_type} {param.p_name}"

        s += ")"

        return s

    def __eq__(self, other) -> bool:
        same = True

        same &= self.return_type == other.return_type
        same &= self.name == other.name

        for s_p, o_p in zip(self.params, other.params):
            same &= s_p.p_type == o_p.p_type

        return same


class Parameter:
    def __init__(self, p_type: str, p_name: str):
        self.p_type = p_type
        self.p_name = p_name

    def __repr__(self):
        return f"({self.p_type}, {self.p_name})"


def extract_signature(lines: list, idx: int) -> Signature:

    height = 1
    i = int(idx)

    while not any([c in lines[i] for c in ["{", ";"]]):
        height += 1
        i += 1

    d = get_full_string(lines, idx, i + 1)

    splitted = re.split("\s|\(", d)
    raw_type = splitted[0]
    raw_name = splitted[1]
    raw_args = " ".join(splitted[2:]).rstrip("); {").split(", ")

    cleaned_args = []
    for a_s in raw_args:
        parts = a_s.split()
        partial_type = parts[0]
        partial_name = " ".join(parts[1:]).strip()
        cleaned_args.append(generate_parameter_from_pair(partial_type, partial_name))

    return Signature(raw_type, raw_name, cleaned_args)


def generate_parameter_from_pair(type_ish: str, name_ish: str) -> Parameter:

    working_type = str(type_ish)
    working_name = str(name_ish)

    while working_name.startswith("*"):
        working_type += "*"
        working_name = working_name.removeprefix("*")

    arr_indicator = ""
    new_name = ""
    nest_depth = 0
    for char in working_name:
        if char == "[":
            nest_depth += 1
            arr_indicator += char
        elif char == "]":
            nest_depth -= 1
            arr_indicator += char
        elif nest_depth == 0:
            new_name += char

    new_type = working_type + arr_indicator

    return Parameter(new_type, new_name)


def get_full_string(lines: list, start: int, end: int) -> str:

    wanted_lines = []

    for i in range(start, end):
        wanted_lines.append(lines[i])

    output_string = " ".join(wanted_lines)

    return output_string
