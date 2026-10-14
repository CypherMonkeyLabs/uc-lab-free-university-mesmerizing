#!/usr/bin/env python3
"""Write campus/assets/flow-catalog.js with a distinct flow per section.

Every section gets its own happy-path definition and a failure-path definition.
End-to-end walkthroughs are additional definitions. The page loads the generated
file. It does not run this script.

  python3 scripts/build-section-flows.py
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "campus" / "uc-lab-free-university.html"
OUT = ROOT / "campus" / "assets" / "flow-catalog.js"

CHARTS = [
    "mos-loss", "mos-delay", "codec-bw", "jitter-buffer", "erlang-b-curve",
    "erlang-c-curve", "sla-agents", "asa-agents", "aht-sensitivity", "trunk-util",
    "cac-budget", "failover-timeline", "latency-waterfall", "sip-timers", "ptime-bw",
    "dscp-map", "loss-burst", "occupancy-sl", "queue-depth", "rona-rate",
    "register-expires", "dns-ttl", "cert-expiry", "codec-mos-bars", "g114-stack",
    "srtp-overhead", "setup-waterfall", "staffing-shrink", "jitter-histogram",
    "cutover-clock", "early-media-timing", "retransmission-backoff",
]

PRODUCTS = [
    ("8x8", "8x8", ["Carrier", "8x8", "Phone"], "cloud", "8x8 call id",
     "SIP toward the 8x8 edge on the trunk you configured. Do not invent a second signaling port."),
    ("avaya", "Avaya Aura", ["Endpoint", "Session Manager", "Communication Manager"], "phone", "SM call id",
     "Session Manager routes the SIP request. Communication Manager applies the station and trunk rules."),
    ("five9", "Five9", ["Carrier", "Five9", "Agent"], "queue", "Five9 call id",
     "The carrier hands the call to Five9. The VCC skill and IVR script decide the agent, not the carrier SIP alone."),
    ("genesys", "Genesys Cloud", ["Carrier", "Genesys Edge", "Agent"], "cloud", "conversation id",
     "Architect owns the flow. The Edge anchors signaling. The conversation id joins the timeline."),
    ("mitel", "Mitel", ["Phone", "Mitel", "Trunk"], "phone", "Mitel call id",
     "The controller routes the call, then the trunk faces the carrier. Keep the two legs separate when you capture."),
    ("nice|cxone", "NICE CXone", ["Carrier", "CXone", "Agent"], "queue", "contact id",
     "CXone routing uses the contact id. The agent desktop is not the RTP clock."),
    ("ringcentral|\\brc\\b", "RingCentral", ["Carrier", "RingCentral", "App"], "cloud", "RC session id",
     "RingCentral is the cloud PBX. A direct number still has a carrier leg and an app or desk-phone leg."),
    ("twilio", "Twilio", ["Carrier", "Twilio", "Webhook"], "cloud", "CallSid",
     "Programmable Voice requests your webhook, then acts on the returned instructions. Studio is a visual form of that same request."),
    ("zoom", "Zoom Phone", ["Carrier", "Zoom Phone", "Device"], "phone", "Zoom call id",
     "Zoom Phone places the call in the site and the user. BYOC, when you use it, is a separate trunk from Zoom Phone native PSTN."),
    ("wxcc|webex contact|webex cc", "Webex Contact Center", ["Caller", "Webex CC", "Agent"], "queue", "interaction id",
     "The entry point starts a flow. The queue selects an agent. Control Hub is beside the call, not inside RTP."),
    ("webex", "Webex Calling", ["Webex app", "Webex Calling", "Local Gateway"], "cloud", "Webex call id",
     "A certificate-based Local Gateway sends outbound SIP TLS toward TCP 5062. A registration trunk uses TCP 8934, and that registration session is reused. Calling Plan has no Local Gateway."),
    ("teams", "Teams Phone", ["Teams client", "Microsoft 365", "SBC"], "team", "Teams call id",
     "Direct Routing sends SIP TLS from the SBC to sip.pstnhub.microsoft.com on 5061, with sip2 and sip3 as failover. Calling Plan and Operator Connect do not use the customer SBC."),
    ("pcce", "PCCE", ["Caller", "PCCE", "Agent"], "queue", "RouterCallKey",
     "Packaged CCE uses the same routing ideas as UCCE: ingress, script, queue, peripheral, agent. The package does not remove the failure domains."),
    ("ucce|\\bcvp\\b|\\bicm\\b|finesse", "UCCE", ["Caller", "CVP", "ICM"], "queue", "RouterCallKey",
     "The ingress gateway sends the switch leg to the CVP call server. CVP asks ICM, then stays in signaling with a re-INVITE toward VVB. CUIC is not in the RTP path."),
    ("cuic", "CUIC", ["Call", "CUIC", "Report"], "proof", "RouterCallKey",
     "CUIC reads historical and live data. It does not carry audio. Time zones and skill-group names have to match or the join breaks."),
    ("amazon connect|\\bconnect\\b", "Amazon Connect", ["Caller", "Connect", "CCP"], "cloud", "contact id",
     "A contact flow runs in Connect. Lambda is invoked by the flow. The CCP is the agent desktop. Connect does not require a customer SBC for the native service."),
    ("cube|\\bsbc\\b|dial-peer", "CUBE", ["CUCM", "CUBE", "ITSP"], "cube", "Call-ID per leg",
     "CUBE is a B2BUA. Each leg has its own Call-ID. CUBE consumes ACK and generates the next leg. Flow-through media keeps CUCM out of RTP unless an MTP is required."),
    ("unity|voicemail|\\bmwi\\b", "Unity Connection", ["CUCM", "Unity Connection", "Phone"], "phone", "redirection Call-ID",
     "The redirect carries the original called number and the reason. MWI is a later NOTIFY or a lamp event, not the audio of the message."),
    ("expressway|\\bmra\\b", "Expressway", ["Jabber", "Expressway-E", "Expressway-C"], "cert", "edge call id",
     "Registration traverses E then C. The certificate chain on E is a common break. Media can hairpin at the edge."),
    ("cucm|\\bcss\\b|route pattern", "CUCM", ["Phone", "CUCM", "Trunk"], "route", "CUCM Call-ID",
     "Digit analysis searches the line CSS partitions first, then the device CSS. First match wins. A route pattern points at a route list, then a route group, then a trunk or gateway."),
    ("e911|emergency|redsky|\\bheld\\b|\\belin\\b", "E911", ["Phone", "Location", "PSAP"], "emergency", "ELIN or location key",
     "CER maps a switch port to an ERL and an ELIN. Webex uses HELD. Teams uses LIS and can add PIDF-LO when PidfLoSupported is set. Kari's Law requires on-site notification."),
    ("qos|dscp|\\bmos\\b|jitter", "QoS", ["Phone", "Switch", "WAN"], "qos", "DSCP 46",
     "Bearer is EF, DSCP 46. Cisco collaboration signaling is commonly CS3, DSCP 24. G.114 plans for about 150 ms one way."),
    ("sip|rfc 3261|invite", "SIP", ["Alice UAC", "Bob UAS"], "sip", "Call-ID",
     "RFC 3261 is the baseline. 100 Trying is hop by hop. A 2xx ACK is end to end. Timer B and Timer F are 64 times T1, 32 seconds on UDP."),
]


def load_sections() -> list[dict]:
    html = HTML.read_text(encoding="utf-8")
    key = "window.SECTIONS = "
    i = html.index(key) + len(key)
    depth = 0
    in_str = False
    esc = False
    for j, ch in enumerate(html[i:], i):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(html[i : j + 1])
    raise SystemExit("SECTIONS did not parse")


def plain(body: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", body)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</(p|li|h[1-6]|tr|div)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", " ").replace("&lt;", " ").replace("&gt;", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text


def blob_of(sec: dict) -> str:
    return f"{sec['id']} {sec['title']} {sec.get('sub', '')}".lower()


def product_of(sec: dict) -> tuple:
    blob = blob_of(sec) + " " + sec["group"].lower()
    for pat, name, actors, icon, idname, fact in PRODUCTS:
        if re.search(pat, blob):
            return name, actors, icon, idname, fact
    if sec["group"] == "Migrations":
        return ("Migration", ["Old platform", "Number", "New platform"], "migration", "ported number",
                "Dual-run means both platforms can still complete a test call until the rollback gate closes.")
    if sec["group"] == "Practice":
        return ("Practice", ["Student", "Ladder", "Answer"], "proof", "the question's object",
                "Answer from the ladder, then check the revealed line. Do not memorize the letter alone.")
    if sec["group"] == "Evidence habits":
        return ("Evidence", ["Leg", "Identifier", "Capture"], "proof", "correlation id",
                "The pack has to name the leg, the id, the counter, and the capture before anyone changes production.")
    if sec["group"] == "Design notes":
        return ("Design", ["Failure domain", "Capacity", "Identity"], "route", "the saturating unit",
                "Name the smallest failure domain and the unit that saturates first before you add a feature.")
    if sec["group"] == "Reference":
        return ("Reference", ["Term", "Current doc", "Lab"], "cert", "the vendor name",
                "Use the product's current document. A glossary entry is a pointer, not a change window.")
    if sec["group"] == "Troubleshooting":
        return ("Fault", ["Caller", "Edge", "Far end"], "tree", "Call-ID",
                "One hypothesis, one change, then the same identifier again.")
    return ("Campus", ["Caller", "Control", "Media"], "proof", "Call-ID",
            "Separate signaling from media, then join the logs on one identifier.")


def kind_of(sec: dict) -> str:
    title = sec["title"].lower()
    gid = sec["id"].lower()
    group = sec["group"]
    if group == "Troubleshooting" or gid.startswith(("trick", "sev", "hub-sev")) or "troubleshooting" in title:
        return "fault"
    if group == "Migrations" or "migrat" in title or "cutover" in title:
        return "migration"
    if group == "Practice" or title.startswith("practice") or gid.startswith(("qb", "drill", "bonus")):
        return "practice"
    if group == "Evidence habits":
        return "evidence"
    if group == "Design notes":
        return "design"
    if group == "Reference":
        return "reference"
    if group == "Emergency calling" or re.search(r"e911|emergency", title):
        return "e911"
    if "call flow" in title:
        return "call"
    if "architecture" in title:
        return "arch"
    if "config" in title:
        return "config"
    if "interview" in title or "q&a" in title:
        return "interview"
    if "overview" in title:
        return "overview"
    if gid.startswith("api-") or "webhook" in title or "rate limit" in title:
        return "api"
    return "topic"


def step(f: int, t: int, label: str, kind: str, cap: str) -> dict:
    cap = re.sub(r"\s+", " ", cap).strip()
    if "@" in cap or "@" in label:
        raise SystemExit(f"refusing @ in flow text: {label}")
    return {"f": f, "t": t, "label": label, "kind": kind, "cap": cap}


def title_clause(sec: dict) -> str:
    title = re.sub(r"\s+", " ", sec["title"]).strip()
    sub = re.sub(r"\s+", " ", sec.get("sub") or "").strip()
    if sub and sub.lower() not in title.lower() and len(sub) > 12:
        return f"{title}. {sub}"
    return title


def chart_for(sec: dict) -> str:
    blob = blob_of(sec)
    rules = [
        (r"mos|voice quality", "mos-loss"),
        (r"jitter", "jitter-histogram"),
        (r"codec|g\.711|g711|bandwidth", "codec-bw"),
        (r"erlang", "erlang-b-curve"),
        (r"service level|\bsla\b", "sla-agents"),
        (r"\basa\b|speed of answer", "asa-agents"),
        (r"\baht\b|handle time", "aht-sensitivity"),
        (r"trunk util|trunk group", "trunk-util"),
        (r"\bcac\b|admission", "cac-budget"),
        (r"failover|srst|\bha\b", "failover-timeline"),
        (r"g\.114|one-way delay|latency", "g114-stack"),
        (r"timer b|sip timer|retransmission", "sip-timers"),
        (r"ptime|packetization", "ptime-bw"),
        (r"\bqos\b|dscp|\bef\b", "dscp-map"),
        (r"packet loss|loss burst", "loss-burst"),
        (r"occupancy", "occupancy-sl"),
        (r"queue", "queue-depth"),
        (r"rona|ring no answer|ring-no-answer", "rona-rate"),
        (r"register|expires", "register-expires"),
        (r"\bdns\b|\bttl\b|\bsrv\b", "dns-ttl"),
        (r"cert|expir|tls", "cert-expiry"),
        (r"srtp|sdes", "srtp-overhead"),
        (r"setup delay|post-dial", "setup-waterfall"),
        (r"shrink|staff", "staffing-shrink"),
        (r"cutover|migrat|dual-run", "cutover-clock"),
        (r"183|early media|prack|100rel", "early-media-timing"),
        (r"\bdelay\b", "latency-waterfall"),
        (r"contact center|agent", "erlang-c-curve"),
    ]
    for pat, cid in rules:
        if re.search(pat, blob):
            return cid
    digest = int(hashlib.sha256(sec["id"].encode()).hexdigest()[:8], 16)
    return CHARTS[digest % len(CHARTS)]


def practice_topics(sec: dict) -> list[str]:
    text = plain(sec.get("body") or "")
    found = re.findall(r"What best describes ([^?]{2,70})\?", text)
    out = []
    for item in found:
        item = re.sub(r"\s+", " ", item).strip(" .")
        if item and item not in out:
            out.append(item)
        if len(out) == 6:
            break
    return out


def happy_steps(sec: dict, kind: str, name: str, actors: list[str], fact: str) -> list[dict]:
    clause = title_clause(sec)
    if kind == "fault":
        return [
            step(0, 1, "Symptom", "note", f"{clause}. Write the user-visible symptom before you name a cause."),
            step(1, 0, "Final response", "prov", "Read the final SIP response, or the platform result code, on the failing leg. 100 Trying is not that result."),
            step(0, 1, "Signaling id", "req", f"Join both sides on {actors[0]} to {actors[-1]} with one identifier. A B2BUA changes Call-ID per leg."),
            step(1, 2 if len(actors) > 2 else 0, "Media check", "media", "If signaling completed and audio did not, the fault is on the RTP path: addresses, ports, anchors, and DSCP."),
            step(0, 1, "Falsifier", "err", f"Name the one capture that would kill the favorite wrong hypothesis for {sec['title']}."),
            step(1, 0, "One change", "ok", "Change one thing. Compare the same identifier. Keep the rollback written before you touch the next hop."),
        ]
    if kind == "migration":
        return [
            step(0, 1, "Discover", "note", f"For {clause}, list the numbers, the current route, and the rollback owner before a pilot."),
            step(1, 2 if len(actors) > 2 else 0, "Dual-run", "req", "Both the old and the new path can still complete a test call. Dual-run is not the same as a cut."),
            step(0, 1, "Pilot INVITE", "req", f"Place a pilot INVITE for {sec['title']}. Compare the identifier on the old leg and the new leg."),
            step(1, 0, "200 OK", "ok", "The pilot must reach 200 OK and two-way media, not only a 180. Early media can hide a broken answer."),
            step(1, 2 if len(actors) > 2 else 0, "Cutover", "req", "Move the route, the carrier, or the user only after the pilot evidence is filed."),
            step(2 if len(actors) > 2 else 1, 0, "Rollback", "err", "Restore the previous route if the hypercare counter moves the wrong way. Rehearse this before the irreversible gate."),
        ]
    if kind == "practice":
        topics = practice_topics(sec) or [sec["title"], "the final response", "the media leg", "the identifier"]
        rows = []
        for i, topic in enumerate(topics[:6]):
            label = topic if len(topic) <= 28 else topic[:27] + "…"
            rows.append(step(i % 2, (i + 1) % 2, label, "note",
                             f"Practice item from {sec['title']}: {topic}. Explain it on a real leg, then check the revealed answer in the bank."))
        return rows
    if kind == "config":
        return [
            step(0, 0, "Open the object", "note", f"In {name}, open the object this section names: {clause}."),
            step(0, 1, "Set the route", "req", fact),
            step(1, 1, "Bind identity", "req", "Save the user, device, and number together. A device without a matching identity does not prove the route."),
            step(1, 0, "Validate", "ok", "Read the saved object back. Do not trust the toast alone."),
            step(0, 1, "Test INVITE", "req", "Place one test call. Capture the INVITE and the final response on that leg."),
            step(1, 0, "200 OK", "ok", "Two-way media after 200 OK is the pass. A 180 alone is not."),
        ]
    if kind == "arch":
        return [
            step(0, 1, "Control", "note", f"{clause}. Control decides whether the call may proceed."),
            step(1, 2 if len(actors) > 2 else 0, "Signaling", "req", fact),
            step(1, 0, "Media", "media", "Media follows SDP, or the platform media anchor. It does not have to follow the SIP hops."),
            step(0, 1, "Identity", "req", "Name what is authenticated: device, user, trunk, or webhook. A trusted IP is not a user identity."),
            step(1, 2 if len(actors) > 2 else 0, "Recorder", "note", "Recording, if it is on this path, is a tap or a fork. Say whether it is in the media path."),
            step(2 if len(actors) > 2 else 1, 0, "Failure domain", "err", "Name the smallest piece whose loss drops this call, and what still works beside it."),
        ]
    if kind == "api":
        return [
            step(0, 1, "Authorize", "req", f"{clause}. Use the platform's token or role. Do not put a long-lived secret in a page."),
            step(1, 0, "Invoke", "req", fact),
            step(1, 2 if len(actors) > 2 else 0, "Webhook", "note", "The event is a notification. Delivery is at least once, so the handler must be idempotent."),
            step(0, 1, "Retry", "err", "A 429 or a timeout retries with backoff. A 4xx that is not 429 or 408 is not a retry storm to ignore."),
            step(1, 0, "Correlate", "ok", "Store the platform id on your side before you return, so a replay does not create a second action."),
            step(0, 1, "Prove", "note", "One successful call and one rejected call belong in the evidence, with the ids and the status codes."),
        ]
    if kind == "e911":
        return [
            step(0, 1, "Discover", "note", f"{clause}. Location is learned from the network, not typed by the caller at the moment of the call."),
            step(1, 0, "ERL or HELD", "req", fact),
            step(0, 1, "INVITE", "req", "The emergency INVITE carries the callback number and the location the platform has. A wrong ELIN sends the return call to the wrong site."),
            step(1, 2 if len(actors) > 2 else 0, "PSAP", "ok", "The call must reach the PSAP that serves that location. Ray Baum's Act expects a dispatchable location."),
            step(1, 0, "On-site", "note", "Kari's Law: the on-site notification fires as well as the outbound call. Test it. Do not assume the trunk did both."),
            step(2 if len(actors) > 2 else 0, 1, "Callback", "req", "The PSAP callback must hit the ELIN or the location path you proved, not a generic main number."),
        ]
    if kind == "evidence":
        return [
            step(0, 0, "Leg", "note", f"{clause}. Name the hop that failed, not the whole product."),
            step(0, 1, "Identifier", "req", f"Write the {actors[-1] if False else 'join'} key this system actually uses. {fact}"),
            step(1, 1, "Counter", "note", "Name the counter that moves when this fault is real, and the interval you will read."),
            step(1, 0, "Capture", "media", "Attach the ladder, the packet capture, the CLI output, or the report row. A screenshot of a green icon is not the capture."),
            step(0, 1, "Time", "note", "Put one time zone on every artifact. CUIC, the phone, and the SBC often disagree."),
            step(1, 0, "Hand-off", "ok", "Someone who was not on the bridge should be able to follow the pack without asking you."),
        ]
    if kind == "design":
        return [
            step(0, 1, "Failure domain", "note", f"{clause}. Draw the piece that can fail alone."),
            step(1, 0, "Capacity", "req", fact),
            step(0, 1, "Identity", "req", "Say who is authenticated and where the directory lives when the call is up."),
            step(1, 2 if len(actors) > 2 else 0, "Media", "media", "Say where RTP is anchored, and what happens if that anchor restarts."),
            step(1, 0, "Overflow", "err", "When the unit saturates, name the user-visible symptom: busy, queue, or one-way audio."),
            step(0, 1, "Prove", "ok", "Name the report or counter you will read on the Monday after cutover."),
        ]
    if kind == "reference":
        return [
            step(0, 1, "Term", "note", f"{clause}. Use the product's name, not a nickname from another vendor."),
            step(1, 0, "Current doc", "req", "Open the vendor's current document for this term before you change a route or a flow."),
            step(0, 1, "Lab check", "ok", fact),
            step(1, 0, "Do not copy", "err", "A glossary line is not a configuration. Copy the idea, then prove it on a non-production call."),
        ]
    if kind == "interview":
        return [
            step(0, 1, "INVITE", "req", f"Draw the call they asked about in {clause}. Start with who sends INVITE."),
            step(1, 0, "100 Trying", "prov", "Say out loud that 100 Trying is hop by hop. It is the usual trick question."),
            step(1, 2 if len(actors) > 2 else 0, "Final response", "ok", fact),
            step(0, 1, "ACK", "req", "A 2xx ACK is end to end. A non-2xx ACK is hop by hop, with the 487 after CANCEL."),
            step(0, 1, "RTP", "media", "Point at SDP, not at the SIP hops, when they ask where audio goes."),
            step(1, 0, "BYE", "bye", "End the dialog. Then name one failure you would ask the interviewer to add."),
        ]
    if kind == "overview":
        return [
            step(0, 1, "INVITE", "req", f"{clause}. {fact}"),
            step(1, 0, "100 Trying", "prov", "100 Trying only means the next hop is working. It is not ringing."),
            step(1, 2 if len(actors) > 2 else 0, "Route", "req", f"{name} applies its own route, flow, or script."),
            step(2 if len(actors) > 2 else 1, 1, "200 OK", "ok", "The answer completes offer and answer. Read the SDP or the platform media path."),
            step(0, 1, "RTP", "media", "Confirm two-way media. One-way audio is a media fault if the 200 completed."),
            step(0, 1, "BYE", "bye", "BYE closes the dialog you just named. Keep that Call-ID or platform id in the notes."),
        ]
    # call and topic: full dialog, product fact on the second hop
    second = actors[2] if len(actors) > 2 else actors[-1]
    return [
        step(0, 1, "INVITE", "req", f"{clause}. {actors[0]} sends INVITE. {fact}"),
        step(1, 0, "100 Trying", "prov", "100 Trying is hop by hop. On UDP it stops INVITE retransmits. It does not mean the far end is ringing."),
        step(1, 2 if len(actors) > 2 else 0, "Next leg", "req", f"{name} starts the leg toward {second}. If this hop is a B2BUA, the Call-ID changes here."),
        step(2 if len(actors) > 2 else 1, 1, "180 Ringing", "prov", "180 Ringing is provisional. The dialog is not confirmed. A phone may play local ringback from this response."),
        step(2 if len(actors) > 2 else 1, 1, "200 OK", "ok", "The 200 carries the SDP answer, or the platform equivalent. Offer and answer are complete."),
        step(0, 1, "ACK", "req", "For a 2xx, ACK is end to end. It is not retransmitted as its own INVITE transaction."),
        step(0, 2 if len(actors) > 2 else 1, "RTP", "media", "Media follows the negotiated addresses. One-way audio after a completed 200 is an RTP problem."),
        step(0, 1, "BYE", "bye", "Either side sends BYE inside the dialog. The identifier stays the same until the 200 for the BYE."),
        step(1, 0, "200 OK", "ok", "The BYE is confirmed. A later request with this identifier is a new problem, not this call."),
    ]


BREAKS = {
    "503": [
        (0, 1, "INVITE", "req", "INVITE leaves {who}. This is the call {title} is about."),
        (1, 0, "503", "err", "503 means the next hop could not complete the request. Read Retry-After if it is present. Do not treat 503 as a busy user."),
        (0, 1, "ACK", "req", "The non-2xx ACK is hop by hop. It completes the transaction. It does not open a dialog."),
        (1, 0, "Timer F", "err", "If no final response arrives, Timer F fires at 64 times T1, 32 seconds on UDP. That is a different fault from a 503 you did receive."),
        (0, 1, "One change", "note", "Change one route, one peer, or one capacity limit. Send the same INVITE shape again."),
    ],
    "486": [
        (0, 1, "INVITE", "req", "{title}: the caller sends INVITE."),
        (1, 0, "180 Ringing", "prov", "180 means alerting started. The dialog is still unconfirmed."),
        (1, 0, "486 Busy", "err", "486 Busy Here is a final response from the user agent. It is not the same tone as a network reorder from 503."),
        (0, 1, "ACK", "req", "ACK the 486 hop by hop. The dialog, if any early dialog existed, ends."),
        (1, 0, "Coverage", "note", "Only after the 486 is explained do you look at hunt, voicemail, or forward-no-answer. Do not skip the response code."),
    ],
    "488": [
        (0, 1, "INVITE", "req", "{title}. The offer is in this INVITE. A codec or SRTP mismatch is answered with 488, not with a busy tone."),
        (1, 0, "488", "err", "488 Not Acceptable Here means the offer did not match. Compare codec lists, ptime, and SRTP before you add a transcoder."),
        (0, 1, "ACK", "req", "ACK the 488. Then capture the SDP that was offered and the SDP the far end can accept."),
        (1, 0, "re-INVITE", "req", "A corrected offer is a new INVITE or a re-INVITE with a new CSeq. Do not reuse the rejected SDP and hope."),
    ],
    "timer": [
        (0, 1, "INVITE", "req", "{title}. UDP will retransmit this INVITE at T1, then back off, until Timer B."),
        (0, 1, "T1 500 ms", "note", "Default T1 is 500 ms. The first retransmission waits one T1."),
        (0, 1, "T2 4 s", "note", "The cap between retransmissions for non-INVITE, and the T2 ceiling, is 4 seconds."),
        (1, 0, "Timer B", "err", "Timer B is 64 times T1, 32 seconds. When it fires, the INVITE transaction failed. You did not get a final response."),
        (0, 1, "Trace", "note", "A missing 100 Trying on UDP makes the UAC keep retransmitting. Find the hop that never answered."),
    ],
    "oneway": [
        (0, 1, "INVITE", "req", "{title}. Signaling is the first question, not the phone firmware."),
        (1, 0, "200 OK", "ok", "If the 200 completed, offer and answer finished. The dialog is up."),
        (0, 1, "ACK", "req", "ACK the 200. Then stop looking at SIP for the silence and open the media path."),
        (0, 1, "RTP one way", "media", "One direction of RTP is missing or going to the wrong address. Compare SDP c= and m= with the packets on the wire, on both sides of every B2BUA."),
        (1, 0, "Anchor", "err", "An SBC, MTP, or ALG that rewrote only one direction leaves the call up and the audio one-way."),
    ],
    "cert": [
        (0, 1, "ClientHello", "req", "{title}. The SIP TLS handshake starts before any INVITE is accepted."),
        (1, 0, "Certificate", "err", "The chain, the name, and the date have to match what the peer trusts. An expired certificate fails the handshake, not the dial plan."),
        (0, 1, "INVITE", "req", "Only after the handshake do you see INVITE. No INVITE in the capture means you are still on TLS or TCP."),
        (1, 0, "Trust store", "note", "Fix the one certificate or the one trust. Then place the same call. Do not also change the route."),
    ],
    "dns": [
        (0, 1, "SRV lookup", "req", "{title}. The SIP target is often an SRV name, not a single A record."),
        (1, 0, "NXDOMAIN", "err", "NXDOMAIN or a stale TTL sends the INVITE nowhere, or to a retired address."),
        (0, 1, "TTL", "note", "Failover waits out the TTL you published plus the client's cache. A low TTL is a choice, not a default you can assume."),
        (1, 0, "INVITE", "req", "After the name resolves, the INVITE goes to that socket. Capture the DNS answer and the first INVITE together."),
    ],
    "cancel": [
        (0, 1, "INVITE", "req", "{title}. The caller hangs up before the final response."),
        (1, 0, "180 Ringing", "prov", "180 created an early dialog. The call is not answered."),
        (0, 1, "CANCEL", "req", "CANCEL asks the next hop to stop the unanswered INVITE. It is its own transaction."),
        (1, 0, "200 CANCEL", "ok", "200 OK answers the CANCEL. It does not answer the original INVITE."),
        (1, 0, "487", "err", "487 Request Terminated is the final response to the INVITE."),
        (0, 1, "ACK", "req", "ACK the 487 hop by hop. Missing that ACK makes the 487 retransmit."),
    ],
    "refer": [
        (0, 1, "REFER", "req", "{title}. REFER asks the other user agent to send a new request. Refer-To names the target."),
        (1, 0, "202", "prov", "202 Accepted means the REFER was accepted. It does not mean the transfer target answered."),
        (1, 0, "NOTIFY", "note", "NOTIFY carries a sipfrag of the new request's progress. Read that body. The transfer result is in there."),
        (0, 1, "BYE", "bye", "The original dialog ends only when that side sends BYE, after the new dialog is up. Do not BYE before the NOTIFY says success."),
    ],
    "hold": [
        (0, 1, "re-INVITE", "req", "{title}. Same Call-ID, new CSeq, SDP a=sendonly. Hold is not a second call."),
        (1, 0, "200 OK", "ok", "The held party should answer a=recvonly. a=sendrecv means the hold did not take."),
        (0, 1, "ACK", "req", "ACK locks the held session."),
        (0, 1, "Resume", "req", "Resume is another re-INVITE with a=sendrecv."),
        (1, 0, "200 OK", "ok", "The answer returns to sendrecv. A failed resume leaves the dialog up and the media on hold."),
    ],
    "srtp": [
        (0, 1, "INVITE", "req", "{title}. The offer asks for RTP/SAVP or a DTLS-SRTP setup."),
        (1, 0, "488 or 200", "err", "A suite mismatch is often 488. A 200 with the wrong keys still fails media. Compare the crypto or the fingerprint on both legs."),
        (0, 1, "SRTP", "media", "If signaling completes and audio fails, compare the SRTP profile. A B2BUA may terminate SRTP on one leg and offer RTP on the other."),
    ],
    "failover": [
        (0, 1, "OPTIONS", "req", "{title}. OPTIONS is the usual keepalive. Three misses, or the configured count, mark the peer down."),
        (1, 0, "Timeout", "err", "The peer stops answering. New INVITEs must take the next route, not the dead one."),
        (0, 1, "INVITE", "req", "The next peer gets a new INVITE. In-dialog calls on the dead peer do not magically move unless the product says they do."),
        (1, 0, "200 OK", "ok", "Prove a new call completes on the backup. Then decide what happened to the calls that were already up."),
    ],
    "queue": [
        (0, 1, "INVITE", "req", "{title}. The contact arrives and the script starts."),
        (1, 0, "Queue", "note", "The caller is queued. That is not the same as an agent alert."),
        (1, 0, "RONA", "err", "If the agent is offered the contact and does not answer, RONA returns it to queue. Check the ring time and the agent state, not the PSTN."),
        (0, 1, "Next agent", "ok", "The next ready agent is offered the same contact id. CUIC or the platform report should show both offers."),
    ],
}


def break_key(sec: dict) -> str:
    blob = blob_of(sec)
    rules = [
        (r"503|retry storm", "503"),
        (r"486|busy|reorder", "486"),
        (r"488|codec|transcoder", "488"),
        (r"timer|retransmit", "timer"),
        (r"one-way|asymmetr|blackhole|dead air|no audio", "oneway"),
        (r"cert|tls|certificate", "cert"),
        (r"dns|nxdomain|srv", "dns"),
        (r"cancel", "cancel"),
        (r"refer|transfer", "refer"),
        (r"hold|sendonly|moh", "hold"),
        (r"srtp|sdes", "srtp"),
        (r"failover|srst|split brain", "failover"),
        (r"rona|queue|hunt", "queue"),
    ]
    for pat, key in rules:
        if re.search(pat, blob):
            return key
    order = ["503", "timer", "oneway", "cert", "486", "failover", "488", "dns"]
    digest = int(hashlib.sha256(("fail:" + sec["id"]).encode()).hexdigest()[:6], 16)
    return order[digest % len(order)]


def break_steps(sec: dict, who: str) -> list[dict]:
    key = break_key(sec)
    rows = []
    for f, t, label, kind, cap in BREAKS[key]:
        text = cap.format(title=sec["title"], who=who)
        rows.append(step(f, t, label, kind, text))
    return rows


def header_lines(sec: dict, steps: list[dict], name: str) -> list[str]:
    first = steps[0]["label"] if steps else "INVITE"
    blob = blob_of(sec)
    if "hold" in blob or "sendonly" in blob:
        return [
            "re-INVITE sip:bob.example SIP/2.0",
            "Call-ID: lab-dialog-001",
            "CSeq: 2 INVITE",
            "Content-Type: application/sdp",
            "a=sendonly",
            f"Section: {sec['title'][:72]}",
        ]
    if re.search(r"sdp|rtp|codec|srtp", blob):
        return [
            "v=0",
            "o=lab 1 1 IN IP4 192.0.2.10",
            "c=IN IP4 192.0.2.10",
            "m=audio 16384 RTP/AVP 0",
            "a=rtpmap:0 PCMU/8000",
            f"Focus: {first}",
        ]
    return [
        f"{first} sip:lab.example SIP/2.0",
        "Via: SIP/2.0/TLS lab.example;branch=z9hG4bK-lab",
        "Max-Forwards: 70",
        "From: Alice;tag=from-a",
        "To: Bob",
        "Call-ID: lab-dialog-001",
        "CSeq: 1 INVITE",
        f"X-Section: {name}",
    ]


def mock_kind(name: str, kind: str) -> str:
    if name in {"CUBE"} or kind == "fault" and name == "CUBE":
        return "cli"
    if name in {"CUCM", "Unity Connection"}:
        return "admin"
    if name in {"Webex Calling", "Webex Contact Center"}:
        return "hub"
    if name in {"UCCE", "PCCE", "CUIC"}:
        return "finesse"
    if name in {"Teams Phone"}:
        return "teams"
    if name in {"Amazon Connect"}:
        return "connect"
    return "cli" if kind == "fault" else "admin"


def mock_lines(kind_name: str, sec: dict, steps: list[dict], fact: str) -> list[str]:
    focus = sec["title"][:78]
    labels = [s["label"] for s in steps[:3]]
    if kind_name == "cli":
        return [
            "lab example, not a production capture",
            f"focus: {focus}",
            "show sip-ua status",
            "show dial-peer voice summary",
            "show voip rtp connections",
            f"first message: {labels[0] if labels else 'INVITE'}",
        ]
    if kind_name == "hub":
        return [
            "Webex Control Hub, lab example",
            "Calling > Call Routing",
            f"focus: {focus}",
            fact[:110],
            f"prove: {labels[0] if labels else 'INVITE'}",
        ]
    if kind_name == "finesse":
        return [
            "Finesse desktop, lab example",
            "Voice: Ready",
            "CUIC is not on this screen's RTP",
            f"focus: {focus}",
            "join: RouterCallKey",
        ]
    if kind_name == "teams":
        return [
            "Teams admin center, lab example",
            "Voice > Direct Routing > SBCs",
            "SIP TLS destination 5061",
            f"focus: {focus}",
            fact[:110],
        ]
    if kind_name == "connect":
        return [
            "Connect contact flow, lab example",
            f"focus: {focus}",
            "Entry: the number or the claimed number",
            "Invoke Lambda only where the flow says",
            f"prove: {labels[0] if labels else 'contact id'}",
        ]
    return [
        "CUCM Administration, lab example",
        "Call Routing > Route/Hunt > Route Pattern",
        f"focus: {focus}",
        "CSS: line partitions, then device partitions",
        f"prove: {labels[0] if labels else 'INVITE'}",
    ]


def art_for(sec: dict, steps: list[dict], actors: list[str], name: str, fact: str, mk: str) -> dict:
    nodes = actors[:4]
    links = []
    for item in steps:
        if item["f"] == item["t"]:
            continue
        if item["f"] >= len(nodes) or item["t"] >= len(nodes):
            continue
        links.append({"a": item["f"], "b": item["t"], "label": item["label"]})
        if len(links) == 6:
            break
    packets = []
    for i, item in enumerate(steps[:8]):
        src = actors[item["f"]] if item["f"] < len(actors) else actors[0]
        dst = actors[item["t"]] if item["t"] < len(actors) else actors[-1]
        packets.append({
            "n": i + 1,
            "src": src,
            "dst": dst,
            "msg": item["label"],
            "note": item["cap"][:110],
        })
    return {
        "topology": {"title": sec["title"], "nodes": nodes, "links": links},
        "mockup": {"kind": mk, "title": sec["title"], "lines": mock_lines(mk, sec, steps, fact)},
        "capture": {"title": sec["title"], "packets": packets},
    }


def keys_for(name: str, idname: str, fact: str, steps: list[dict]) -> list[list[str]]:
    return [
        [idname, "Join the logs on this"],
        [name, fact[:72]],
        [steps[0]["label"], "First message in this section"],
        ["LICC", "Leg, id, counter, capture"],
    ]


def cite_for(name: str, kind: str) -> str:
    if name == "Webex Calling":
        return "Webex Calling port reference and RFC 3261"
    if name == "Teams Phone":
        return "Microsoft Learn Direct Routing and RFC 3261"
    if name == "UCCE":
        return "Cisco CVP 15 comprehensive model and RFC 3261"
    if name == "E911":
        return "CER, RFC 5985 HELD, Kari's Law, Ray Baum's Act"
    if name == "QoS":
        return "ITU-T G.114 and Cisco collaboration QoS marking"
    if name in {"SIP", "CUBE", "CUCM"}:
        return "RFC 3261, RFC 3264, and the Cisco collaboration guide for this hop"
    if kind == "migration":
        return "Campus migration habit: dual-run, pilot, rollback"
    return f"{name} current admin guide and RFC 3261 where the leg is SIP"


def make_flow(fid: str, title: str, why: str, cite: str, actors: list[str], steps: list[dict], *,
              layout: str, chart: str, icon: str, keys: list, header: str | None,
              header_lines: list[str] | None, audio: bool, scenarios: list[str] | None,
              art: dict | None, walkthrough: bool, section_id: str | None) -> dict:
    flow = {
        "id": fid,
        "title": title,
        "why": why,
        "cite": cite,
        "layout": layout,
        "actors": actors,
        "chart": chart,
        "icon": icon,
        "keys": keys,
        "header": header,
        "audio": audio,
        "steps": steps,
        "walkthrough": walkthrough,
    }
    if header_lines:
        flow["headerLines"] = header_lines
    if scenarios:
        flow["scenarios"] = scenarios
    if art:
        flow["art"] = art
    if section_id:
        flow["sectionId"] = section_id
    return flow


def audio_wanted(sec: dict) -> bool:
    blob = blob_of(sec) + " " + sec["group"].lower()
    return bool(re.search(r"sip|media|codec|qos|rtp|tone|fax|jitter|mos|voice|cube|calling", blob))


def layout_for(kind: str) -> str:
    if kind in {"config", "evidence", "design", "reference", "practice"}:
        return "tree"
    return "ladder"


def flagship(sec: dict) -> list[dict] | None:
    """Hand-checked ladders for the sections a reviewer opens first."""
    sid = sec["id"]
    if sid == "proto-sip-master":
        return [
            step(0, 1, "INVITE", "req", "Alice sends INVITE. Via carries the branch, From has a tag, and CSeq starts this transaction."),
            step(1, 0, "401", "err", "A 401 from the UAS challenges the user. A 407 would be the proxy's challenge. They are not the same hop."),
            step(0, 1, "ACK", "req", "ACK completes the non-2xx transaction. It is hop by hop."),
            step(0, 1, "INVITE", "req", "The new INVITE carries Authorization and a new CSeq and branch. The Call-ID stays if this is still the same attempt."),
            step(1, 0, "200 OK", "ok", "The 200 brings the To tag and the SDP answer. The dialog is confirmed only after this."),
            step(0, 1, "ACK", "req", "This ACK is end to end because the response was a 2xx."),
            step(0, 1, "491", "err", "A glare 491 means both sides sent a re-INVITE. Back off and retry one of them. Do not treat it as a busy user."),
            step(0, 1, "BYE", "bye", "BYE uses the same Call-ID and tags. A BYE glare is two BYEs crossing; both still get a 200."),
        ]
    if sid == "found-4":
        return [
            step(0, 1, "INVITE", "req", "A method starts a transaction. INVITE is the method that opens a dialog when the far end answers."),
            step(1, 0, "100 Trying", "prov", "100 Trying is hop by hop. It ends INVITE retransmits on UDP. It is not a dialog."),
            step(1, 2, "INVITE", "req", "A B2BUA creates a second dialog. The Call-ID on this leg is new. Session-ID, if present, is the header that still joins them."),
            step(2, 1, "183", "prov", "183 with SDP is early media. A provisional is not the final answer. 100rel makes it reliable."),
            step(1, 2, "PRACK", "req", "PRACK acknowledges a reliable provisional. It has its own transaction and a RAck."),
            step(2, 1, "200 OK", "ok", "The final response confirms the dialog and finishes offer and answer."),
            step(0, 1, "ACK", "req", "2xx ACK is end to end."),
            step(0, 2, "RTP", "media", "Media uses the SDP addresses, which may not be the B2BUA signaling addresses."),
        ]
    if sid == "hub-sip":
        return [
            step(0, 1, "INVITE", "req", "The SIP chapter starts here: one INVITE, one Call-ID, one From tag."),
            step(1, 2, "Fork", "req", "A proxy may fork that INVITE. Each branch has its own branch id."),
            step(2, 1, "180 Ringing", "prov", "One target rings. 180 does not cancel the other branches."),
            step(2, 1, "200 OK", "ok", "The first 200 wins the dialog. The proxy now has a confirmed branch."),
            step(1, 2, "CANCEL", "req", "The proxy cancels the branches that are still outstanding."),
            step(0, 1, "ACK", "req", "ACK confirms the winning 200 end to end."),
            step(0, 2, "RTP", "media", "Audio follows the winner's SDP."),
            step(0, 2, "BYE", "bye", "BYE ends that dialog only."),
        ]
    if sid == "hub-cube-sbc":
        return [
            step(0, 1, "INVITE", "req", "The SIP trunk hits CUBE. Normalization and the dial-peer happen before the provider sees the request."),
            step(1, 0, "OPTIONS", "req", "OPTIONS is the keepalive. When it fails, new calls should hunt, not keep using the dead peer."),
            step(1, 2, "INVITE", "req", "The outbound dial-peer sends a new Call-ID. CUBE is a B2BUA."),
            step(2, 1, "200 OK", "ok", "The far end answers."),
            step(1, 0, "200 OK", "ok", "CUBE answers the original leg and anchors media."),
            step(0, 1, "REFER", "req", "A REFER that arrives here is consumed or passed by policy. 202 is not the transferred call's answer."),
            step(1, 2, "Failover", "err", "Box-to-box HA moves new calls. A call already up on the dead box does not silently continue."),
        ]
    if sid in {"prod-cube"}:
        return [
            step(0, 1, "INVITE leg A", "req", "CUCM sends INVITE to the dial-peer that targets CUBE. This Call-ID belongs to leg A."),
            step(1, 0, "100 Trying", "prov", "CUBE answers 100 Trying on leg A so CUCM stops retransmitting."),
            step(1, 2, "INVITE leg B", "req", "CUBE is a B2BUA. Leg B has a new Call-ID, a new From tag, and the SDP CUBE is willing to anchor."),
            step(2, 1, "183 or 180", "prov", "Early media, if it comes, is 183 with SDP. 180 alone can be local ringback."),
            step(2, 1, "200 OK", "ok", "The provider answers on leg B."),
            step(1, 0, "200 OK", "ok", "CUBE answers leg A. CUCM is not in the RTP path unless an MTP was inserted."),
            step(0, 1, "ACK", "req", "CUBE consumes the ACK on leg A and generates the ACK on leg B."),
            step(0, 2, "RTP", "media", "Flow-through media is anchored on CUBE. Compare c= and m= on both legs if audio is one-way."),
            step(0, 1, "BYE", "bye", "BYE on one leg is translated into BYE on the other. The Call-IDs stay different."),
        ]
    if sid == "hub-cucm":
        return [
            step(0, 1, "REGISTER", "req", "The phone registers. The device is not in the route plan until this succeeds."),
            step(0, 1, "Digits", "note", "CUCM searches line CSS partitions first, then the device CSS. First match wins."),
            step(1, 1, "Route pattern", "req", "The pattern points at a route list, not directly at a gateway, when you use a list."),
            step(1, 2, "Route group", "req", "The route group picks a member trunk or gateway."),
            step(2, 1, "INVITE", "req", "That member sends INVITE. Capture this Call-ID separately from the phone leg if a B2BUA sits behind it."),
            step(2, 0, "200 OK", "ok", "Answer and media follow that selection. A later pattern is never tried after the first match."),
        ]
    if sid in {"prod-cucm"}:
        return [
            step(0, 1, "Digits", "note", "The phone sends the digits. CUCM searches the line CSS partitions first, then the device CSS. First match wins."),
            step(1, 1, "Route pattern", "req", "The matching route pattern points at a route list."),
            step(1, 1, "Route list", "req", "The route list tries route groups in order."),
            step(1, 2, "Trunk", "req", "The route group picks a trunk or gateway. That hop sends INVITE."),
            step(2, 1, "200 OK", "ok", "The far end answers. Read the Call-ID on the trunk, not only the phone's leg."),
            step(0, 2, "RTP", "media", "Phone-to-phone media may go direct. A trunk call's media goes where SDP says, often via CUBE."),
        ]
    if sid == "prod-webex":
        return [
            step(0, 1, "Location", "note", "The user and the number live in a Webex Calling location. The location picks Calling Plan or a Local Gateway."),
            step(1, 1, "Calling Plan", "note", "Calling Plan has no customer Local Gateway. Do not look for TCP 5062 on that path."),
            step(1, 2, "Local Gateway", "req", "If the location uses a gateway, a certificate trunk sends SIP TLS toward TCP 5062. A registration trunk uses TCP 8934."),
            step(2, 1, "200 OK", "ok", "The PSTN answer returns through the gateway."),
            step(0, 2, "SRTP", "media", "Media toward Webex Calling is SRTP."),
            step(0, 1, "BYE", "bye", "BYE clears the Webex leg. The gateway clears its own PSTN Call-ID."),
        ]
    if sid in {"vd-webex-calling-call-flow"}:
        return [
            step(0, 1, "Dial", "req", "The app sends the call into Webex Calling. The location decides the PSTN path."),
            step(1, 2, "INVITE", "req", "A certificate Local Gateway receives outbound SIP TLS toward TCP 5062. Registration trunks use TCP 8934 and reuse that session. Calling Plan has no Local Gateway."),
            step(2, 1, "100 Trying", "prov", "100 Trying is hop by hop on the gateway leg."),
            step(2, 1, "200 OK", "ok", "The PSTN answer returns through the gateway. Media toward Webex is SRTP."),
            step(0, 1, "RTP", "media", "Confirm SRTP on the Webex side and whatever the trunk negotiated on the PSTN side."),
            step(0, 1, "BYE", "bye", "BYE clears both the Webex leg and the gateway leg."),
        ]
    if sid == "prod-teams":
        return [
            step(0, 1, "Choose PSTN", "note", "Teams Phone PSTN is Calling Plan, Operator Connect, or Direct Routing. Only Direct Routing uses the customer SBC."),
            step(1, 2, "INVITE", "req", "Direct Routing signaling is SIP TLS on 5061 toward sip.pstnhub.microsoft.com, with sip2 and sip3 for failover."),
            step(2, 1, "180 Ringing", "prov", "Ringing is still a signaling event. Media bypass does not move this message."),
            step(2, 1, "200 OK", "ok", "Answer completes the dialog."),
            step(0, 2, "Media", "media", "Without bypass, media uses the processor ranges UDP 3478-3481 and 49152-53247. Bypass is not supported on IPv6."),
            step(1, 2, "BYE", "bye", "BYE stays on the Direct Routing signaling path."),
        ]
    if sid in {"vd-teams-phone-call-flow"}:
        return [
            step(0, 1, "Dial", "req", "The Teams client signals Microsoft 365, not the customer SBC, for the first hop."),
            step(1, 2, "INVITE", "req", "Direct Routing: Microsoft sends SIP TLS to the SBC, or the SBC sends to sip.pstnhub.microsoft.com port 5061. sip2 and sip3 are the failover names."),
            step(2, 1, "183 or 180", "prov", "Ringback may be 180 or early media in 183. Media bypass, if enabled, does not change this signaling."),
            step(2, 1, "200 OK", "ok", "The answer completes the call. Without media bypass, media hairpins on UDP 3478-3481 and 49152-53247."),
            step(0, 2, "RTP", "media", "Media bypass is optional and is not supported on IPv6. Calling Plan and Operator Connect do not use this SBC."),
            step(1, 2, "BYE", "bye", "BYE releases the Direct Routing dialog."),
        ]
    if sid == "hub-icm-ucce":
        return [
            step(0, 1, "SIP INVITE", "req", "Ingress reaches CVP. This chapter's path is caller, CUBE, CVP, ICM, queue, CUCM, Finesse. CUIC is beside that path."),
            step(1, 2, "Route request", "req", "CVP asks ICM. The join key you will need later is RouterCallKey."),
            step(2, 1, "Script", "note", "The script queues or treats. A skill-group rename breaks the historical report even when calls still connect."),
            step(1, 0, "Agent", "ok", "The agent label rings the phone and should pop Finesse."),
            step(0, 1, "Desktop dark", "err", "If the phone rings and the desktop does not, the fault is PG, CTI, or Finesse, not the PSTN leg you already proved."),
            step(0, 1, "RTP", "media", "Audio is still a separate proof. Time zones must match before you compare CUIC to the capture."),
        ]
    if sid in {"prod-ucce"}:
        return [
            step(0, 1, "SIP INVITE", "req", "The ingress gateway sends the call to the CVP call server. This is the switch leg."),
            step(1, 2, "Route request", "req", "CVP, as a routing client, asks ICM through the VRU PG."),
            step(2, 1, "Send to VRU", "note", "ICM returns Send to VRU. A Type 10 Network VRU keeps the handoff simple. The correlation id matches the VRU leg."),
            step(1, 1, "re-INVITE", "req", "The usual transfer to Cisco VVB is a re-INVITE, so CVP stays in signaling. REFER would step CVP out."),
            step(1, 1, "VXML", "note", "The VVB plays the script from the VXML server while the caller is treated."),
            step(2, 0, "Agent label", "ok", "ICM returns an agent label. CUCM rings the phone and Finesse shows the same contact. CUIC is not in the RTP path."),
            step(0, 1, "RTP", "media", "Audio is between the caller and the agent endpoint, or the whisper and record legs you explicitly built. Join logs with RouterCallKey."),
        ]
    if sid == "hub-qos":
        return [
            step(0, 1, "DSCP 46", "media", "The phone marks RTP as EF. Signaling is commonly CS3, DSCP 24, on a Cisco collaboration design."),
            step(1, 1, "Trust", "note", "The access switch trusts or remarks that mark. An untrusted edge that rewrites EF to BE starves the call."),
            step(1, 2, "Queue", "req", "The WAN queue serves EF ahead of bulk data. Measure the queue, do not only draw it."),
            step(2, 0, "150 ms", "ok", "Add packetization, queuing, serialization, propagation, and jitter buffer. G.114 plans around 150 ms one way."),
        ]
    if sid == "found-11":
        return [
            step(0, 1, "Switch port", "note", "CER learns the phone's switch port and maps that port to an ERL."),
            step(1, 1, "ELIN", "req", "The ERL selects the ELIN, the callback number the PSAP will use."),
            step(1, 2, "INVITE", "req", "The emergency INVITE uses that ELIN. A wrong port-to-ERL map sends help to the wrong floor."),
            step(2, 0, "On-site", "note", "Kari's Law: on-site notification has to fire as well. Ray Baum's Act expects a dispatchable location."),
            step(2, 1, "Callback", "ok", "A return call to the ELIN must reach the site you proved, not a generic attendant."),
        ]
    if sid == "trick-0":
        return [
            step(0, 1, "200 OK", "ok", "One-way audio after 200 OK means signaling finished. Do not restart the cluster first."),
            step(0, 1, "ACK", "req", "ACK is present. The dialog is confirmed."),
            step(0, 1, "SDP c=", "media", "Compare the connection address and port on both sides of each B2BUA with the RTP you actually captured."),
            step(1, 0, "One direction", "err", "One RTP direction is missing, blackholed, or sent to the pre-NAT address."),
            step(1, 0, "One change", "note", "Fix the one anchor, ALG, or route. Place the same call and compare the same Call-ID."),
        ]
    if sid == "home":
        return [
            step(0, 1, "SIP ladder", "req", "Start with INVITE, the final response, ACK, and RTP. 100 Trying is hop by hop."),
            step(1, 2, "CUCM and CUBE", "req", "Digit analysis, then a B2BUA. Each CUBE leg has its own Call-ID."),
            step(2, 1, "Cloud PSTN", "note", "Webex Calling Local Gateway and Teams Direct Routing are different trunks. Calling Plan uses neither customer SBC."),
            step(1, 0, "Contact center", "req", "UCCE: switch leg, CVP, ICM, VVB, agent. CUIC is beside the audio."),
            step(0, 1, "E911", "err", "Prove location and on-site notification before you prove a normal call."),
            step(1, 2, "QoS", "media", "EF for bearer, DSCP 46. Measure the delay budget against 150 ms."),
            step(0, 1, "LICC", "ok", "On a fault: one leg, one identifier, one counter, one capture, one change."),
        ]
    return None


def walkthroughs() -> list[dict]:
    specs = [
        ("walk-pstn-agent", "PSTN call to a UCCE agent",
         "A full walk from the carrier to the agent desktop, including the VRU and the agent leg.",
         "Cisco CVP 15 comprehensive model",
         ["Carrier", "CUBE", "CVP", "Agent"],
         [
            (0, 1, "INVITE", "The carrier sends INVITE to CUBE."),
            (1, 2, "Switch leg", "CUBE sends the switch leg to the CVP call server. New Call-ID."),
            (2, 2, "ICM", "CVP asks ICM for a label. This request is not RTP."),
            (2, 2, "Send to VRU", "ICM says Send to VRU. The correlation id will match the treatment leg."),
            (2, 2, "re-INVITE VVB", "CVP re-INVITEs to VVB and stays in signaling."),
            (2, 0, "Treatment", "The caller hears the script. CUIC is not in this audio."),
            (2, 3, "Agent label", "ICM returns the agent label. CUCM rings the phone. Finesse shows the contact."),
            (0, 3, "RTP", "Caller audio reaches the agent endpoint. Join the story with RouterCallKey."),
            (3, 2, "BYE", "The agent or the caller hangs up. BYE clears the legs CVP still holds."),
         ]),
        ("walk-cucm-failover", "CUCM node failover",
         "A phone re-registers to the next CUCM when the primary stops answering.",
         "CUCM clustering behavior",
         ["Phone", "Primary CUCM", "Backup CUCM"],
         [
            (0, 1, "REGISTER", "The phone is registered to the primary."),
            (1, 0, "Silence", "The primary stops answering. Keepalives fail."),
            (0, 2, "REGISTER", "The phone registers to the next server in its list. This is a new registration, not a moved dialog."),
            (0, 2, "INVITE", "A new call uses the backup. A call that was already up may drop."),
            (2, 0, "200 OK", "Prove one new call completes before you call the failover done."),
         ]),
        ("walk-cutover", "Number cutover with rollback",
         "Dual-run a number, pilot it, cut the route, and keep a rehearsed rollback.",
         "Campus migration habit",
         ["Caller", "Old route", "New route"],
         [
            (0, 1, "Discover", "Write the current route and the rollback owner."),
            (0, 1, "INVITE old", "A pilot still completes on the old route."),
            (0, 2, "INVITE new", "The same number completes on the new route while dual-run is open."),
            (1, 2, "Compare ids", "The two Call-IDs or contact ids will differ. Compare the outcome, not the id string."),
            (0, 2, "Cut", "Only now does the carrier or the route pattern prefer the new path."),
            (0, 1, "Rollback", "If hypercare fails, restore the old route before the irreversible gate."),
         ]),
        ("walk-wx-out", "Webex Calling outbound walkthrough",
         "From the Webex app through a Local Gateway to the PSTN.",
         "Webex Calling port reference",
         ["Webex app", "Webex Calling", "Local Gateway", "PSTN"],
         [
            (0, 1, "Dial", "The app asks Webex Calling to place the call."),
            (1, 2, "INVITE", "Certificate trunk: outbound SIP TLS toward TCP 5062. Registration trunk: the session on TCP 8934 is reused."),
            (2, 3, "INVITE", "The gateway sends the provider leg. That Call-ID is not the Webex call id."),
            (3, 2, "200 OK", "The PSTN answers."),
            (2, 1, "200 OK", "The gateway answers Webex Calling."),
            (0, 3, "SRTP", "Media toward Webex is SRTP. The PSTN side is whatever the trunk negotiated."),
            (0, 1, "BYE", "BYE clears the Webex leg and the gateway clears the PSTN leg."),
         ]),
        ("walk-wx-in", "Webex Calling inbound walkthrough",
         "A PSTN call arrives on the Local Gateway and rings a Webex user.",
         "Webex Calling port reference",
         ["PSTN", "Local Gateway", "Webex Calling", "Webex app"],
         [
            (0, 1, "INVITE", "The carrier sends INVITE to the gateway listen port you chose. It is not always 5061."),
            (1, 2, "INVITE", "The gateway sends the call into Webex Calling."),
            (2, 3, "Alert", "The app rings."),
            (3, 2, "200 OK", "The user answers."),
            (0, 3, "SRTP", "Media toward Webex is SRTP."),
            (3, 0, "BYE", "Hangup clears both legs."),
         ]),
        ("walk-teams-out", "Teams Direct Routing outbound",
         "A Teams user calls the PSTN through a customer SBC.",
         "Microsoft Learn Direct Routing",
         ["Teams client", "Microsoft 365", "SBC", "PSTN"],
         [
            (0, 1, "Dial", "The client talks to Microsoft 365 first."),
            (1, 2, "INVITE", "SIP TLS to the SBC, or from the SBC to sip.pstnhub.microsoft.com port 5061."),
            (2, 3, "INVITE", "The SBC places the PSTN leg with its own Call-ID."),
            (3, 2, "200 OK", "The PSTN answers."),
            (0, 3, "Media", "Without bypass, media uses UDP 3478-3481 and 49152-53247. Bypass does not change the signaling."),
            (0, 1, "BYE", "BYE releases Direct Routing. Calling Plan would not have used this SBC."),
         ]),
        ("walk-teams-in", "Teams Direct Routing inbound",
         "The PSTN calls a Teams user through the SBC.",
         "Microsoft Learn Direct Routing",
         ["PSTN", "SBC", "Microsoft 365", "Teams client"],
         [
            (0, 1, "INVITE", "The carrier sends INVITE to the SBC."),
            (1, 2, "INVITE", "The SBC sends SIP TLS to sip.pstnhub.microsoft.com on 5061. sip2 and sip3 are failover."),
            (2, 3, "Alert", "The Teams client rings. The SBC is not the client."),
            (3, 2, "200 OK", "The user answers."),
            (0, 3, "Media", "Media follows the bypass setting. Signaling stays on Direct Routing either way."),
            (3, 0, "BYE", "The hangup clears the Teams leg and the SBC clears the carrier."),
         ]),
        ("walk-cube", "CUBE B2BUA walkthrough",
         "Two Call-IDs, one anchored media path.",
         "RFC 3261 and CUBE B2BUA behavior",
         ["CUCM", "CUBE", "ITSP"],
         [
            (0, 1, "INVITE A", "Leg A Call-ID is the CUCM trunk dialog."),
            (1, 0, "100 Trying", "Hop by hop on leg A."),
            (1, 2, "INVITE B", "Leg B is a new dialog."),
            (2, 1, "200 OK", "The provider answers leg B."),
            (1, 0, "200 OK", "CUBE answers leg A."),
            (0, 1, "ACK", "CUBE consumes ACK on A and sends ACK on B."),
            (0, 2, "RTP", "Flow-through media. CUCM is not in RTP unless an MTP is in the call."),
            (2, 0, "BYE", "BYE is translated across the Call-ID boundary."),
         ]),
        ("walk-hold", "Hold and resume walkthrough",
         "re-INVITE inside one dialog.",
         "RFC 3264",
         ["Holder", "Held party"],
         [
            (0, 1, "Connected", "The first dialog is already up. Same Call-ID."),
            (0, 1, "re-INVITE", "CSeq increases. SDP says a=sendonly."),
            (1, 0, "200 OK", "The answer should be a=recvonly."),
            (0, 1, "ACK", "Hold is locked."),
            (0, 1, "re-INVITE", "Resume offers a=sendrecv."),
            (1, 0, "200 OK", "Answer is sendrecv."),
            (0, 1, "ACK", "Media returns. A failed resume leaves the hold in place."),
         ]),
        ("walk-refer", "Blind transfer walkthrough",
         "REFER, 202, and NOTIFY. 202 is not the answer.",
         "RFC 3515",
         ["Alice", "Bob", "Carol"],
         [
            (0, 1, "REFER", "Alice asks Bob to invite Carol. Refer-To names Carol."),
            (1, 0, "202", "202 means Bob accepted the REFER, not that Carol answered."),
            (1, 2, "INVITE", "Bob sends a new INVITE to Carol. New Call-ID."),
            (2, 1, "200 OK", "Carol answers Bob."),
            (1, 0, "NOTIFY", "The sipfrag in NOTIFY tells Alice that the new call reached 200."),
            (0, 1, "BYE", "Alice leaves the original dialog only after that success."),
         ]),
        ("walk-attended", "Attended transfer walkthrough",
         "Consultation call, then Replaces.",
         "RFC 3891 and RFC 3515",
         ["Alice", "Bob", "Carol"],
         [
            (0, 1, "Hold", "Alice holds Bob with a=sendonly."),
            (0, 2, "INVITE", "Alice consults Carol on a second dialog."),
            (2, 0, "200 OK", "Carol answers the consultation."),
            (0, 1, "REFER", "REFER to Bob carries Replaces for the consultation dialog."),
            (1, 2, "INVITE", "Bob invites Carol with Replaces. Carol swaps the peer."),
            (0, 1, "BYE", "Alice drops off after NOTIFY shows success."),
         ]),
        ("walk-e911", "CER emergency walkthrough",
         "Switch port, ERL, ELIN, PSAP, on-site notification, callback.",
         "CER, Kari's Law, Ray Baum's Act",
         ["Phone", "CER", "PSAP"],
         [
            (0, 1, "Port", "CER learns the switch port."),
            (1, 1, "ERL", "The port maps to an emergency response location."),
            (1, 1, "ELIN", "That ERL selects the callback number."),
            (0, 2, "INVITE", "The emergency call uses the ELIN."),
            (1, 0, "On-site", "Kari's Law: the site notification fires too."),
            (2, 0, "Callback", "A return call to the ELIN reaches this site."),
         ]),
        ("walk-held", "Webex HELD emergency walkthrough",
         "The client asks for location, then the emergency call uses it.",
         "RFC 5985",
         ["Webex client", "Location", "PSAP"],
         [
            (0, 1, "HELD", "The client sends a location request. BSSID, chassis port, or civic address selects the location."),
            (1, 0, "Location", "The response is the dispatchable location, not a guess typed at call time."),
            (0, 2, "INVITE", "The emergency INVITE carries that location reference."),
            (2, 0, "Callback", "Callback uses the number Webex associated with the location."),
         ]),
        ("walk-srst", "SRST fallback walkthrough",
         "The WAN fails and the gateway serves the phones.",
         "CUCM SRST behavior",
         ["Phone", "CUCM", "SRST gateway"],
         [
            (0, 1, "REGISTER", "Phones are registered to CUCM while the WAN is up."),
            (0, 1, "WAN down", "Keepalives to CUCM fail."),
            (0, 2, "Fallback", "The phone registers to the local SRST gateway."),
            (0, 2, "INVITE", "A new call uses the local dial peers. The old CUCM dialog is gone."),
            (1, 0, "WAN up", "When CUCM returns, phones register back. Do not assume held calls survived."),
         ]),
        ("walk-mra", "MRA registration and call",
         "Jabber outside, through Expressway-E and Expressway-C, then a call.",
         "Expressway MRA",
         ["Jabber", "Expressway-E", "Expressway-C", "CUCM"],
         [
            (0, 1, "TLS", "The client hits Expressway-E. The certificate name has to match."),
            (1, 2, "Traversal", "E forwards the registration toward C."),
            (2, 3, "REGISTER", "CUCM sees the device."),
            (0, 3, "INVITE", "The call is signed through the same edge."),
            (0, 3, "Media", "Media may hairpin at E. One-way audio here is often the edge, not the desk phone VLAN."),
         ]),
        ("walk-oneway", "One-way audio walkthrough",
         "Signaling is finished. The fault is the media path.",
         "RFC 3264",
         ["Alice", "SBC", "Bob"],
         [
            (0, 1, "200 OK", "Both SIP legs reached 200 OK."),
            (0, 1, "ACK", "Dialogs are confirmed."),
            (0, 1, "RTP", "Alice sends RTP to the address in her SDP answer."),
            (1, 2, "RTP", "The SBC forwards it, or it does not."),
            (2, 0, "Missing", "Bob's RTP never arrives. Compare c= and the captured destination, per leg."),
            (1, 1, "One change", "Fix the single rewrite. Repeat the same call."),
         ]),
        ("walk-183", "Early media walkthrough",
         "183 with SDP, then a later 200 that may change the media.",
         "RFC 3261 and RFC 3960",
         ["Alice", "Bob"],
         [
            (0, 1, "INVITE", "The INVITE carries the offer."),
            (1, 0, "183", "183 Session Progress can carry SDP. That is early media, not the final answer."),
            (0, 1, "PRACK", "If the 183 was sent reliably, Alice sends PRACK."),
            (1, 0, "200 PRACK", "The reliable provisional is acknowledged."),
            (1, 0, "200 INVITE", "The final 200 may carry a new SDP answer. Play ringback from the right one."),
            (0, 1, "ACK", "ACK completes the INVITE."),
         ]),
        ("walk-cancel", "CANCEL walkthrough",
         "Hang up before answer. 200 for CANCEL, then 487, then ACK.",
         "RFC 3261",
         ["Alice", "Bob"],
         [
            (0, 1, "INVITE", "INVITE is still outstanding."),
            (1, 0, "180", "Early dialog only."),
            (0, 1, "CANCEL", "Alice cancels."),
            (1, 0, "200 CANCEL", "This 200 answers CANCEL, not the call."),
            (1, 0, "487", "The INVITE ends with 487."),
            (0, 1, "ACK", "ACK the 487 or it retransmits."),
         ]),
        ("walk-cert", "SIP TLS certificate failure",
         "The handshake dies before INVITE.",
         "SIP over TLS operations",
         ["UAC", "UAS"],
         [
            (0, 1, "ClientHello", "TCP connects and TLS starts."),
            (1, 0, "Certificate", "The presented chain does not match the name or the date."),
            (0, 1, "Alert", "The handshake fails. There is still no INVITE."),
            (1, 0, "Replace cert", "Install the one certificate that matches the SIP name."),
            (0, 1, "INVITE", "Only the next call shows INVITE. That is the proof."),
         ]),
        ("walk-hunt", "Hunt group to voicemail",
         "No member answers, so coverage takes the call.",
         "CUCM hunt and Unity Connection",
         ["Caller", "CUCM", "Member", "Unity"],
         [
            (0, 1, "INVITE", "The hunt pilot is the called number."),
            (1, 2, "Alert", "The first logged-in member rings."),
            (2, 1, "No answer", "RNA expires. This is not a PSTN failure."),
            (1, 2, "Next", "The hunt algorithm tries the next member."),
            (1, 3, "Forward", "Final coverage sends the call to Unity Connection with the original called party."),
            (3, 0, "200 OK", "The greeting answers. MWI is a later event, not this 200."),
         ]),
        ("walk-wxcc", "Webex Contact Center inbound",
         "Entry point, flow, queue, agent.",
         "Webex Contact Center flow model",
         ["Caller", "Webex CC", "Agent"],
         [
            (0, 1, "Entry", "The number hits an entry point."),
            (1, 1, "Flow", "Flow Designer runs. A bad flow publish is a routing change."),
            (1, 1, "Queue", "The contact waits. That is not an agent alert yet."),
            (1, 2, "Offer", "A ready agent is offered the interaction id."),
            (2, 1, "Answer", "The agent answers in the desktop. Media follows the Webex media path."),
            (2, 0, "Wrap-up", "Wrap-up is after the talk. It is not part of the RTP."),
         ]),
        ("walk-connect", "Amazon Connect inbound",
         "Number, contact flow, queue, CCP.",
         "Amazon Connect contact flow model",
         ["Caller", "Connect", "Agent"],
         [
            (0, 1, "INVITE", "The claimed number enters Connect. There is no customer SBC in this native path."),
            (1, 1, "Flow", "The contact flow runs. Lambda runs only where a block invokes it."),
            (1, 1, "Queue", "The contact queues. The contact id is already assigned."),
            (1, 2, "CCP", "A ready agent gets the contact in the CCP."),
            (2, 0, "Talk", "Audio is between the caller and the agent softphone."),
            (1, 1, "CTR", "The contact trace record is written after the contact. It is evidence, not the live audio."),
         ]),
        ("walk-qos", "EF remarked to best effort",
         "The phone marks EF. A later hop remarks it, and the call starves.",
         "Cisco collaboration QoS",
         ["Phone", "Access", "WAN"],
         [
            (0, 1, "DSCP 46", "The phone sends RTP marked EF."),
            (1, 1, "Trust", "The access port is set to untrusted and rewrites the mark."),
            (1, 2, "BE", "The WAN sees best effort. The EF queue stays empty."),
            (2, 0, "Starve", "Jitter and loss climb when the link is busy. Signaling may still look fine."),
            (1, 1, "Restore", "Trust the voice VLAN or mark at the trusted boundary. Measure again."),
         ]),
        ("walk-pcce", "PCCE inbound walkthrough",
         "The packaged layout still has script, queue, and agent.",
         "PCCE routing model",
         ["Caller", "PCCE", "Agent"],
         [
            (0, 1, "Ingress", "The call enters the packaged ingress."),
            (1, 1, "Script", "The script queues or prompts. Packaging did not remove the script."),
            (1, 2, "Agent", "The peripheral offers the agent."),
            (2, 1, "Answer", "Finesse and the phone have to agree. If the phone rings and the desktop does not, look at CTI."),
            (0, 2, "RTP", "Audio is still a media problem if this 200 completed and one direction is missing."),
         ]),
        ("walk-bypass", "Teams media bypass walkthrough",
         "Signaling stays on Direct Routing. Media takes the bypass path.",
         "Microsoft Learn media bypass",
         ["Teams client", "Microsoft 365", "SBC"],
         [
            (0, 1, "INVITE", "Signaling still goes to Microsoft."),
            (1, 2, "INVITE", "The SBC still speaks SIP to the PSTN hub on 5061."),
            (0, 2, "Media", "With bypass, media can go between the client and the SBC. Signaling did not move with it."),
            (1, 1, "IPv6", "Media bypass is not the IPv6 path. Do not enable it there and expect the same shortcut."),
            (0, 1, "BYE", "BYE is still a signaling message through Microsoft."),
         ]),
        ("walk-dial-peer", "CUBE dial-peer failover",
         "The first outbound peer times out. The next peer gets a new INVITE.",
         "CUBE outbound dial-peer hunting",
         ["CUCM", "CUBE", "Peer A", "Peer B"],
         [
            (0, 1, "INVITE", "CUCM hits CUBE."),
            (1, 2, "INVITE", "CUBE tries the first outbound dial-peer."),
            (2, 1, "Timeout", "Peer A does not answer. OPTIONS or the invite timeout marks it down."),
            (1, 3, "INVITE", "CUBE sends a new INVITE to peer B. New Call-ID on that leg."),
            (3, 1, "200 OK", "Peer B answers."),
            (1, 0, "200 OK", "CUCM sees one answered call. The failed peer is a CUBE event, not a CUCM route-list event, unless you also hunted there."),
         ]),
    ]
    flows = []
    for fid, title, why, cite, actors, rows in specs:
        steps = [step(a, b, label, "req", cap) for a, b, label, cap in rows]
        flows.append(make_flow(
            fid, title, why, cite, actors, steps,
            layout="walk", chart="setup-waterfall", icon="route",
            keys=[["Walkthrough", title], ["Steps", str(len(steps))], ["Offline", "No media files"], ["LICC", "Leg, id, counter, capture"]],
            header="invite", header_lines=None, audio=False,
            scenarios=None, art=None, walkthrough=True, section_id=None,
        ))
    return flows


WALK_MATCH = [
    (r"ucce|cvp|icm", "walk-pstn-agent"),
    (r"pcce", "walk-pcce"),
    (r"failover|cucm", "walk-cucm-failover"),
    (r"cutover|dual-run|migrat", "walk-cutover"),
    (r"webex calling|local gateway", "walk-wx-out"),
    (r"direct routing|teams", "walk-teams-out"),
    (r"cube|dial-peer", "walk-cube"),
    (r"hold|sendonly", "walk-hold"),
    (r"attended|replaces", "walk-attended"),
    (r"refer|transfer", "walk-refer"),
    (r"e911|cer|emergency", "walk-e911"),
    (r"held|redsky", "walk-held"),
    (r"srst", "walk-srst"),
    (r"mra|expressway", "walk-mra"),
    (r"one-way|dead air", "walk-oneway"),
    (r"183|early media|prack", "walk-183"),
    (r"cancel", "walk-cancel"),
    (r"cert|tls", "walk-cert"),
    (r"hunt|voicemail", "walk-hunt"),
    (r"wxcc|webex contact", "walk-wxcc"),
    (r"amazon connect|\bconnect\b", "walk-connect"),
    (r"qos|dscp|remark", "walk-qos"),
    (r"media bypass", "walk-bypass"),
]


def match_walk(sec: dict) -> str | None:
    blob = blob_of(sec)
    for pat, fid in WALK_MATCH:
        if re.search(pat, blob):
            return fid
    return None


def build() -> tuple[list[dict], dict[str, str]]:
    sections = load_sections()
    flows: list[dict] = []
    mapping: dict[str, str] = {}
    used_charts: set[str] = set()
    for sec in sections:
        name, actors, icon, idname, fact = product_of(sec)
        kind = kind_of(sec)
        custom = flagship(sec)
        steps = custom if custom else happy_steps(sec, kind, name, actors, fact)
        # Keep actor indexes inside range. Flagship steps assume their own actors.
        if custom and sec["id"] in {"prod-cube", "hub-cube-sbc"}:
            actors = ["CUCM", "CUBE", "ITSP"]
        elif custom and sec["id"] == "hub-sip":
            actors = ["Alice", "Proxy", "Bob"]
        elif custom and sec["id"] == "found-4":
            actors = ["Alice", "B2BUA", "Bob"]
        elif custom and sec["id"] in {"hub-cucm", "prod-cucm"}:
            actors = ["Phone", "CUCM", "Trunk"]
        elif custom and sec["id"] in {"vd-webex-calling-call-flow", "prod-webex"}:
            actors = ["Webex app", "Webex Calling", "Local Gateway"]
        elif custom and sec["id"] in {"vd-teams-phone-call-flow", "prod-teams"}:
            actors = ["Teams client", "Microsoft 365", "SBC"]
        elif custom and sec["id"] in {"hub-icm-ucce", "prod-ucce"}:
            actors = ["Caller", "CVP", "ICM"]
        elif custom and sec["id"] == "hub-qos":
            actors = ["Phone", "Switch", "WAN"]
        elif custom and sec["id"] == "found-11":
            actors = ["Phone", "CER", "PSAP"]
        elif custom and sec["id"] == "trick-0":
            actors = ["Caller", "SBC", "Agent"]
        elif custom and sec["id"] == "home":
            actors = ["You", "Control", "Media"]
        elif custom:
            actors = ["Alice UAC", "Bob UAS"]
        chart = chart_for(sec)
        used_charts.add(chart)
        primary_id = "sec-" + sec["id"]
        fail_id = "fail-" + sec["id"]
        walk = match_walk(sec)
        scenarios = [primary_id, fail_id]
        if walk:
            scenarios.append(walk)
        header = "hold" if re.search(r"hold|sendonly", blob_of(sec)) else "sdp" if re.search(r"sdp|rtp|codec", blob_of(sec)) else "invite"
        lines = header_lines(sec, steps, name)
        mk = mock_kind(name, kind)
        art = art_for(sec, steps, actors, name, fact, mk)
        flows.append(make_flow(
            primary_id, sec["title"], fact, cite_for(name, kind), actors, steps,
            layout="walk" if sec["id"] == "home" else layout_for(kind),
            chart=chart, icon=icon, keys=keys_for(name, idname, fact, steps),
            header=header, header_lines=lines, audio=audio_wanted(sec) or sec["id"] == "home",
            scenarios=scenarios, art=art, walkthrough=sec["id"] == "home", section_id=sec["id"],
        ))
        fail_actors = actors[:2] if len(actors) >= 2 else actors
        fail = break_steps(sec, name)
        fail_art = art_for(sec, fail, fail_actors, name, fact, mk)
        flows.append(make_flow(
            fail_id, sec["title"] + " — failure path",
            f"The failure variant for {sec['title']}. {fact}",
            cite_for(name, kind), fail_actors, fail,
            layout="ladder", chart=chart, icon=icon,
            keys=keys_for(name, idname, fact, fail),
            header=header, header_lines=header_lines(sec, fail, name),
            audio=False, scenarios=[fail_id, primary_id] + ([walk] if walk else []),
            art=fail_art, walkthrough=False, section_id=sec["id"],
        ))
        mapping[sec["id"]] = primary_id
    flows.extend(walkthroughs())
    # Make sure every chart type is attached to at least one flow.
    missing = [cid for cid in CHARTS if cid not in used_charts]
    donors = [f for f in flows if f.get("sectionId") and not f["id"].startswith("fail-")]
    for cid, donor in zip(missing, donors):
        donor["chart"] = cid
        used_charts.add(cid)
    return flows, mapping


def main() -> None:
    flows, mapping = build()
    ids = [f["id"] for f in flows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate flow ids")
    signatures = []
    for flow in flows:
        if len(flow["steps"]) < 3:
            raise SystemExit(f"short flow {flow['id']}")
        for item in flow["steps"]:
            if not item["cap"] or not item["label"]:
                raise SystemExit(f"empty step in {flow['id']}")
        sig = tuple((s["label"], s["cap"]) for s in flow["steps"])
        signatures.append(sig)
    unique_sigs = len(set(signatures))
    if unique_sigs < 600:
        raise SystemExit(f"only {unique_sigs} distinct step signatures")
    if len(mapping) != 476:
        raise SystemExit(f"mapped {len(mapping)} sections")
    walks = sum(1 for f in flows if f.get("walkthrough"))
    if walks < 20:
        raise SystemExit(f"only {walks} walkthroughs")
    text = (
        "/* Generated by scripts/build-section-flows.py. Do not edit by hand. */\n"
        "window.UC_FLOW_CATALOG = "
        + json.dumps(flows, ensure_ascii=True, separators=(",", ":"))
        + ";\nwindow.UC_SECTION_FLOW = "
        + json.dumps(mapping, ensure_ascii=True, separators=(",", ":"))
        + ";\nwindow.UC_CHART_TYPES = "
        + json.dumps(CHARTS)
        + ";\n"
    )
    if "@" in text:
        raise SystemExit("generated catalog contains @")
    OUT.write_text(text, encoding="utf-8")
    charts_used = {f.get("chart") for f in flows if f.get("chart")}
    arts = set()
    for flow in flows:
        art = flow.get("art") or {}
        for key in ("topology", "mockup", "capture"):
            if key in art:
                arts.add(json.dumps(art[key], sort_keys=True))
    print(
        f"flows {len(flows)} distinct signatures {unique_sigs} sections {len(mapping)} "
        f"walkthroughs {walks} charts used {len(charts_used)} art specs {len(arts)} "
        f"bytes {OUT.stat().st_size}"
    )


if __name__ == "__main__":
    main()
