from __future__ import annotations

import sys


def main() -> int:
    """Route the current atlas explicitly while preserving preview replay."""

    if sys.argv[1:2] == ["chromatic"]:
        del sys.argv[1]
        from .chromatic import main as chromatic_main

        return chromatic_main()

    from .preview import main as preview_main

    return preview_main()


raise SystemExit(main())
