# FAQ

**Edition:** v21 · October 2026

## What is this?

An offline browser campus for unified communications and contact center study. A small HTML shell plus lesson modules. No account.

The tracks match the job: CUCM, CUBE, SIP, Webex Calling, Webex Contact Center, Teams Phone, UCCE, PCCE, CUIC, the main CCaaS platforms, E911, QoS, and troubleshooting.

Labs load when you open them. There are 21 teaching labs: call flows (24 ladders, including hold, blind and consult transfer, hunt, MRA, IVR to agent, E911, Teams Direct Routing, and Webex Contact Center), a dial plan, an IVR, SIP decode, codec and jitter tools, CUCM routing, Webex Calling, UCCE, Finesse, E911, QoS, SRTP, Erlang-C, fault finding, dial-peers, one-way audio, and recording. The quiz has at least 150 scored questions on each track (2,913 total) plus a boss exam. Flashcards are 2,018. Each lesson links to a matching lab. Quiz scores stay in the browser. Nothing is uploaded.

## How do I open it?

1. Download [the v21 zip](../releases/uc-lab-free-university.html.zip).
2. Unzip it.
3. Open `uc-lab-free-university.html` in Chrome, Safari, Edge, or Firefox.

From a clone, open [campus/uc-lab-free-university.html](../campus/uc-lab-free-university.html). That file is edition v21: 580 sections. Settings has light, dark, high contrast, and signal, plus sound, narration, motion, and font size. Tips and cheat sheets are at `#/tips`. Steps for a phone are in [HOW-TO-USE](./HOW-TO-USE.md).

## Does it work on a phone?

Yes, in the full browser app. The shell loads first. Under 640px, **Menu** opens the paths and a bottom nav stays on screen. A laptop is easier for the ladders.

## Is there a PDF?

No separate textbook. The campus is the book. Use the browser print dialog, or the export menu inside the page, when you want a PDF of a section. The [62-slide briefing](../downloads/Enterprise-Voice-with-Cisco-Technologies-CC-Cloud-Migration.pptx) is the slide companion.

## Is this official vendor training?

No. It is educational material by CYPHER0X9. Read the current Cisco, Microsoft, or CCaaS document before you change production.

## Why is WebRTC here?

Contact-center agent desktops and web soft clients send media from the browser. A silent agent is often ICE, TURN, or a SASE inspection policy. A desk phone does not use that path. The campus says so on the WebRTC page.

## Why is Linux here?

CUCM, Unity Connection, IM and Presence, and Emergency Responder run on Cisco VOS, which is a locked-down Linux. The command line is how you check NTP, database replication, certificates, and disk. There is no general Linux course in this edition.

## What is LICC?

Leg, identifier, counter, capture. Name the hop, the id that joins the logs, the counter that moved, and the artifact that proves it.

## Can I use this at work?

The license is MIT. Do not paste secrets or customer captures into an issue. Do not treat a page as a production runbook until you have checked the vendor document for your version.

## Related campus

[AI Lab Free University](https://github.com/CypherMonkeyLabs/ai-lab-free-university-mesmerizing) is a separate offline campus for a different subject. See [SIBLINGS](./SIBLINGS.md).

## How do I contribute?

Open an issue, or read [CONTRIBUTING](../CONTRIBUTING.md) and [REMIX](./REMIX.md).
