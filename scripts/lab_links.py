"""Public links for the deck footer and the README badges.

Add Instagram, Kaggle, or Google Developer later with one new line in
FOOTER_LINKS. The icon field is the file stem in scripts/brand_icons/
(instagram.svg, kaggle.svg, and google.svg are already there). Then run
`python3 scripts/brand-pptx.py`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FooterLink:
    key: str
    label: str
    cta: str
    href: str
    icon: str


DISCLAIMER = (
    "Educational independent student project. Not affiliated with or endorsed "
    "by Cisco or any vendor. Trademarks belong to their owners."
)
FOOTER_LINE = "Cypher Monkey Labs © 2026 CypherMonkeyLabs"
APP_HREF = "https://cyphermonkeylabs.com/uc-lab-free-university-mesmerizing/"
APP_CTA = "Open the app"

# The briefing ships as 62 content slides plus the branded close.
BASE_SLIDES = 62
EXPECTED_SLIDES = BASE_SLIDES + 1

FOOTER_LINKS: tuple[FooterLink, ...] = (
    FooterLink("github", "GitHub", "Visit my GitHub", "https://github.com/cipher0x9", "github"),
    FooterLink("labs", "Labs org", "Labs org", "https://github.com/CypherMonkeyLabs", "github"),
    FooterLink("website", "Website", "Website", "https://cyphermonkeylabs.com", "globe"),
    FooterLink("x", "X", "X", "https://x.com/Cypher0x9", "x"),
    FooterLink("linkedin", "LinkedIn", "LinkedIn", "https://www.linkedin.com/in/luckylakshmanucwebex", "linkedin"),
    FooterLink("huggingface", "Hugging Face", "Hugging Face", "https://huggingface.co/Cypher0x9", "huggingface"),
    # FooterLink("instagram", "Instagram", "Instagram", "https://www.instagram.com/example", "instagram"),
    # FooterLink("kaggle", "Kaggle", "Kaggle", "https://www.kaggle.com/example", "kaggle"),
    # FooterLink("googledev", "Google Developer", "Google Developer", "https://developers.google.com/profile/example", "google"),
)


def readme_links() -> tuple[FooterLink, ...]:
    """README buttons: the app first, then the same row as the deck footer."""
    opener = FooterLink("app", APP_CTA, APP_CTA, APP_HREF, "app")
    return (opener, *FOOTER_LINKS)
