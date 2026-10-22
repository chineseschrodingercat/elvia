"""Support python -m elvia using the same CLI as the installed script."""

from elvia.cli import main

raise SystemExit(main())
