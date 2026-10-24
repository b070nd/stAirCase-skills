STAIRCASE_BIN ?= staircase

.PHONY: check test skills validate

# The tests of the check, then the check of the skills against the installed staircase.
check: test skills

test:
	python3 -W error::ResourceWarning -m unittest discover -s tests

skills:
	python3 tools/check_skills.py --staircase $(STAIRCASE_BIN)

# Claude Code's own validator, strict: the marketplace, the plugin manifest and the skills.
validate:
	claude plugin validate --strict .
	claude plugin validate --strict .claude-plugin/plugin.json
	claude plugin validate --strict skills
