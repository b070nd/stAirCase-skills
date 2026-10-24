#!/usr/bin/env python3
"""Check the skills of this plugin: their form, their prose, and every stAirCase command they show.

A skill that tells a person to run `staircase seal --alow x` is worse than no skill, so every command in a code block or in inline code
is resolved against the real CLI (`staircase <command> --help`): the command and each flag must exist. The binary must be the version in
STAIRCASE_VERSION, the one the skills were written for.

The set is also kept whole: every skill is named sc-<folder>, is listed in plugin.json, mentioned by the router sc-ask, linked from the
README and has a docs page; a skill the assistant may not start itself (disable-model-invocation) is always written with the slash.

    python3 tools/check_skills.py [--root DIR] [--staircase PATH] [--allow-version-mismatch]
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys

DESCRIPTION_LIMIT = 1024
HIDDEN = re.compile("[­؜᠎​-‏ -‮⁠-⁤⁦-⁩﻿︀-︎\U000e0000-\U000e007f]")
EMOJI = re.compile("[ℹ↩↪↺↻⌚⌛⏩-⏺☀-➿⬀-⯿\U0001f000-\U0001faff]️?")
DASHES = {"—": "em dash", "–": "en dash"}
SHELL_FENCES = {"", "bash", "sh", "shell", "zsh"}
OPERATORS = {"&&", "||", "|", ";", ">", ">>", "<", "2>", "2>&1", "&"}
WORD = re.compile(r"[a-z][a-z0-9-]*")
PREFIX = "sc-"
ROUTER = "sc-ask"
# the sections of a docs page, in the order they must come; the first, third and last two are required
SECTIONS = ["## What it does", "## When to reach for it", "## Prerequisites", "## Common questions", "## It's working if", "## Where it fits"]
REQUIRED = {"## What it does", "## When to reach for it", "## It's working if", "## Where it fits"}
SKILL_REF = re.compile(r"`(/?)(sc-[a-z0-9-]+)`")
SKILL_CALL = re.compile(r'Skill tool with "([^"]+)"')


class Cli:
    """The staircase binary's help output, asked once per command."""

    def __init__(self, binary):
        self.binary = binary
        self._help = {}

    def help(self, path):
        key = tuple(path)
        if key not in self._help:
            try:
                done = subprocess.run([self.binary, *path, "--help"], capture_output=True, text=True, timeout=30)
                self._help[key] = done.stdout if done.returncode == 0 else None
            except (OSError, subprocess.TimeoutExpired):
                self._help[key] = None
        return self._help[key]

    def version(self):
        done = subprocess.run([self.binary, "version"], capture_output=True, text=True, timeout=30)
        return done.stdout.strip()

    def subcommands(self, path):
        text = self.help(path) or ""
        out, inside = set(), False
        for line in text.splitlines():
            if line.strip() == "Available Commands:":
                inside = True
            elif inside and not line.strip():
                break
            elif inside:
                out.add(line.split()[0])
        return out - {"help", "completion"} if path else out - {"completion"}

    def flags(self, path):
        text = self.help(path) or ""
        out = set()
        for line in text.splitlines():
            m = re.match(r"^\s+(?:(-\w), )?(--[\w-]+)", line)
            if m:
                out.update(g for g in m.groups() if g)
        return out


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    out = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = re.match(r"^([\w-]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return None


def shell_commands(tokens):
    """The staircase commands in one shell line: each is the tokens after 'staircase' up to the next operator."""
    segment, segments = [], []
    for tok in tokens + [";"]:
        if tok in OPERATORS:
            segments.append(segment)
            segment = []
        else:
            segment.append(tok)
    out = []
    for seg in segments:
        while seg and re.match(r"^[A-Z_][A-Z0-9_]*=", seg[0]):  # NAME=value staircase ...
            seg = seg[1:]
        if seg and seg[0] == "staircase":
            out.append(seg[1:])
    return out


def split(line):
    lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    lexer.commenters = "#"
    return list(lexer)


def check_command(cli, tokens, where):
    problems = []
    path, i = [], 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.startswith("-") or "<" in tok or not WORD.fullmatch(tok):
            break
        subs = cli.subcommands(path)
        if not subs:
            break  # a leaf command: what follows are its arguments
        if tok not in subs:
            problems.append(f"{where}: `staircase {' '.join(path + [tok])}`: {tok!r} is not a command (try: {', '.join(sorted(subs))})")
            return problems
        path.append(tok)
        i += 1
    if cli.help(path) is None:
        problems.append(f"{where}: `staircase {' '.join(path)}` is not a command")
        return problems
    known = cli.flags(path) | cli.flags([])
    for tok in tokens[i:]:
        if tok == "--":
            break
        if tok.startswith("--"):
            name = tok.split("=", 1)[0]
            if name not in known:
                problems.append(f"{where}: `staircase {' '.join(path)}` has no flag {name}")
        elif re.fullmatch(r"-[A-Za-z]", tok) and tok not in known:
            problems.append(f"{where}: `staircase {' '.join(path)}` has no flag {tok}")
    return problems


def markdown_commands(text):
    """Yield (line number, tokens) for each staircase command in shell code blocks and inline code."""
    lines = text.split("\n")
    fence, lang, i = False, "", 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^\s*```(\S*)", line)
        if m:
            fence, lang = (not fence), (m.group(1) if not fence else "")
            i += 1
            continue
        if fence:
            if lang in SHELL_FENCES:
                start, joined = i + 1, line.strip()
                while joined.endswith("\\") and i + 1 < len(lines):
                    i += 1
                    joined = joined[:-1].rstrip() + " " + lines[i].strip()
                joined = re.sub(r"^\$\s+", "", joined)
                try:
                    for cmd in shell_commands(split(joined)):
                        yield start, cmd
                except ValueError:
                    pass
        else:
            for span in re.findall(r"`([^`\n]+)`", line):
                if span.startswith("staircase "):
                    try:
                        for cmd in shell_commands(split(span)):
                            yield i + 1, cmd
                    except ValueError:
                        pass
        i += 1


def prose_problems(rel, text):
    problems = []
    for n, line in enumerate(text.split("\n"), 1):
        for ch, name in DASHES.items():
            if ch in line:
                problems.append(f"{rel}:{n}: an {name}: rewrite the sentence with a comma, colon or full stop")
        if EMOJI.search(line):
            problems.append(f"{rel}:{n}: an emoji or symbol: say it in words")
        if HIDDEN.search(line):
            problems.append(f"{rel}:{n}: a hidden character")
    return problems


def link_problems(root, path, rel, text):
    problems = []
    for n, line in enumerate(text.split("\n"), 1):
        for target in re.findall(r"\]\(([^)\s#]+)(?:#[^)]*)?\)", line):
            if re.match(r"^[a-z]+:", target):
                continue
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), target))):
                problems.append(f"{rel}:{n}: the link {target} does not exist")
    return problems


def reference_problems(rel, text, invoked, slash_rule):
    """Check how a file names the skills. invoked maps each skill to True when only the person may start it.
    In a skill (slash_rule), such a skill is always written with the slash, so it reads as something to tell the person."""
    problems = []
    for n, line in enumerate(text.split("\n"), 1):
        for slash, name in SKILL_REF.findall(line):
            if name not in invoked:
                problems.append(f"{rel}:{n}: `{slash}{name}` is not a skill of this plugin")
            elif slash_rule and invoked[name] and not slash:
                problems.append(f"{rel}:{n}: {name} is started by the person only: write it `/{name}`")
        for name in SKILL_CALL.findall(line):
            if name not in invoked:
                problems.append(f"{rel}:{n}: the Skill tool is told to call {name}, which is not a skill of this plugin")
            elif invoked[name]:
                problems.append(f"{rel}:{n}: the Skill tool cannot call {name}: only the person starts it, so tell them to run /{name}")
    return problems


def docs_problems(root, names):
    """Each skill has a docs page with the same sections in the same order, and no page is left without its skill."""
    problems = []
    docs = os.path.join(root, "docs")
    pages = sorted(f[:-3] for f in os.listdir(docs) if f.endswith(".md")) if os.path.isdir(docs) else []
    for name in names:
        if name not in pages:
            problems.append(f"docs/{name}.md: the skill {name} has no docs page")
    for page in pages:
        if page not in names:
            problems.append(f"docs/{page}.md: a docs page without a skill")
            continue
        rel = f"docs/{page}.md"
        text = read(os.path.join(docs, page + ".md"))
        headings = [(n, line.rstrip()) for n, line in enumerate(text.split("\n"), 1) if line.startswith("#") and not line.startswith("###")]
        found = [h for _, h in headings]
        for n, h in headings:
            if h.startswith("# "):
                problems.append(f"{rel}:{n}: a docs page has no H1: its title is its file name")
            elif h not in SECTIONS:
                problems.append(f"{rel}:{n}: {h!r} is not one of the sections: {', '.join(SECTIONS)}")
        for h in sorted(REQUIRED - set(found)):
            problems.append(f"{rel}: the section {h!r} is missing")
        known = [h for h in found if h in SECTIONS]
        if known != sorted(known, key=SECTIONS.index):
            problems.append(f"{rel}: the sections are out of order, they come as: {', '.join(SECTIONS)}")
        if page != ROUTER and "(sc-ask.md)" not in text:
            problems.append(f"{rel}: 'Where it fits' must link the router: [sc-ask](sc-ask.md)")
    return problems


def check(root, binary, allow_version_mismatch=False):
    problems = []
    cli = Cli(binary)
    skills_dir = os.path.join(root, "skills")
    names = sorted(d for d in os.listdir(skills_dir) if os.path.isfile(os.path.join(skills_dir, d, "SKILL.md"))) if os.path.isdir(skills_dir) else []

    want = read(os.path.join(root, "STAIRCASE_VERSION")).strip()
    got = cli.version()
    if want not in got and not allow_version_mismatch:
        problems.append(f"STAIRCASE_VERSION: the skills are written for {want}, but the staircase on this machine says {got!r}")

    with open(os.path.join(root, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        listed = set(json.load(f).get("skills", []))
    expected = {f"./skills/{n}" for n in names}
    for missing in sorted(expected - listed):
        problems.append(f".claude-plugin/plugin.json: the skill {missing} is not listed in plugin.json")
    for extra in sorted(listed - expected):
        problems.append(f".claude-plugin/plugin.json: {extra} is listed but has no SKILL.md")

    metas, invoked = {}, {}
    for name in names:
        metas[name] = frontmatter(read(os.path.join(skills_dir, name, "SKILL.md"))) or {}
        invoked[name] = metas[name].get("disable-model-invocation") == "true"

    for name in names:
        path = os.path.join(skills_dir, name, "SKILL.md")
        rel = f"skills/{name}/SKILL.md"
        text = read(path)
        meta = frontmatter(text)
        if not name.startswith(PREFIX):
            problems.append(f"{rel}: the folder must start with {PREFIX}")
        if meta is None:
            problems.append(f"{rel}:1: no frontmatter (--- name: ... description: ... ---)")
        else:
            if meta.get("name") != name:
                problems.append(f"{rel}:2: the name is {meta.get('name')!r}, but the folder is {name!r}")
            flag = meta.get("disable-model-invocation")
            if flag not in (None, "true"):
                problems.append(f"{rel}: disable-model-invocation is {flag!r}: it is either true or left out")
            desc = meta.get("description", "")
            if not desc:
                problems.append(f"{rel}:3: no description")
            else:
                if invoked[name] and "Use when" in desc:
                    problems.append(f"{rel}:3: a skill only the person starts has a description for people: take out \"Use when ...\"")
                if not invoked[name] and "Use when" not in desc:
                    problems.append(f"{rel}:3: the description must say when to use the skill (\"Use when ...\")")
                if len(desc) > DESCRIPTION_LIMIT:
                    problems.append(f"{rel}:3: the description is {len(desc)} characters, the limit is {DESCRIPTION_LIMIT}")
        problems += prose_problems(rel, text)
        problems += link_problems(root, path, rel, text)
        problems += reference_problems(rel, text, invoked, True)
        for line, cmd in markdown_commands(text):
            problems += check_command(cli, cmd, f"{rel}:{line}")

    if names:
        if ROUTER not in names:
            problems.append(f"skills/{ROUTER}/SKILL.md: the router is missing")
        else:
            router = read(os.path.join(skills_dir, ROUTER, "SKILL.md"))
            for name in names:
                if name != ROUTER and not re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", router):
                    problems.append(f"skills/{ROUTER}/SKILL.md: the router does not mention {name}")

    readme = os.path.join(root, "README.md")
    readme_text = read(readme) if os.path.isfile(readme) else ""
    for name in names:
        if f"(skills/{name}/SKILL.md)" not in readme_text:
            problems.append(f"README.md: no link to skills/{name}/SKILL.md")

    problems += docs_problems(root, names)

    files = [("README.md", readme), ("CHANGELOG.md", os.path.join(root, "CHANGELOG.md"))]
    docs = os.path.join(root, "docs")
    if os.path.isdir(docs):
        files += [(f"docs/{f}", os.path.join(docs, f)) for f in sorted(os.listdir(docs)) if f.endswith(".md")]
    for rel, p in files:
        if os.path.isfile(p):
            text = read(p)
            problems += prose_problems(rel, text)
            problems += link_problems(root, p, rel, text)
            if rel != "CHANGELOG.md":
                problems += reference_problems(rel, text, invoked, False)
                for line, cmd in markdown_commands(text):
                    problems += check_command(cli, cmd, f"{rel}:{line}")
    return problems


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.dirname(here))
    ap.add_argument("--staircase", default=os.environ.get("STAIRCASE_BIN", "staircase"))
    ap.add_argument("--allow-version-mismatch", action="store_true")
    args = ap.parse_args(argv)
    problems = check(args.root, args.staircase, args.allow_version_mismatch)
    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("skills ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
