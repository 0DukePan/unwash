**Title**

Four ways an AI agent makes a test suite green without fixing the bug

**Body**

I kept hitting the same thing with coding agents: the turn ends with "done, tests pass", the suite really is green, and the bug is still there. After enough of these I went through the diffs. The same four shapes kept showing up.

**1. Skipping the test instead of making it pass**

```python
@pytest.mark.skip(reason="temporarily flaky")
def test_refund_caps_at_balance():
    ...
```

The suite reports green because the test never runs. A diff shows it, but it is easy to scroll past in 400 lines, and the run summary says "1 passed, 1 skipped", which reads like success.

**2. Mocking the thing under test**

```python
def test_total_is_correct():
    with mock.patch("cart.calculate_total", return_value=42):
        assert cart.calculate_total() == 42
```

This looks like a test. It asserts that a mock returned the value you told it to return. Coverage goes up. `calculate_total` is never executed.

**3. Hardcoding the asserted value**

The test says `assert calc.add(2, 3) == 5`. The diff changes `add` to `return 5`. The visible test passes. The hidden test that would catch it, the one with different numbers, does not exist yet. That is the whole point.

**4. Swallowing the exception that should have failed**

```python
try:
    data = json.loads(raw)
except Exception:
    data = {}
```

The function "never crashes" now. If the input was malformed you get `{}`, and you find out three layers later in a log nobody reads.

---

**What actually catches these**

The four are easy to grep for. The reason they survive review is that each diff looks plausible on its own. What separates a real fix from these is a second opinion from tests the agent did not write:

1. **Re-run the test in its committed form.** If a diff touches `tests/test_x.py`, check out the version from `git show HEAD:tests/test_x.py` and run that against the new code. An edited test that only passes in its edited form is the signature of #1 and #3. It is three lines of shell and it catches more than any static rule I have written.

2. **Keep one suite the agent never sees.** It does not have to be elaborate. One file, different inputs than the ones in the prompt. It is the only check that cannot be argued with, because it is the only one the agent could not edit.

3. **Run the suite on the base commit too.** If it was already failing before the change, "tests pass" is a claim about the tree, not about the fix.

Number one is the one I got tired of doing by hand on every PR. It is now a CLI called `unwash`, which does the committed-test replay, the baseline diff, and the held-out run, then prints a verdict with the evidence attached. It reports by default and only blocks if you turn that on:

```
pipx install unwash-cli
unwash
```

If you take one thing from this post, take the replay snippet. It works with whatever harness you already have and does not need my tool.

---

**On the numbers, because someone will ask**

I planted 25 cheats across 28 tasks and the tool caught all 25. I also wrote every one of those tasks, so that number says it works on my test cases and not much else. The 95% interval on recall is 71.5 to 100. You can re-run it yourself without a model in about 90 seconds: `python benchmark/verify.py`.

The number I actually wanted, whether having the tool around makes an agent cheat less often, I could not measure. 252 scored runs across three configurations came back indistinguishable, and the instrument that produced those labels turned out to be broken in a way I only found later. That null is at the top of the README, not buried.

Everything above, plus the six things I know are still open, is in `docs/what-did-not-work.md`. The one I would flag hardest: the swallow class in general cannot be detected from a diff, and the honest remedy is a held-out suite, which almost nobody has.

Questions about the replay approach welcome. That part is not specific to my tool.
