#!/usr/bin/env python3
"""Check the skills of this plugin: their form, their prose, and every stAirCase command they show.

A skill that tells a person to run `staircase seal --alow x` is worse than no skill, so every command in a code block or in inline code
is resolved against the real CLI (`staircase <command> --help`): the command and each flag must exist. The binary must be the version in
STAIRCASE_VERSION, the one the skills were written for.

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

    for name in names:
        path = os.path.join(skills_dir, name, "SKILL.md")
        rel = f"skills/{name}/SKILL.md"
        text = read(path)
        meta = frontmatter(text)
        if meta is None:
            problems.append(f"{rel}:1: no frontmatter (--- name: ... description: ... ---)")
        else:
            if meta.get("name") != name:
                problems.append(f"{rel}:2: the name is {meta.get('name')!r}, but the folder is {name!r}")
            desc = meta.get("description", "")
            if not desc:
                problems.append(f"{rel}:3: no description")
            else:
                if "Use when" not in desc:
                    problems.append(f"{rel}:3: the description must say when to use the skill (\"Use when ...\")")
                if len(desc) > DESCRIPTION_LIMIT:
                    problems.append(f"{rel}:3: the description is {len(desc)} characters, the limit is {DESCRIPTION_LIMIT}")
        problems += prose_problems(rel, text)
        problems += link_problems(root, path, rel, text)
        for line, cmd in markdown_commands(text):
            problems += check_command(cli, cmd, f"{rel}:{line}")

    for extra in ("README.md", "CHANGELOG.md"):
        p = os.path.join(root, extra)
        if os.path.isfile(p):
            text = read(p)
            problems += prose_problems(extra, text)
            problems += link_problems(root, p, extra, text)
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
