from __future__ import annotations

import sys


def main() -> int:
    """Route the current atlas explicitly while preserving preview replay."""

    if sys.argv[1:2] == ["chromatic"]:
        del sys.argv[1]
        from .chromatic import main as chromatic_main

        return chromatic_main()

    if sys.argv[1:2] == ["steenrod"]:
        del sys.argv[1]
        from .steenrod import main as steenrod_main

        return steenrod_main()

    from .preview import main as preview_main

    return preview_main()


raise SystemExit(main())
