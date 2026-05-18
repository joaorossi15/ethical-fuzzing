import random
import string

def mutate_canary_surface(value: str, canary_type: str) -> str:
    v = value

    def maybe(prob: float) -> bool:
        return random.random() < prob

    def toggle_case(s: str) -> str:
        mode = random.choice(["lower", "upper", "title"])
        if mode == "lower":
            return s.lower()
        if mode == "upper":
            return s.upper()
        return s.title()

    def add_quotes(s: str) -> str:
        q = random.choice(["'", '"', "`"])
        return f"{q}{s}{q}"

    def add_label(s: str) -> str:
        label = random.choice(["code", "ref", "id", "token", "key", "pwd"])
        sep = random.choice([": ", "=", " -> ", " is "])
        return f"{label}{sep}{s}"

    def punctuation_wrap(s: str) -> str:
        left, right = random.choice([("(", ")"), ("[", "]"), ("{", "}"), ("<", ">")])
        return f"{left}{s}{right}"

    def sep_variation(s: str) -> str:
        if "-" in s or "_" in s:
            frm, to = random.choice([("-", "_"), ("_", "-"), ("-", " "), ("_", " ")])
            return s.replace(frm, to)
        if len(s) >= 6 and maybe(0.5):
            k = random.choice([2, 3, 4])
            return " ".join([s[i:i+k] for i in range(0, len(s), k)])
        return s

    def confusable_substitution(s: str) -> str:
        conf = {
            "0": ["O", "o"],
            "O": ["0"],
            "o": ["0"],
            "1": ["l", "I"],
            "l": ["1", "I"],
            "I": ["1", "l"],
            "5": ["S", "s"],
            "S": ["5"],
            "s": ["5"],
            "2": ["Z", "z"],
            "Z": ["2"],
            "z": ["2"],
        }
        idxs = [i for i, ch in enumerate(s) if ch in conf]
        if not idxs:
            return s
        i = random.choice(idxs)
        ch = s[i]
        rep = random.choice(conf[ch])
        return s[:i] + rep + s[i+1:]

    def transpose_adjacent(s: str) -> str:
        if len(s) < 4:
            return s
        i = random.randint(1, len(s) - 2)
        return s[:i] + s[i+1] + s[i] + s[i+2:]

    def single_typo(s: str) -> str:
        if len(s) < 3:
            return s
        op = random.choice(["replace", "delete", "dup"])
        i = random.randint(0, len(s) - 1)
        if op == "delete":
            return s[:i] + s[i+1:]
        if op == "dup":
            return s[:i] + s[i] + s[i:]
        ch = s[i]
        if ch.isdigit():
            r = random.choice(string.digits)
        elif ch.isalpha():
            r = random.choice(string.ascii_letters)
        else:
            r = random.choice(["-", "_"])
        return s[:i] + r + s[i+1:]

    def number_style(n: str) -> str:
        choices = []
        choices.append(lambda x: x)  
        choices.append(lambda x: x.lstrip("0") if len(x) > 1 else x) 
        choices.append(lambda x: f"{int(x):,}".replace(",", random.choice([".", " "])) if x.isdigit() else x)
        choices.append(lambda x: f"{x} ") 
        choices.append(lambda x: f" {x}")  
        choices.append(lambda x: add_label(x))
        choices.append(lambda x: punctuation_wrap(x))
        if maybe(0.3):
            choices.append(lambda x: single_typo(x))
        return random.choice(choices)(n)

    def word_style(w: str) -> str:
        choices = []
        choices.append(lambda x: x)
        choices.append(lambda x: toggle_case(x))
        choices.append(lambda x: add_quotes(x))
        choices.append(lambda x: punctuation_wrap(x))
        if maybe(0.35):
            choices.append(lambda x: single_typo(x))
        return random.choice(choices)(w)

    def id_style(s: str) -> str:
        choices = []
        choices.append(lambda x: x)
        choices.append(lambda x: toggle_case(x))
        choices.append(lambda x: sep_variation(x))
        choices.append(lambda x: punctuation_wrap(x))
        choices.append(lambda x: add_label(x))
        if maybe(0.4):
            choices.append(lambda x: confusable_substitution(x))
        if maybe(0.25):
            choices.append(lambda x: transpose_adjacent(x))
        if maybe(0.2):
            choices.append(lambda x: single_typo(x))
        return random.choice(choices)(s)

    t = (canary_type or "").lower()

    if t in {"number", "numeric"}:
        return number_style(v)

    if t in {"word", "token_word"}:
        return word_style(v)

    if t in {"id_random", "id"}:
        return id_style(v)

    if t in {"composite"}:
        out = v
        ops = [toggle_case, sep_variation, confusable_substitution, punctuation_wrap, add_label]
        if maybe(0.35):
            ops.append(single_typo)
        out = random.choice(ops)(out)
        if maybe(0.25):
            out = random.choice(ops)(out)
        return out

    return id_style(v)
