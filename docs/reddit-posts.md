# Reddit posts, one per channel

Every one of these is written to survive a "no pure self-promotion" rule: the
technique comes first, the tool is mentioned at the end, and each gives away
something that works without the tool.

**I could not read any subreddit's rules.** Reddit serves the same JavaScript
shell to anonymous requests and blocks its API (403 on `about.json`), so every
fetch returned an identical 340KB page with no content in it. Open the sidebar
yourself before posting. These are written to be safe under the strictest rule
set I know of (r/ChatGPTCoding's: no pure self-promotion, no AI slop, use the
right flair), but check.

Post one per day, not one per hour. Several channels ban you for the second.

---

# 1. r/ClaudeAI

*Angle: the Stop hook. This audience runs Claude Code and knows what a hook is.*

**Title**

A Stop hook that blocks Claude Code from ending a turn on a faked "done"

**Body**

Claude Code will end a turn saying "done, tests pass" on a diff that made the
test pass rather than the code work. The Stop hook is the one place you can
intervene, because it fires before the claim goes out.

I built one that checks three things when the turn tries to end:

1. **Did the diff edit a test?** If so, run the committed version of that test
   against the new code. `git show HEAD:tests/test_x.py`. If it only passes in
   its edited form, that is the finding.
2. **Did the suite pass on the base commit?** If it was already red before the
   change, "tests pass" is a claim about the tree.
3. **Is there a held-out suite?** If you have one, it runs it. That is the only
   check the agent could not have edited.

In report mode it prints and lets the turn end. With `"mode": "enforce"` in
`.unwash/config.json` it exits 2, which hands the findings back to the model:

```
unwash: SUSPICIOUS (medium confidence)
  strict gate: blocked -- the diff contains a pattern that needs an explanation:
      [hardcoded-return] src/calc.py:2
  visible tests: 1/1
```

Install as a plugin:

```
/plugin marketplace add 0DukePan/unwash
/plugin install unwash@unwash
```

Or just the CLI if you only want it in CI:

```
pipx install unwash-cli
```

No model, no network, no dependencies. It reads the diff and runs your tests.

What I would warn you about before adding a hook: a gate that fires on ordinary
work gets uninstalled within a week. Mine had exactly that bug at first, because
the hook re-derived the decision instead of reading the CLI's exit code and
blocked on findings that were already verified. The false-positive classes I
know about are documented rather than hidden, because the alternative is a tool
people disable.

Repo with the honest limits: https://github.com/0DukePan/unwash

**First comment**

> The config that matters is two fields:
>
> ```json
> { "mode": "enforce",
>   "test_command": "python -m pytest -q",
>   "heldout": "tests/heldout" }
> ```
>
> Pin `test_command`. Discovery guesses wrong on monorepos and then the hook is
> checking something you did not intend. `heldout` is the one I would set up
> first if you can only do one.

---

# 2. r/SideProject

*Angle: the build story and the published null. This subreddit exists for this.*

**Title**

I spent months building a checker for AI agents that fake passing tests. The honest result is "it works, but I could not prove it changes anything"

**Body**

The problem: an AI agent finishes a task with "done, tests pass". Sometimes the
suite is green because the test was skipped, the unit under test was mocked, the
asserted value was hardcoded, or the exception that would have failed loudly got
swallowed. From the outside that looks identical to a real fix.

I built a CLI that reads the diff and runs the tests, and refuses to guess when
it cannot tell. `pipx install unwash-cli`, no dependencies, no model, no network.

**What went right**

I wrote 28 tasks, each with a planted cheat, and the detector caught 25 of 25
that ran (three tasks need toolchains I do not have installed). Those cheats
actually made the visible suite go green before they were scored, so it is not a
toy corpus.

**What went wrong, in order of embarrassment**

1. The first behavioural study reported "no cheating in 252 runs". The
   instrument that produced those labels could not record a cheat that passed
   the held-out suite. A 0% from a broken instrument is not a 0%.
2. My first labels called 16 runs "silent cheats". All 16 turned out to be
   honest fixes to tasks whose hidden tests checked requirements the prompt
   never stated. That was a bug in my corpus, not the agent. I published the
   correction with its arithmetic.
3. One rule produced 104 of 109 flags on ten real repositories, nearly all
   dependency bumps. I narrowed it and the same history produces 7. It had been
   measuring noise.
4. The project is on its third name, because the first two collided with other
   packages. A PyPI token even landed that was scoped to someone else's project,
   `unswallow`. I did not publish with it.

**Where it stands**

The detector numbers are first-party, so the 95% interval on recall is 71.5 to
100 and I say so before anyone else does. The behavioural question, whether
having the tool around makes an agent cheat less, is still unmeasured. My next
step is a corpus I did not write, and that needs other people.

https://github.com/0DukePan/unwash

**First comment**

> The thing I would do differently: publish the "what did not work" page in week
> one instead of month four. Every time I found a bug in my own benchmark it
> cost less to write it down than to have someone else find it in the comments.

---

# 3. r/softwaretesting

*Angle: test integrity as a discipline. Highest topical relevance of any sub.*

**Title**

When the fix is "the test was wrong": detecting tests edited to pass

**Body**

Most of what gets called "AI breaking tests" is more boring and more useful than
that: someone changed a test so the code would go green. Sometimes that is
correct, and the spec really did change. Sometimes it is the bug moving into the
test file.

A reviewer reading a diff cannot easily tell those apart, because the edit looks
reasonable in isolation. Three checks settle it, and none of them needs a model:

**1. Run the committed test against the new code.**

```bash
git show HEAD:tests/test_refund.py > /tmp/committed_test.py
python -m pytest /tmp/committed_test.py
```

If the committed version fails and the edited version passes, you have separated
"behaviour changed" from "the assertion changed". That is the whole question.
This is the single highest-value check and it is four lines of shell.

**2. Run the old tests against the new code, not just the new tests.**

A suite that grows a new passing test while quietly losing an assertion is the
common shape. Counting assertions per file before and after catches it.

**3. Keep a suite the change cannot see.**

The usual objection is coverage: an independent suite is another thing to
maintain. My experience is that one file with three cases covers most of the
value, because the failure mode is not subtle wrongness, it is "nobody
re-checked the thing this test used to check".

I automated the first two plus a baseline run, and turned it into a CLI
(`pipx install unwash-cli`) because doing them by hand on every PR stopped
happening around the third week. But the replay snippet above is the part worth
keeping either way.

One thing I got wrong and would flag: I assumed detection was the hard part. It
is not. The hard part is the false positive rate, because a gate that cries wolf
gets switched off, and then it protects nothing.

**First comment**

> On assertion counting: the naive version (count `assert` lines per file before
> and after) catches the obvious deletions and misses the interesting ones,
> where one strong assertion is replaced by three weak ones. I do not have a
> good automated answer for that. If anyone does, I would like to read it.

---

# 4. r/commandline

*Angle: a zero-dependency CLI. This audience cares about the tool, not the AI.*

**Title**

unwash: a zero-dependency CLI that re-runs the tests an agent edited

**Body**

`unwash` is a single Python CLI with no dependencies that answers one question
about a git diff: is this change backed by evidence?

Three modes:

```bash
unwash          # report on the current diff
unwash scan     # static rules only, no test run
unwash verify   # behavioral checks only
```

And one subcommand that was worth building:

```bash
unwash coverage --run-tests "python -m pytest -q" \
  --require "Login succeeds => tests/test_auth.py::test_login" \
  --require "Login succeeds => tests/test_auth.py::test_login_after_refresh"
```

Repeating a sentence binds more evidence to it, so one test passing and another
failing comes out as `contradictory` instead of being averaged into a pass.

Exit codes are conventional: 0 clean, 1 findings, 2 blocking, 3 could not run,
4 integrity failure. Nothing blocks unless you pass `--enforce`.

Install:

```
pipx install unwash-cli
```

Python 3.10+, no dependencies, no network, no account. Report output is a
terminal table by default with `--json` and `--format markdown` alongside.

https://github.com/0DukePan/unwash

**First comment**

> The one non-obvious design decision: `ignore_rules` is refused in strict mode
> rather than honoured. Suppressing a rule that would have blocked turns "I
> decided this is fine" into "I stopped looking", and only the first one is
> auditable. Waivers have to carry a reviewer, a reason and an expiry of 30 days
> or less.

---

# 5. r/webdev or r/ExperiencedDevs

**Skip these.** Both have strict anti-promotion rules and neither audience is
the buyer. r/programming is also not worth it for a first launch: they remove
anything that reads as marketing, and the honest post here still reads as a
project announcement.

---

# Posting order

| Day | Channel | Why |
|---|---|---|
| 1 | r/chatgptcoding | smallest, most forgiving, tells you what lands |
| 2 | r/ClaudeAI | largest relevant audience, hook angle is concrete |
| 3 | r/SideProject | explicitly allows promotion, different expectations |
| 4 | r/softwaretesting | small but the topic fits exactly |
| 5 | r/commandline | only if the above went well |

Change the first sentence between posts. Copy the same opening twice and you
will be treated as a spammer regardless of the content.
