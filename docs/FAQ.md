# FAQ

**Edition:** v21 · October 2026

## What is this?

An offline browser campus for unified communications and contact center study. One HTML file. No account.

The tracks match the job: CUCM, CUBE, SIP, Webex Calling, Webex Contact Center, Teams Phone, UCCE, PCCE, CUIC, the main CCaaS platforms, E911, QoS, and troubleshooting.

## How do I open it?

1. Download [the v21 zip](../releases/uc-lab-free-university.html.zip).
2. Unzip it.
3. Open the HTML file in Chrome, Safari, Edge, or Firefox.

From a clone, open [university/v17-UNIVERSITY.html](../university/v17-UNIVERSITY.html). The filename predates v21. The page title says v21.

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

[AI Lab Free University](https://github.com/cipher0x9/ai-lab-free-university-mesmerizing) is a separate offline campus for a different subject.
