from _baseline import Baseline
from _transforms import ascii_repr, rstrip


class AsciiBaseline(Baseline):

    """Baselined string (with non-printable characters escaped)."""

    TRANSFORMS = [ascii_repr]


class StrippedBaseline(Baseline):

    """Baselined string (with whitespace stripped from line endings)."""

    TRANSFORMS = [rstrip]
