# FAQ

**Edition:** v21 · October 2026

## What is this?

An offline browser campus for unified communications and contact center study. One HTML file. No account.

The tracks match the job: CUCM, CUBE, SIP, Webex Calling, Webex Contact Center, Teams Phone, UCCE, PCCE, CUIC, the main CCaaS platforms, E911, QoS, and troubleshooting.

The home page is a dashboard. Ctrl+K searches every lesson. Thirty labs sit on the same page: call flows (24 scenarios), a dial plan, an IVR, SIP decode, codec and jitter tools, CUCM routing, Webex Calling, UCCE, Finesse, E911, QoS, SRTP, Erlang-C, fault finding, dial-peers, one-way audio, recording, plus line-and-device CSS, called-party digits, a SIP ladder, a certificate chain, route patterns, Collaboration PA bandwidth, pasted SDP, hunt distribution, and 29 troubleshooting cases. The quiz has at least 300 scored questions on each track (6,522 total) plus a boss exam. Flashcards are 3,402. Each lesson has a Try it button for its lab. Progress stays in the browser. Nothing is uploaded.

## How do I open it?

1. Download [the v21 zip](../releases/uc-lab-free-university.html.zip).
2. Unzip it.
3. Open `uc-lab-free-university.html` in Chrome, Safari, Edge, or Firefox.

From a clone, open [campus/uc-lab-free-university.html](../campus/uc-lab-free-university.html). That file is edition v21: 507 sections, light and dark themes. Steps for a phone are in [HOW-TO-USE](./HOW-TO-USE.md).

## Does it work on a phone?

Yes, in the full browser app. The first load can take a little while. A laptop is easier to study on.

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

[AI Lab Free University](https://github.com/cipher0x9/ai-lab-free-university-mesmerizing) is a separate offline campus for a different subject. See [SIBLINGS](./SIBLINGS.md).

## How do I contribute?

Open an issue, or read [CONTRIBUTING](../CONTRIBUTING.md) and [REMIX](./REMIX.md).
