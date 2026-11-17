"""unwash -- a report on what an agent's "done" claim is actually worth.

The public surface is small and stable:

    unwash.domain          Run, Claim, Signal, VerificationResult, Verdict,
                              TrustReport -- the versioned wire format
    unwash.confidence      deterministic, explainable scoring
    unwash.scan            static diff analysis -> Signal[]
    unwash.verify          behavioral verification -> VerificationResult
    unwash.report          terminal / json / markdown renderers
    unwash.cli             zero-config entry point

Nothing here requires a network call, an account, or a model. The tool reads
your diff and runs your tests; that is the whole mechanism.
"""

__version__ = "0.5.1"

__all__ = ["__version__"]
