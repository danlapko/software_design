import re
import logging as log


def clip_both_quotes(s):
    """Megafunction. Main goal - detect correct quotes places. Returns list
    of 3 list and 3 flags: [], flag1, [], flag2 ,[], flag3
    1st list) places of single quotes in string s in format:
    [(a1,b1),(a2,b2),..] where (a_,b_) - alternate intervals of
    substrings which included in single quotes and intervals between single
    quotes, flag1 - flag of which interval the first
    2nd) - the same but for double quotes
    3rd) - the same but for both types of quotes"""

    def validate_quotes(s):
        singles = []
        doubles = []
        i = 0

        while i < len(s):
            if s[i] == '\\':
                i += 2
                continue

            if s[i] == "'":
                a = i
                i += 1
                while i < len(s) and s[i] != "'":
                    i += 1
                if i >= len(s):
                    raise AttributeError("unclosed single quotes")
                singles.append((a, i))

            if s[i] == '"':
                a = i
                i += 1
                while i < len(s) and s[i] != '"':
                    if s[i] == '\\':
                        i += 2
                    else:
                        i += 1
                if i >= len(s):
                    raise AttributeError("unclosed double quotes")
                doubles.append((a, i))

            i += 1
            return singles, doubles

    singles, doubles = validate_quotes(s)

    # ----------SINGLES---------
    s_n_singles = set()
    sing_first = True
    for (a, b) in singles:
        s_n_singles.add(a)
        s_n_singles.add(b)
    s_n_singles.discard((len(s) - 1))
    if 0 not in s_n_singles:
        s_n_singles.add(0)
        sing_first = False
    s_n_singles.add(len(s))
    sor = sorted(s_n_singles)
    singles = []
    for i in range(1, len(sor)):
        singles.append((sor[i - 1], sor[i]))

    # ----------Doubles---------
    s_n_doubles = set()
    doub_first = True
    for (a, b) in doubles:
        s_n_doubles.add(a)
        s_n_doubles.add(b)
    s_n_doubles.discard(len(s) - 1)
    if 0 not in s_n_doubles:
        s_n_doubles.add(0)
        doub_first = False
    s_n_doubles.add(len(s))
    sor = sorted(s_n_doubles)
    doubles = []
    for i in range(1, len(sor)):
        doubles.append((sor[i - 1], sor[i]))

    # ----------BOTH---------
    s_n_both = set()
    for (a, b) in singles:
        s_n_both.add(a)
        s_n_both.add(b)
    for (a, b) in doubles:
        s_n_both.add(a)
        s_n_both.add(b)

    if 0 not in s_n_both:
        s_n_both.add(0)

    both_first = sing_first or doub_first
    if len(s) not in s_n_both:
        s_n_both.add(len(s))

    sor = sorted(s_n_both)
    both = []
    for i in range(1, len(sor)):
        both.append((sor[i - 1], sor[i]))

    return singles, sing_first, doubles, doub_first, both, both_first


def strip_quotes(s):
    if not s:
        return ""

    singles, _, doubles, _, boths, both_first = clip_both_quotes(s)
    res = ""

    for i in range(len(boths)):
        a, b = boths[i]
        if (s[a] in "'\"") and b - 1 >= 0 and (s[b - 1] in "'\""):
            res += s[a + 1:b - 1]
        elif s[a] in "'\"":
            res += s[a + 1:b]
        elif b - 1 >= 0 and s[b - 1] in "'\"":
            res += s[a:b - 1]
        else:
            res += s[a:b]

    return res


def split_by_spaces(s):
    """splitting string vy spaces which are not in quotes intervals"""
    if not s:
        return []
    _, _, _, _, boths, both_first = clip_both_quotes(s)
    res = []
    block = ""
    for i in range(len(boths)):
        a, b = boths[i]

        if i % 2 == (not both_first):
            block += s[a: b]
        else:
            blocks = s[a:b].split(" ")
            for tmp in blocks[:-1]:
                block += tmp
                res.append(block)
                block = ""
            block += blocks[-1]

    res.append(block)
    return res


def substitute_dollar(s, envs):
    """substituting dollars (environment anchors) by environment variables (
    does nothing in single quotes) """
    singles, sing_first, _, _, _, _ = clip_both_quotes(s)

    pattern_keys = "|".join(envs.keys())
    default_pattern = re.compile(r'\$(?!(' + pattern_keys + r')(?=\b))\w*')
    log.info("default_pattern: " + str(default_pattern))

    res = ""
    for i in range(len(singles)):
        a, b = singles[i]
        l = s[a:b]

        if (i + (not sing_first)) % 2 == 0:
            res += l
            continue

        l = re.sub(default_pattern, "", l)
        log.info("applied def_pattern: " + l)

        log.info(envs)
        for key, val in envs.items():
            pattern = r'\$' + key + r'\b'
            log.info("pattern: " + pattern)
            l = re.sub(
                # "\$" + key + "(?=[\s\W\b`\-=~!@$\$#%^&*()+\[\]{};\\:\"|<,.\/<>?])",
                pattern,
                val,
                l)
        res += l

    return res


def split_by_pipeline(s):
    """splitting by pipelines ('|') whcih are not in quotes"""
    _, _, _, _, boths, both_first = clip_both_quotes(s)

    blocks = []
    block = ""
    for i in range(len(boths)):
        a, b = boths[i]
        s_tmp = s[a:b]
        if i % 2 == (not both_first):
            block += s_tmp
        else:
            tmp = s_tmp.split('|')
            for segm in tmp[:-1]:
                block += segm
                blocks.append(block)
                block = ""
            block += tmp[-1]

    blocks.append(block)

    return blocks


def block_to_cmd_args(block):
    """splitting the block string, which already doesn't contain pipelines,
    into command and args """

    block = block.strip()
    _, _, _, _, boths, both_first = clip_both_quotes(block)

    for i in range(both_first, len(boths), 2):
        a, b = boths[i]
        tmp = block[a:b]
        for i in range(len(tmp)):
            if tmp[i] == " ":
                return strip_quotes(block[:a + i]), block[a + i:]

    return strip_quotes(block), ""


def is_assignment(block):
    """verifing if block is assigment operation and returns two operands if
    true """

    if not block.strip():
        return False
    _, _, _, _, boths, both_first = clip_both_quotes(block)
    a, b = boths[0]
    tmp = block[a:b]
    if both_first or "=" not in block[a:b]:
        return False

    tmp = tmp.split("=")
    if len(tmp) != 2 or not tmp[0].isalpha():
        raise AttributeError("incorrect assigment")
    return tmp
