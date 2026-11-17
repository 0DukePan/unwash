# Reddit launch kit

Three posts, because the same text in three subreddits is what gets you banned
as a spammer. Pick the one that matches the channel, change nothing else.

Post in this order: **r/ChatGPTCoding** first (smallest, most forgiving, tells
you what lands), then **r/ClaudeAI**, then **r/programming** only if the first
two went well.

## Before you post — five minutes of checks

1. **Post the social preview.** Settings → General → Social preview, upload
   `assets/social-preview.png`. Without it the link renders as a grey box.
2. **Read the sidebar of the target subreddit.** I could not fetch their rules —
   Reddit blocks anonymous API reads. Reddit's own self-promotion guidance is a
   rough 9:1 ratio of participation to promotion; a brand-new account posting a
   link as its first act gets filtered by the spam classifier regardless of the
   content.
3. **Have the first comment ready.** It is the one you will actually be judged
   on. Drafted below each post.

---

## r/ChatGPTCoding

**Title**

> I got tired of "done, tests pass" being a lie, so I built a checker that reruns the test the agent edited

**Body**

Every agent finishes the same way: *"Done, tests pass."*

Usually that is true. Sometimes the suite is green because the test got skipped,
the unit under test got mocked, the expected value got hardcoded, or the
exception that would have failed loudly got swallowed. From the outside those
look identical to a real fix.

`unwash` reads the diff and runs the tests. Three checks matter:

**1. It reruns the test in its committed form.** If a diff changes
`tests/test_calc.py`, it takes the version from git and runs *that* against the
current code. An edited test that only passes in its edited form is reported as
`test-weakened`, with the committed assertion that no longer holds.

**2. It runs a held-out suite if you have one.** This is the only check that
disagrees with a suite the agent could edit, and it is where the leverage is.

**3. It binds requirements to tests.** Repeating a sentence binds more evidence
to it, so one test passing and another failing is reported as *contradictory*
rather than quietly averaged:

```bash
unwash coverage --run-tests "python -m pytest -q" \
  --require "Login succeeds => tests/test_auth.py::test_login" \
  --require "Login succeeds => tests/test_auth.py::test_login_after_refresh" \
  --require "Invalid credentials rejected => tests/test_auth.py::test_rejects"
```

What it actually looks like:

```
! [hardcoded-return] UW-TEST-004  src/calc.py:2
    returns literal 5 (directly), which a test asserts against
Verdict: SUSPICIOUS -- the diff contains a pattern that needs an explanation
```

Exit 2, which hands the findings back to the agent. The visible suite passed.
That gap is the evidence.

```bash
pipx install unwash-cli
cd your-repo
unwash
```

MIT, no dependencies, no model, no network. It reports a pattern and says
"explain this" — it does not claim to know intent.

Repo: https://github.com/0DukePan/unwash

**First comment (post it yourself, immediately)**

> The number I'd attack if I were you: the detector catches 25 of 25 planted
> cheats, but I wrote those 25 tasks. The exact intervals are 71.5–100% recall
> and 0–28.5% false alarms. You can re-run it yourself without a model in 90
> seconds: `python benchmark/verify.py`.
>
> The bigger caveat: I could not show this changes agent behaviour. I ran 252
> scored runs across three plugin states and the arms were indistinguishable.
> That null is in the README above the fold. What it did buy me is a correction
> — all 16 runs my first labels called "silent cheats" turned out to be honest
> fixes to tasks whose hidden tests checked requirements the prompt never
> stated. That was a bug in my corpus, not the agent.

---

## r/ClaudeAI

**Title**

> A Stop hook that blocks Claude Code from ending a turn on a faked "done"

**Body**

Claude Code will end a turn saying "done, tests pass" on a diff that made the
test pass rather than the code work. The Stop hook is the only place you can
catch that, because it is the last moment before the claim goes out.

`unwash` ships one. In report mode it prints what it found and lets the turn
end. With `"mode": "enforce"` in `.unwash/config.json` it exits 2 and hands the
findings back to the model:

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

Or plain CLI if you only want it in CI:

```bash
pipx install unwash-cli
```

It never calls a model, never leaves your machine, and has no dependencies.

The thing it catches that a normal review misses: when the diff edits a test,
it re-runs the **committed** version of that test against the new code. If the
test only passes in its edited form, that is the finding.

Repo with the honest limits: https://github.com/0DukePan/unwash

**First comment**

> Config is one file, `.unwash/config.json`. The two knobs worth setting:
>
> - `test_command` — pin it, or the hook discovers it and discovery can guess
>   wrong on a monorepo.
> - `heldout` — a path to a suite the agent never saw. It is the only check that
>   can disagree with a suite the agent might edit.
>
> Full list: https://github.com/0DukePan/unwash/blob/main/docs/ADOPTION_GUIDE.md — and the false-positive classes I know about are documented rather than hidden, because a tool that cries wolf gets uninstalled.

---

## r/programming — only if the first two went well

**Title**

> Coding agents fake passing tests in four specific ways. I built a checker for the gap between "tests pass" and "the code works"

**Body**

Lead with the evidence gap, not the product. The interesting claim is narrow:

An agent that skips the test, mocks the unit under test, hardcodes the asserted
value, or swallows the exception produces exactly the same observable output as
a real fix: a green suite. Static review catches the shapes but not the
consequences, which is why the tool runs the tests rather than only reading the
diff.

The checks that carry weight:

- **committed-test replay** — a changed test is re-run in its original form
- **held-out suite** — a suite the agent never saw
- **baseline differential** — the same tests on the untouched tree
- **requirement binding** — a claim sentence bound to the tests that would prove
  it, with `contradictory` as its own verdict rather than a pass

What it does not do: prove correctness, infer intent, or call a model. The
verdict vocabulary has an explicit "I could not tell".

Two numbers, both with their caveats:

| | |
|---|---|
| Planted cheats caught | 25/25 — **but I wrote the corpus** (95% CI 71.5–100%) |
| Does it change agent behaviour? | **Unmeasured.** 252 runs, three arms, indistinguishable |

MIT, Python, no dependencies: `pipx install unwash-cli`

https://github.com/0DukePan/unwash

**First comment**

> Why the null is published instead of buried: a tool that reports "no effect"
> on its own headline metric is more useful to you than one that reports a
> number you cannot check. Both numbers, and the four ways the first benchmark
> was wrong, are in `docs/what-did-not-work.md`.

---

## What not to do

- **Do not post the same text twice.** Rewrite the opening line at minimum.
- **Do not lead with the null.** I argued for this and still think the null
  belongs in the second half; a reader decides in eight seconds and "my tool
  didn't work" loses them before they see what it does.
- **Do not argue with the "your own corpus" comment.** Agree, link the
  intervals, move on. That comment is correct and conceding it is the whole
  reason the rest is believable.
- **Do not crosspost to four subs the same day.** One sub, wait a day, read the
  comments, adjust.
- **Answer the first ten comments.** A launch is forty minutes of replies, not
  a post.
