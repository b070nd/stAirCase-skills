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
name: sc-sealing
description: Seal what an agent changed. Use when the user has staged changes made by an agent in their own checkout.
---

# Sealing

Run this in your terminal, it asks you:

```bash
staircase seal --allow "src/**" -y
```
"""


PAGE = """## What it does

It does one thing.

## When to reach for it

When you need it.

## It's working if

- it works

## Where it fits

A step. The map is [sc-ask](sc-ask.md).
"""


def router(names):
    return "---\nname: sc-ask\ndescription: Ask which skill fits.\ndisable-model-invocation: true\n---\n\n" + "\n".join(f"- `/{n}`" for n in names) + "\n"


class Repo:
    """A whole valid repository: the skills, the router, the README and a docs page for each. The arguments take pieces away or change them."""
    created = []

    def __init__(self, skills=None, listed=None, version="v1.3.0", readme=True, docs=True, extra_docs=None):
        self.dir = tempfile.TemporaryDirectory()
        Repo.created.append(self)
        self.root = self.dir.name
        skills = dict({"sc-sealing": GOOD} if skills is None else skills)
        if "sc-ask" not in skills:
            skills["sc-ask"] = router([n for n in skills])
        os.makedirs(os.path.join(self.root, ".claude-plugin"))
        for name, body in skills.items():
            os.makedirs(os.path.join(self.root, "skills", name))
            with open(os.path.join(self.root, "skills", name, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write(body)
        if readme:
            with open(os.path.join(self.root, "README.md"), "w") as f:
                f.write("# Skills\n\n" + "\n".join(f"- [`{n}`](skills/{n}/SKILL.md)" for n in skills) + "\n")
        if docs:
            os.makedirs(os.path.join(self.root, "docs"))
            for name in skills:
                with open(os.path.join(self.root, "docs", name + ".md"), "w") as f:
                    f.write(PAGE)
        for name, body in (extra_docs or {}).items():
            os.makedirs(os.path.join(self.root, "docs"), exist_ok=True)
            with open(os.path.join(self.root, "docs", name + ".md"), "w") as f:
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


def skill(body, name="sc-sealing", desc="Seal changes. Use when the user wants it."):
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
        r = Repo({"sc-sealing": skill("x", name="other")})
        self.assertProblem(r.check(), "sc-sealing/SKILL.md", "name", "other")

    def test_the_description_must_say_when_to_use_it(self):
        r = Repo({"sc-sealing": skill("x", desc="Seals changes.")})
        self.assertProblem(r.check(), "sc-sealing/SKILL.md", "Use when")

    def test_the_description_has_a_limit(self):
        r = Repo({"sc-sealing": skill("x", desc="Use when " + "a" * 1100)})
        self.assertProblem(r.check(), "1024")

    def test_the_plugin_lists_every_skill_and_only_those(self):
        r = Repo(listed=[])
        self.assertProblem(r.check(), "sc-sealing", "plugin.json")
        r = Repo(listed=["./skills/sc-sealing", "./skills/ghost"])
        self.assertProblem(r.check(), "ghost")

    def test_an_unknown_command_is_named_with_its_line(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase sael\n```")})
        self.assertProblem(r.check(), "sc-sealing/SKILL.md:7", "sael")

    def test_a_typo_in_a_subcommand_of_a_group_is_caught(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase project profil show 3\n```")})
        self.assertProblem(r.check(), "profil")

    def test_a_positional_argument_after_a_leaf_command_is_fine(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase vendor add acme\nstaircase project profile set 3 --protect \"tests/**\"\n```")})
        self.assertEqual(r.check(), [])

    def test_an_unknown_flag_is_caught(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase seal --nope\n```")})
        self.assertProblem(r.check(), "--nope", "staircase seal")

    def test_a_global_flag_and_a_short_flag_are_known(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase seal --dir /tmp/ws -y\n```")})
        self.assertEqual(r.check(), [])

    def test_a_flag_with_a_value_after_equals_is_checked_by_name(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase seal --allow=src/**\n```")})
        self.assertEqual(r.check(), [])

    def test_placeholders_and_continued_lines(self):
        r = Repo({"sc-sealing": skill("```bash\nstaircase seal \\\n  --allow \"<path>\" \\\n  --nope\n```")})
        self.assertProblem(r.check(), "--nope")

    def test_a_command_in_inline_code_is_checked(self):
        r = Repo({"sc-sealing": skill("Run `staircase sael` now, or `staircase seal --allow x`.")})
        self.assertProblem(r.check(), "sael")
        self.assertNotIn("--allow", "\n".join(r.check()))

    def test_output_blocks_are_not_commands(self):
        r = Repo({"sc-sealing": skill("```text\nstaircase nonsense happened\n```")})
        self.assertEqual(r.check(), [])

    def test_a_dollar_prompt_is_ignored(self):
        r = Repo({"sc-sealing": skill("```bash\n$ staircase seal\n```")})
        self.assertEqual(r.check(), [])

    def test_em_dashes_and_emoji_are_refused(self):
        r = Repo({"sc-sealing": skill("This — that.")})
        self.assertProblem(r.check(), "sc-sealing/SKILL.md", "em dash")
        r = Repo({"sc-sealing": skill("Done ✅")})
        self.assertProblem(r.check(), "emoji")

    def test_hidden_characters_are_refused(self):
        r = Repo({"sc-sealing": skill("zero​width")})
        self.assertProblem(r.check(), "hidden")
        r = Repo({"sc-sealing": skill("tag\U000e0041char")})
        self.assertProblem(r.check(), "hidden")

    def test_the_binary_must_be_the_version_the_skills_were_written_for(self):
        r = Repo(version="v1.2.0")
        self.assertProblem(r.check(), "v1.2.0", "v1.3.0")
        self.assertEqual(r.check(allow_version_mismatch=True), [])

    def test_a_relative_link_must_exist(self):
        r = Repo({"sc-sealing": skill("See [more](references/more.md) and [site](https://example.com).")})
        self.assertProblem(r.check(), "references/more.md")
        os.makedirs(os.path.join(r.root, "skills", "sc-sealing", "references"))
        with open(os.path.join(r.root, "skills", "sc-sealing", "references", "more.md"), "w") as f:
            f.write("x")
        self.assertEqual(r.check(), [])

def person_only(body="x", name="sc-away", desc="Start a task and leave."):
    return f"---\nname: {name}\ndescription: {desc}\ndisable-model-invocation: true\n---\n\n{body}\n"


class WholeSet(unittest.TestCase):
    """The rules that keep the set whole: names, invocation, the router, the README and the docs."""
    tearDown = CheckSkills.tearDown
    assertProblem = CheckSkills.assertProblem

    def test_every_skill_starts_with_the_prefix(self):
        r = Repo({"sealing": skill("x", name="sealing")})
        self.assertProblem(r.check(), "skills/sealing/SKILL.md", "sc-")

    def test_a_skill_only_the_person_starts_has_no_use_when(self):
        r = Repo({"sc-away": person_only(desc="Start a task. Use when you leave."), "sc-sealing": GOOD})
        self.assertProblem(r.check(), "sc-away/SKILL.md:3", "for people")
        self.assertEqual(Repo({"sc-away": person_only(), "sc-sealing": GOOD}).check(), [])

    def test_the_flag_is_true_or_absent(self):
        bad = person_only().replace("disable-model-invocation: true", "disable-model-invocation: yes")
        r = Repo({"sc-away": bad, "sc-sealing": GOOD})
        self.assertProblem(r.check(), "disable-model-invocation", "yes")

    def test_a_person_only_skill_is_written_with_the_slash_in_a_skill(self):
        away = {"sc-away": person_only(), "sc-sealing": skill("Ask the user to run `sc-away`.")}
        self.assertProblem(Repo(away).check(), "sc-sealing/SKILL.md", "`/sc-away`")
        away["sc-sealing"] = skill("Ask the user to run `/sc-away`.")
        self.assertEqual(Repo(away).check(), [])

    def test_the_skill_tool_may_not_call_a_person_only_skill(self):
        r = Repo({"sc-away": person_only(), "sc-sealing": skill('Call the Skill tool with "sc-away".')})
        self.assertProblem(r.check(), "cannot call sc-away", "/sc-away")
        r = Repo({"sc-away": person_only(), "sc-sealing": skill('Call the Skill tool with "sc-ghost".')})
        self.assertProblem(r.check(), "sc-ghost")
        r = Repo({"sc-away": person_only(), "sc-sealing": skill('Call the Skill tool with "sc-away-no".')})
        self.assertProblem(r.check(), "sc-away-no")

    def test_a_model_invoked_skill_may_be_called_and_named_either_way(self):
        r = Repo({"sc-away": person_only(), "sc-sealing": skill('Call the Skill tool with "sc-sealing". See `sc-sealing` or `/sc-sealing`.')})
        self.assertEqual(r.check(), [])

    def test_a_skill_that_does_not_exist_cannot_be_named(self):
        r = Repo({"sc-sealing": skill("See `sc-ghost`.")})
        self.assertProblem(r.check(), "sc-ghost", "not a skill")

    def test_the_router_must_exist_and_mention_every_skill(self):
        r = Repo({"sc-sealing": GOOD, "sc-ask": router([])})
        self.assertProblem(r.check(), "router does not mention sc-sealing")
        # a longer name does not count as a mention of a shorter one
        r = Repo({"sc-sealing": GOOD, "sc-sealing-more": skill("x", name="sc-sealing-more"), "sc-ask": router(["sc-sealing-more"])})
        problems = r.check()
        self.assertProblem(problems, "does not mention sc-sealing")
        self.assertNotIn("sc-sealing-more", "\n".join(problems))
        import shutil
        r = Repo()
        shutil.rmtree(os.path.join(r.root, "skills", "sc-ask"))
        self.assertProblem(r.check(), "router is missing")

    def test_the_readme_links_every_skill(self):
        r = Repo(readme=False)
        self.assertProblem(r.check(), "README.md", "sc-sealing")

    def test_every_skill_has_a_docs_page_and_no_page_is_left_over(self):
        r = Repo(docs=False)
        self.assertProblem(r.check(), "docs/sc-sealing.md", "no docs page")
        r = Repo(extra_docs={"sc-old": PAGE})
        self.assertProblem(r.check(), "docs/sc-old.md", "without a skill")

    def test_a_docs_page_keeps_its_sections_in_order(self):
        missing = PAGE.replace("## It's working if\n\n- it works\n\n", "")
        self.assertProblem(Repo(extra_docs={"sc-sealing": missing}).check(), "docs/sc-sealing.md", "It's working if", "missing")
        swapped = "## When to reach for it\n\nx\n\n" + PAGE.replace("## When to reach for it\n\nWhen you need it.\n\n", "")
        self.assertProblem(Repo(extra_docs={"sc-sealing": swapped}).check(), "out of order")
        other = PAGE + "\n## Extra\n\nx\n"
        self.assertProblem(Repo(extra_docs={"sc-sealing": other}).check(), "## Extra", "not one of the sections")
        titled = "# Sealing\n\n" + PAGE
        self.assertProblem(Repo(extra_docs={"sc-sealing": titled}).check(), "no H1")
        optional = PAGE.replace("## It's working", "## Prerequisites\n\nstAirCase.\n\n## It's working")
        self.assertEqual(Repo(extra_docs={"sc-sealing": optional}).check(), [])

    def test_a_docs_page_links_the_router(self):
        page = PAGE.replace("[sc-ask](sc-ask.md)", "the router")
        self.assertProblem(Repo(extra_docs={"sc-sealing": page}).check(), "sc-ask.md")

    def test_commands_and_names_in_a_docs_page_are_checked(self):
        page = PAGE.replace("it works", "run `staircase sael` and see `sc-ghost`")
        problems = Repo(extra_docs={"sc-sealing": page}).check()
        self.assertProblem(problems, "docs/sc-sealing.md", "sael", "sc-ghost")

    def test_a_docs_page_may_name_a_person_only_skill_without_the_slash(self):
        page = PAGE.replace("It does one thing.", "`sc-away` is the one you type.")
        r = Repo({"sc-away": person_only(), "sc-sealing": GOOD}, extra_docs={"sc-sealing": page})
        self.assertEqual(r.check(), [])


if __name__ == "__main__":
    unittest.main()
