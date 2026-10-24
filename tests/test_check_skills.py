"""Tests for tools/check_skills.py. A fake `staircase` prints help in the shape cobra uses, so no real binary is needed."""
import json
import os
import stat
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import check_skills  # noqa: E402

FAKE = """#!/bin/sh
case "$*" in
"version") echo "stAirCase v1.3.0 (commit abc, built now)" ;;
"--help") printf 'Available Commands:\\n  project     Manage projects\\n  seal        Commit staged changes\\n  vendor      Manage vendors\\n  help        Help\\n\\nFlags:\\n  -h, --help   help\\n' ;;
"seal --help") printf 'Usage:\\n  staircase seal [flags]\\n\\nFlags:\\n      --allow stringArray   paths\\n  -y, --yes   start\\n  -h, --help   help\\n\\nGlobal Flags:\\n      --dir string   Workspace directory\\n' ;;
"project --help") printf 'Available Commands:\\n  add      Register\\n  profile  Profile\\n\\nFlags:\\n  -h, --help   help\\n\\nGlobal Flags:\\n      --dir string   Workspace directory\\n' ;;
"project profile --help") printf 'Available Commands:\\n  set   Set\\n  show  Show\\n\\nFlags:\\n  -h, --help   help\\n' ;;
"project profile set --help") printf 'Usage:\\n  staircase project profile set\\n\\nFlags:\\n      --protect stringArray   paths\\n  -h, --help   help\\n' ;;
"project add --help"|"project profile show --help") printf 'Flags:\\n  -h, --help   help\\n' ;;
"vendor --help") printf 'Available Commands:\\n  add   Add\\n\\nFlags:\\n  -h, --help   help\\n' ;;
"vendor add --help") printf 'Flags:\\n  -h, --help   help\\n' ;;
*) echo "Error: unknown command" >&2; exit 1 ;;
esac
"""

GOOD = """---
name: sealing
description: Seal what an agent changed. Use when the user has staged changes made by an agent in their own checkout.
---

# Sealing

Run this in your terminal, it asks you:

```bash
staircase seal --allow "src/**" -y
```
"""


class Repo:
    created = []

    def __init__(self, skills=None, listed=None, version="v1.3.0"):
        self.dir = tempfile.TemporaryDirectory()
        Repo.created.append(self)
        self.root = self.dir.name
        skills = {"sealing": GOOD} if skills is None else skills
        os.makedirs(os.path.join(self.root, ".claude-plugin"))
        for name, body in skills.items():
            os.makedirs(os.path.join(self.root, "skills", name))
            with open(os.path.join(self.root, "skills", name, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write(body)
        listed = ["./skills/" + n for n in skills] if listed is None else listed
        with open(os.path.join(self.root, ".claude-plugin", "plugin.json"), "w") as f:
            json.dump({"name": "x", "skills": listed}, f)
        with open(os.path.join(self.root, "STAIRCASE_VERSION"), "w") as f:
            f.write(version + "\n")
        self.bin = os.path.join(self.root, "staircase")
        with open(self.bin, "w") as f:
            f.write(FAKE)
        os.chmod(self.bin, os.stat(self.bin).st_mode | stat.S_IXUSR)

    def check(self, **kw):
        return check_skills.check(self.root, self.bin, **kw)


def skill(body, name="sealing", desc="Seal changes. Use when the user wants it."):
    return f"---\nname: {name}\ndescription: {desc}\n---\n\n{body}\n"


class CheckSkills(unittest.TestCase):
    def tearDown(self):
        while Repo.created:
            Repo.created.pop().dir.cleanup()

    def assertProblem(self, problems, *words):
        text = "\n".join(problems)
        for w in words:
            self.assertIn(w, text)

    def test_a_correct_skill_passes(self):
        self.assertEqual(Repo().check(), [])

    def test_the_name_must_be_the_folder(self):
        r = Repo({"sealing": skill("x", name="other")})
        self.assertProblem(r.check(), "sealing/SKILL.md", "name", "other")

    def test_the_description_must_say_when_to_use_it(self):
        r = Repo({"sealing": skill("x", desc="Seals changes.")})
        self.assertProblem(r.check(), "sealing/SKILL.md", "Use when")

    def test_the_description_has_a_limit(self):
        r = Repo({"sealing": skill("x", desc="Use when " + "a" * 1100)})
        self.assertProblem(r.check(), "1024")

    def test_the_plugin_lists_every_skill_and_only_those(self):
        r = Repo(listed=[])
        self.assertProblem(r.check(), "sealing", "plugin.json")
        r = Repo(listed=["./skills/sealing", "./skills/ghost"])
        self.assertProblem(r.check(), "ghost")

    def test_an_unknown_command_is_named_with_its_line(self):
        r = Repo({"sealing": skill("```bash\nstaircase sael\n```")})
        self.assertProblem(r.check(), "sealing/SKILL.md:7", "sael")

    def test_a_typo_in_a_subcommand_of_a_group_is_caught(self):
        r = Repo({"sealing": skill("```bash\nstaircase project profil show 3\n```")})
        self.assertProblem(r.check(), "profil")

    def test_a_positional_argument_after_a_leaf_command_is_fine(self):
        r = Repo({"sealing": skill("```bash\nstaircase vendor add acme\nstaircase project profile set 3 --protect \"tests/**\"\n```")})
        self.assertEqual(r.check(), [])

    def test_an_unknown_flag_is_caught(self):
        r = Repo({"sealing": skill("```bash\nstaircase seal --nope\n```")})
        self.assertProblem(r.check(), "--nope", "staircase seal")

    def test_a_global_flag_and_a_short_flag_are_known(self):
        r = Repo({"sealing": skill("```bash\nstaircase seal --dir /tmp/ws -y\n```")})
        self.assertEqual(r.check(), [])

    def test_a_flag_with_a_value_after_equals_is_checked_by_name(self):
        r = Repo({"sealing": skill("```bash\nstaircase seal --allow=src/**\n```")})
        self.assertEqual(r.check(), [])

    def test_placeholders_and_continued_lines(self):
        r = Repo({"sealing": skill("```bash\nstaircase seal \\\n  --allow \"<path>\" \\\n  --nope\n```")})
        self.assertProblem(r.check(), "--nope")

    def test_a_command_in_inline_code_is_checked(self):
        r = Repo({"sealing": skill("Run `staircase sael` now, or `staircase seal --allow x`.")})
        self.assertProblem(r.check(), "sael")
        self.assertNotIn("--allow", "\n".join(r.check()))

    def test_output_blocks_are_not_commands(self):
        r = Repo({"sealing": skill("```text\nstaircase nonsense happened\n```")})
        self.assertEqual(r.check(), [])

    def test_a_dollar_prompt_is_ignored(self):
        r = Repo({"sealing": skill("```bash\n$ staircase seal\n```")})
        self.assertEqual(r.check(), [])

    def test_em_dashes_and_emoji_are_refused(self):
        r = Repo({"sealing": skill("This — that.")})
        self.assertProblem(r.check(), "sealing/SKILL.md", "em dash")
        r = Repo({"sealing": skill("Done ✅")})
        self.assertProblem(r.check(), "emoji")

    def test_hidden_characters_are_refused(self):
        r = Repo({"sealing": skill("zero​width")})
        self.assertProblem(r.check(), "hidden")
        r = Repo({"sealing": skill("tag\U000e0041char")})
        self.assertProblem(r.check(), "hidden")

    def test_the_binary_must_be_the_version_the_skills_were_written_for(self):
        r = Repo(version="v1.2.0")
        self.assertProblem(r.check(), "v1.2.0", "v1.3.0")
        self.assertEqual(r.check(allow_version_mismatch=True), [])

    def test_a_relative_link_must_exist(self):
        r = Repo({"sealing": skill("See [more](references/more.md) and [site](https://example.com).")})
        self.assertProblem(r.check(), "references/more.md")
        os.makedirs(os.path.join(r.root, "skills", "sealing", "references"))
        with open(os.path.join(r.root, "skills", "sealing", "references", "more.md"), "w") as f:
            f.write("x")
        self.assertEqual(r.check(), [])


if __name__ == "__main__":
    unittest.main()
