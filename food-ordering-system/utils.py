"""Small input and display helpers."""


def ask_int(prompt, lo=None, hi=None):
    while True:
        try:
            v = int(input(prompt).strip())
        except ValueError:
            print("Please enter a whole number.")
            continue
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            print("Value out of range.")
            continue
        return v


def ask_float(prompt, minimum=0.01):
    while True:
        try:
            v = float(input(prompt).strip())
        except ValueError:
            print("Please enter a number.")
            continue
        if v < minimum:
            print(f"Must be at least {minimum}.")
            continue
        return v


def ask_text(prompt, allow_blank=False):
    while True:
        v = input(prompt).strip()
        if v or allow_blank:
            return v
        print("This cannot be empty.")


def ask_yes_no(prompt):
    return input(prompt + " (y/n): ").strip().lower() == "y"


def print_table(headers, rows):
    if not rows:
        print("  (nothing to show)")
        return
    rows = [[str(c) for c in r] for r in rows]
    widths = [max(len(str(h)), *(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    line = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(line)
    print("-" * len(line))
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))
