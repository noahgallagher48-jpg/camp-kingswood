#!/usr/bin/env python3
"""The bleedhero spread map. ONE definition, read by both renderers.

A spread is a hero frame that bleeds across the left page with 2 to 6 detail
frames facing it on the right.

WHY THIS FILE EXISTS. The map used to live twice: hardcoded in book_layout.py's
JavaScript for the on-screen preview, and again in build_book.py for the press
file. On 2026-08-28 Codex caught them disagreeing. The viewer promised a
five-photograph spread while the builder, whose map was empty, matted the hero
and printed one page. Selecting a frame previewed one book and printed another.
Both renderers now import this.

Format: {hero frame number: [the frames facing it]}. Empty is correct until Noah
names a spread; nothing is inferred, and a frame is never placed by guesswork.
"""

MONTAGE_SPREADS = {}
