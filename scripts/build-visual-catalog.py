#!/usr/bin/env python3
"""Build campus/assets/flow-catalog.js from authored call flows.

The campus page loads the generated file. It does not run this script.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "campus" / "uc-lab-free-university.html"
OUT = ROOT / "campus" / "assets" / "flow-catalog.js"

FLOWS: list[dict] = []


def add(fid, title, why, cite, actors, rows, *, layout="ladder", chart="none",
        icon="sip", keys=None, header=None, audio=False):
    steps = []
    for row in rows:
        f, t, label, kind, cap = row
        steps.append({"f": f, "t": t, "label": label, "kind": kind, "cap": cap})
    FLOWS.append({
        "id": fid,
        "title": title,
        "why": why,
        "cite": cite,
        "layout": layout,
        "actors": actors,
        "chart": chart,
        "icon": icon,
        "keys": keys or [
            ["LICC", "Leg, id, counter, capture"],
            ["One change", "Then compare the same id"],
            ["Call-ID", "Join the logs"],
            ["Current doc", "Re-check before production"],
        ],
        "header": header,
        "audio": audio,
        "steps": steps,
    })


def tree(fid, title, why, cite, rows, *, chart="none", icon="tree", keys=None, audio=False):
    add(fid, title, why, cite, ["Check"], [(0, 0, a, b, c) for a, b, c in rows],
        layout="tree", chart=chart, icon=icon, keys=keys, audio=audio)


K_SIP = [["5060", "SIP UDP and TCP"], ["5061", "SIP over TLS"], ["Call-ID", "Same dialog on a proxy"], ["CSeq", "Rises inside the dialog"]]
K_RTP = [["RTP", "Even UDP port, dynamic"], ["RTCP", "Usually RTP port + 1"], ["16384–32767", "Common Cisco range"], ["SDP c= / m=", "Where media is sent"]]
K_QOS = [["DSCP 46", "EF bearer"], ["DSCP 24", "CS3 signaling, Cisco path"], ["150 ms", "G.114 one-way planning"], ["< 1% loss", "Design target, then measure"]]
K_E911 = [["911", "Emergency pattern"], ["ELIN", "Callback number"], ["ERL", "Emergency response location"], ["Kari", "On-site notification"]]


def build() -> None:
    add("sip-basic", "Basic SIP dialog",
        "Every later hop is a guess until this ladder is right: offer, answer, ACK, media, BYE.",
        "RFC 3261 and RFC 3264",
        ["Alice UAC", "Bob UAS"],
        [
            (0, 1, "INVITE", "req", "Alice sends INVITE with a new Call-ID, a From tag, and an SDP offer. The branch id starts this transaction."),
            (1, 0, "100 Trying", "prov", "100 Trying is hop by hop. It only means the next hop is working on the INVITE. It does not mean Bob is ringing."),
            (1, 0, "180 Ringing", "prov", "180 Ringing is provisional. The dialog is not confirmed. A phone may start local ringback from this response."),
            (1, 0, "200 OK", "ok", "Bob accepts. The 200 carries the SDP answer and Bob's To tag. Offer and answer are now complete."),
            (0, 1, "ACK", "req", "Alice sends ACK. For a 2xx, that ACK is end to end: it is not retransmitted as its own transaction the way a non-2xx ACK is."),
            (0, 1, "RTP", "media", "Media follows the SDP addresses, not the SIP path. One-way audio is an RTP problem unless the 200 never completed."),
            (0, 1, "BYE", "bye", "Either party sends BYE inside the dialog. The Call-ID and tags stay the same."),
            (1, 0, "200 OK", "ok", "The BYE is answered with 200 OK. The dialog is over. A later packet with this Call-ID is a new problem, not this call."),
        ],
        chart="sip", icon="sip", keys=K_SIP, header="invite", audio=True)

    add("sip-proxy", "INVITE through a proxy",
        "A proxy is in the signaling path only. 100 Trying stops retransmissions; it is not forwarded as a sign that the far end is ringing.",
        "RFC 3261 sections 16 and 17",
        ["Alice", "Proxy", "Bob"],
        [
            (0, 1, "INVITE", "req", "Alice sends INVITE to the outbound proxy. Via and the branch identify this hop."),
            (1, 0, "100 Trying", "prov", "The proxy sends 100 Trying to Alice. That response is hop by hop and is not relayed from Bob."),
            (1, 2, "INVITE", "req", "The proxy forwards the INVITE. A pure proxy keeps the Call-ID. It adds its own Via."),
            (2, 1, "180 Ringing", "prov", "Bob sends 180. The proxy will forward this provisional response back along the Via stack."),
            (1, 0, "180 Ringing", "prov", "Alice receives 180. Local ringback may start. Early media has not been negotiated unless SDP already arrived."),
            (2, 1, "200 OK", "ok", "Bob sends 200 OK with the answer SDP and a To tag. The dialog exists."),
            (1, 0, "200 OK", "ok", "The proxy forwards the 200. It does not generate the ACK for a 2xx."),
            (0, 1, "ACK", "req", "Alice generates the ACK. If the proxy inserted Record-Route, the route set sends this ACK via the proxy."),
            (1, 2, "ACK", "req", "The proxy forwards the ACK. The CSeq number matches the INVITE. The method is ACK."),
            (0, 2, "RTP", "media", "RTP does not have to hairpin through the proxy. If it does, something else is anchoring media."),
        ],
        chart="sip", icon="sip", keys=K_SIP, audio=True)

    add("sip-183", "Early media with 183",
        "183 Session Progress can carry the SDP answer before the call is answered. That is how in-band announcements and network ringback are played. Silence here is an early-media fault, not a missing 180.",
        "RFC 3261 and RFC 3960",
        ["Alice", "Bob"],
        [
            (0, 1, "INVITE", "req", "The INVITE carries the offer. Early media needs an answer before 200 OK."),
            (1, 0, "100 Trying", "prov", "100 Trying still means only that the request is being handled."),
            (1, 0, "183 + SDP", "prov", "183 Session Progress carries the answer SDP. Early RTP may start now. A 180 without SDP does not do this."),
            (1, 0, "early RTP", "media", "One-way media before answer: ringback, an intercept message, or a carrier tone. Two-way speech is not established yet."),
            (1, 0, "200 OK", "ok", "Answer. If the 183 already completed offer/answer, the 200 often repeats that SDP rather than opening a new negotiation."),
            (0, 1, "ACK", "req", "ACK confirms the dialog. Media continues on the negotiated ports."),
        ],
        chart="sip", icon="media", keys=K_RTP, header="sdp", audio=True)

    add("sip-prack", "Reliable provisional response (PRACK)",
        "If the far end requires 100rel, a 183 that carries SDP is not final until PRACK. Lost early media is often a missing PRACK, not a codec bug.",
        "RFC 3262",
        ["Alice", "Bob"],
        [
            (0, 1, "INVITE", "req", "Alice offers 100rel in Supported, or the network Requires it."),
            (1, 0, "183 RSeq", "prov", "The 183 includes Require: 100rel and an RSeq number. The UAS will retransmit this 183 until PRACK arrives."),
            (0, 1, "PRACK", "req", "PRACK names that RSeq in RAck. This is its own transaction."),
            (1, 0, "200 PRACK", "ok", "200 OK answers the PRACK, not the INVITE. The INVITE is still outstanding."),
            (1, 0, "200 INVITE", "ok", "Now the UAS accepts the INVITE."),
            (0, 1, "ACK", "req", "ACK completes the INVITE dialog. Do not confuse it with the PRACK."),
        ],
        chart="sip", icon="sip", keys=K_SIP, audio=True)

    add("sip-hold", "Hold and resume with re-INVITE",
        "Hold is a change to the existing dialog, not a second call. RFC 3264 uses a=sendonly and a=recvonly. a=inactive means neither side sends.",
        "RFC 3264",
        ["Holder", "Held party"],
        [
            (0, 1, "re-INVITE", "req", "Same Call-ID, new CSeq, SDP with a=sendonly. This is the holder offering to stop sending media."),
            (1, 0, "200 OK", "ok", "The held party answers with a=recvonly. If it answers sendrecv, the hold did not take."),
            (0, 1, "ACK", "req", "ACK locks the held session."),
            (0, 1, "one-way RTP", "media", "Media, if any, flows toward the holder. Music on hold is a separate source the holder may play."),
            (0, 1, "re-INVITE", "req", "Resume is another re-INVITE with a=sendrecv."),
            (1, 0, "200 OK", "ok", "The answer returns to sendrecv."),
            (0, 1, "ACK", "req", "ACK completes resume. A failed resume leaves the dialog up and the media on hold."),
        ],
        chart="codec", icon="media", keys=[["a=sendonly", "Holder"], ["a=recvonly", "Held party"], ["re-INVITE", "Same Call-ID"], ["CSeq + 1", "New transaction"]],
        header="hold", audio=True)

    add("sip-refer", "Blind transfer with REFER",
        "REFER asks the other user agent to start a new request. 202 means the REFER was accepted, not that the transfer target answered.",
        "RFC 3515",
        ["Alice", "Bob", "Carol"],
        [
            (0, 1, "REFER", "req", "Alice sends REFER to Bob with Refer-To set to Carol. This rides the existing dialog."),
            (1, 0, "202 Accepted", "ok", "202 accepts the REFER request. Carol has not been contacted yet."),
            (1, 0, "NOTIFY 100", "prov", "Bob opens the subscription and sends NOTIFY with a sipfrag, often SIP/2.0 100 Trying."),
            (1, 2, "INVITE", "req", "Bob places a new INVITE to Carol. That dialog has its own Call-ID."),
            (2, 1, "200 OK", "ok", "Carol answers Bob."),
            (1, 2, "ACK", "req", "Bob completes the new dialog."),
            (1, 0, "NOTIFY 200", "ok", "NOTIFY tells Alice the referred request got a 200. This is the success signal."),
            (0, 1, "BYE", "bye", "Alice drops the original dialog. Bob and Carol stay up on the new one."),
        ],
        chart="sip", icon="sip", keys=[["202", "REFER accepted"], ["NOTIFY", "sipfrag result"], ["Refer-To", "The target"], ["New Call-ID", "Bob to Carol"]])

    add("sip-attended", "Attended transfer with Replaces",
        "Attended transfer uses a consultation call first. Replaces names that dialog so Carol's phone swaps the consult for the original party.",
        "RFC 3515 and RFC 3891",
        ["Alice", "Bob", "Carol"],
        [
            (0, 2, "INVITE", "req", "Alice consults Carol on a second dialog and waits until Carol answers."),
            (2, 0, "200 OK", "ok", "The consultation is up. Alice now has two dialogs."),
            (0, 1, "REFER", "req", "Alice sends REFER to Bob. Refer-To includes a Replaces parameter for the Alice–Carol dialog."),
            (1, 0, "202 Accepted", "ok", "Bob accepts the request to replace."),
            (1, 2, "INVITE", "req", "Bob invites Carol with Replaces. Carol matches the existing dialog."),
            (2, 1, "200 OK", "ok", "Carol accepts Bob and drops the consultation with Alice."),
            (1, 0, "NOTIFY 200", "ok", "Alice sees the referred call succeed, then BYE on both of her dialogs."),
        ],
        icon="sip", keys=[["Replaces", "Target dialog"], ["Consult", "Second Call-ID"], ["202", "Not the answer"], ["NOTIFY", "Final status"]])

    add("sip-cancel", "CANCEL before answer",
        "CANCEL stops a ringing INVITE. It uses the same branch as that INVITE. The INVITE itself ends with 487, and that 487 still needs an ACK.",
        "RFC 3261 section 9",
        ["Alice", "Bob"],
        [
            (0, 1, "INVITE", "req", "The INVITE is outstanding. CANCEL is legal only before a final response."),
            (1, 0, "180 Ringing", "prov", "Bob is alerting. No dialog is confirmed yet."),
            (0, 1, "CANCEL", "bye", "CANCEL carries the same branch as the INVITE. It is its own request."),
            (1, 0, "200 CANCEL", "ok", "200 answers the CANCEL. The INVITE is not finished by this 200."),
            (1, 0, "487", "err", "487 Request Terminated answers the INVITE."),
            (0, 1, "ACK", "req", "ACK for a non-2xx is hop by hop and belongs to that INVITE transaction. Skipping it leaves retransmissions running."),
        ],
        chart="sip", icon="sip", keys=K_SIP)

    add("sip-407", "Proxy authentication",
        "407 is the proxy challenging the request. 401 is the UAS. The ACK for that non-2xx, then a new INVITE with the authorization header, is the whole story.",
        "RFC 3261 sections 22 and 17",
        ["Alice", "Proxy"],
        [
            (0, 1, "INVITE", "req", "First INVITE has no credentials."),
            (1, 0, "407", "err", "407 Proxy Authentication Required carries Proxy-Authenticate. A 401 would carry WWW-Authenticate instead."),
            (0, 1, "ACK", "req", "ACK the 407. It is a non-2xx final response."),
            (0, 1, "INVITE", "req", "A new INVITE, new branch, CSeq incremented, with Proxy-Authorization."),
            (1, 0, "180 Ringing", "prov", "The challenge succeeded. The call proceeds."),
        ],
        chart="sip", icon="cert", keys=[["407", "Proxy challenge"], ["401", "UAS challenge"], ["New branch", "New INVITE"], ["CSeq + 1", "Not a retransmission"]])

    add("sip-options", "OPTIONS keepalive",
        "OPTIONS asks whether the far end can take a call. A trunk that answers OPTIONS and drops INVITE is a policy failure, not a routing failure.",
        "RFC 3261 section 11",
        ["SBC", "Peer"],
        [
            (0, 1, "OPTIONS", "req", "The SBC sends OPTIONS on an interval. No dialog is created."),
            (1, 0, "200 OK", "ok", "200 means the peer is willing to receive requests. It says nothing about media ACLs."),
            (0, 1, "INVITE", "req", "A real call is a separate transaction. Do not treat a green OPTIONS counter as proof of audio."),
        ],
        icon="sip", keys=[["OPTIONS", "Out of dialog"], ["200", "Reachable"], ["INVITE", "Still separate"], ["ACL", "Can still drop RTP"]], audio=True)

    add("sip-delayed", "Delayed offer",
        "Delayed offer puts no SDP in the INVITE. The offer arrives in the 200, and the answer comes back in the ACK. Early offer is the opposite.",
        "RFC 3261 and RFC 3264",
        ["UAC", "UAS"],
        [
            (0, 1, "INVITE", "req", "No SDP body. The UAC has not offered a codec yet."),
            (1, 0, "180 Ringing", "prov", "Alerting can still happen. There is no media to play until offer/answer completes."),
            (1, 0, "200 + SDP", "ok", "The UAS offers SDP in the 200 OK."),
            (0, 1, "ACK + SDP", "req", "The UAC answers in the ACK. If this ACK is lost, the UAS has no answer and media does not start."),
            (0, 1, "RTP", "media", "RTP starts only after that answer. A capture that shows 200 OK and no ACK is this fault."),
        ],
        chart="codec", icon="media", keys=[["No SDP", "Delayed offer"], ["Offer in 200", "UAS offers"], ["Answer in ACK", "UAC answers"], ["Early offer", "SDP already in INVITE"]], audio=True)

    add("sip-dtmf", "RFC 2833 telephone events",
        "Named events in RTP are the usual DTMF path. SIP INFO and KPML are different tools. An IVR that is deaf after G.729 often never received events, because the transcoder or the SBC dropped them.",
        "RFC 4733 (updates RFC 2833)",
        ["Phone", "IVR"],
        [
            (0, 1, "INVITE", "req", "The offer includes telephone-event, often payload 101, for the codec that will carry the audio."),
            (1, 0, "200 OK", "ok", "The answer agrees to telephone-event. If it does not, digits will not arrive as events."),
            (0, 1, "RTP audio", "media", "Speech uses the voice payload."),
            (0, 1, "RTP event", "media", "The digit is a named telephony event in the same RTP stream, with a marker and an end bit. It is not a tone in the audio unless the SBC converts it."),
        ],
        chart="codec", icon="media", keys=[["PT 101", "Common telephone-event"], ["End bit", "Digit finished"], ["INFO", "A different method"], ["KPML", "SUBSCRIBE for digits"]], audio=True)

    add("sip-486", "Busy and 486",
        "486 Busy Here is a final response from the UAS. The UAC ACKs it and does not send BYE, because no dialog was confirmed.",
        "RFC 3261",
        ["Alice", "Bob"],
        [
            (0, 1, "INVITE", "req", "Alice calls Bob."),
            (1, 0, "486 Busy", "err", "Bob's UAS is busy. This is final. It is not 180 and it is not CANCEL."),
            (0, 1, "ACK", "req", "ACK the 486. Stop. There is no BYE."),
        ],
        chart="sip", icon="phone", keys=[["486", "Busy Here"], ["600", "Busy Everywhere"], ["480", "Temporarily unavailable"], ["ACK", "Required for non-2xx"]], audio=True)

    add("sip-503", "503 and retry storms",
        "503 means this server cannot take the request now. Retry-After, if present, is the timer. A client that immediately retries every 503 will melt the peer.",
        "RFC 3261",
        ["UAC", "Server"],
        [
            (0, 1, "INVITE", "req", "A call arrives while the server is overloaded or in maintenance."),
            (1, 0, "503", "err", "503 Service Unavailable. Read Retry-After before you try again."),
            (0, 1, "ACK", "req", "ACK the 503."),
            (0, 1, "INVITE", "err", "An immediate new INVITE is how a 503 becomes a retry storm. Back off, or fail over to the next peer in the route."),
        ],
        chart="sip", icon="sip", keys=[["503", "This server, now"], ["Retry-After", "Wait"], ["500", "Server internal error"], ["Failover", "Next peer, not a tight loop"]])

    add("stir-shaken", "STIR/SHAKEN Identity",
        "The Identity header signs the calling number. If an SBC strips PAI or From and does not rebuild the identity, verification fails downstream and the call looks spoofed.",
        "RFC 8224",
        ["Originating SP", "Transit", "Terminating SP"],
        [
            (0, 1, "INVITE + Identity", "req", "The originating provider adds an Identity header over the attested calling number and a date."),
            (1, 2, "INVITE", "req", "Transit must pass the Identity header and the signed calling information. A SIP profile that deletes PAI can break the attestation."),
            (2, 1, "verify", "note", "The terminating provider checks the signature against the provider certificate. A fail is a signing or header-stripping problem, not a dial-plan problem."),
            (2, 1, "180 / 200", "ok", "The call can still complete while verification fails. The symptom is often a label or a dropped call only where policy requires a pass."),
        ],
        icon="cert", keys=[["Identity", "Signed token"], ["PAI", "Do not strip blindly"], ["Attestation", "A, B, or C"], ["Date", "Clock skew fails verification"]])

    add("sip-tls", "SIP over TLS",
        "TLS protects signaling, not RTP. SRTP is a separate negotiation. A trunk can be TLS-up and still play unencrypted audio, or fail SRTP and go silent.",
        "RFC 3261 and RFC 3711",
        ["Client", "Server"],
        [
            (0, 1, "TCP 5061", "req", "The client opens TLS. 5061 is the registered SIP TLS port. Webex Calling and Teams use their own documented ports on top of this idea."),
            (0, 1, "Certificate", "note", "Each side checks the name in the certificate against the name it dialed. An incomplete chain fails before any INVITE."),
            (0, 1, "INVITE", "req", "The INVITE rides inside TLS. A capture on the wire shows records, not cleartext SIP, unless you have the keys."),
            (0, 1, "SRTP", "media", "Media encryption is negotiated in SDP (RTP/SAVP or a UDP/TLS/RTP/SAVPF profile). It is not implied by SIP TLS."),
        ],
        chart="sip", icon="cert", keys=[["5061", "SIP TLS"], ["mTLS", "Both certificates"], ["SRTP", "Separate from TLS"], ["Chain", "Intermediate must be sent"]], audio=True)

    add("codec-neg", "Offer and answer codec choice",
        "The answerer picks one payload from the offer for each stream it accepts. Sending a codec the answer did not list is how you get silence with a perfect 200 OK.",
        "RFC 3264",
        ["Offerer", "Answerer"],
        [
            (0, 1, "offer", "req", "The offer lists payloads in preference order, with rtpmap and fmtp."),
            (1, 0, "answer", "ok", "The answer keeps one payload for the stream, or rejects the stream with port 0."),
            (0, 1, "RTP", "media", "Both sides send the answered payload. A ptime mismatch is legal within limits; a payload mismatch is not."),
        ],
        chart="codec", icon="media", keys=[["m= audio", "Port and payloads"], ["port 0", "Stream rejected"], ["rtpmap", "Name the payload"], ["fmtp", "Required parameters"]], audio=True)

    add("rtp-plane", "RTP and RTCP beside SIP",
        "Signaling can be perfect while RTP is blackholed. RTP is its own UDP flow. RTCP on the next port tells you whether the other side is receiving.",
        "RFC 3550",
        ["Sender", "Receiver"],
        [
            (0, 1, "SDP", "req", "c= is the address. m= is the port and payload. That pair is the media target."),
            (0, 1, "RTP", "media", "Even UDP port is the usual RTP port. Sequence numbers and timestamps move only when packets are sent."),
            (1, 0, "RTCP", "media", "RTCP receiver reports show loss and jitter as the receiver saw them. No RTCP often means the return path is filtered."),
            (0, 1, "BYE", "bye", "SIP BYE does not itself stop a stream that a device failed to close. Check the counters after the BYE."),
        ],
        chart="mos", icon="media", keys=K_RTP, header="sdp", audio=True)

    add("srtp-sdes", "SRTP with SDES",
        "SRTP without a matching crypto suite is silence, not garbled audio. Both sides must agree the profile and the key in SDP.",
        "RFC 3711 and RFC 4568",
        ["Alice", "Bob"],
        [
            (0, 1, "RTP/SAVP", "req", "The offer uses a secure profile and lists a=crypto with a suite and a key."),
            (1, 0, "answer", "ok", "The answer selects one suite. If the suites do not overlap, the call may signal and then carry no decodeable media."),
            (0, 1, "SRTP", "media", "The UDP payload is encrypted. A capture still shows packets. A phone shows them as received and drops them if the key is wrong."),
        ],
        chart="mos", icon="cert", keys=[["RTP/SAVP", "Secure AVP"], ["a=crypto", "SDES key"], ["Suite", "Must overlap"], ["TLS", "Does not encrypt RTP"]], audio=True)

    add("nat-media", "NAT and the media latch",
        "The address in SDP is useless if it is a private address the far end cannot route. Symmetric latching or ICE has to learn the public mapped port.",
        "RFC 6314 behavior, SDP c=",
        ["Phone", "NAT", "SBC"],
        [
            (0, 1, "INVITE", "req", "SDP c= may say a private address. That address is not on the public side of the NAT."),
            (1, 2, "INVITE", "req", "If nothing rewrites c=, the SBC sends RTP to a private address and the packets die."),
            (2, 1, "RTP", "media", "The SBC can latch onto the source address of RTP that actually arrives, when latching is enabled."),
            (0, 2, "RTP", "media", "After the latch, media flows to the mapped port. A SIP ALG that rewrites SDP badly fights the SBC and should be off."),
        ],
        chart="codec", icon="route", keys=[["c=", "Declared address"], ["Latch", "Learned address"], ["SIP ALG", "Turn it off"], ["ICE", "Better when both sides support it"]], audio=True)

    add("ice", "ICE, STUN, and TURN",
        "ICE gathers candidates, checks them in pairs, and nominates one pair. TURN is a relay for the pairs that cannot punch through. It is not the first choice.",
        "RFC 8445, RFC 8489, RFC 8656",
        ["Agent", "STUN/TURN", "Peer"],
        [
            (0, 1, "gather", "note", "The browser gathers host candidates and asks STUN for a server-reflexive address. TURN allocates a relay if configured."),
            (0, 2, "checks", "media", "Connectivity checks run on candidate pairs. The nominated pair is the one media will use."),
            (0, 1, "TURN relay", "media", "If no direct pair works, media hairpins through TURN. Capacity on that relay is a real limit for home agents."),
            (0, 2, "SRTP", "media", "The selected pair is one address family. An IPv4-only candidate does not carry an IPv6 stream."),
        ],
        icon="media", keys=[["Host", "Local address"], ["srflx", "STUN mapped"], ["relay", "TURN"], ["Nominated", "The pair in use"]], audio=True)

    add("webrtc", "WebRTC agent desktop",
        "A browser agent does not send RTP the way a desk phone does. Media is DTLS-SRTP, negotiated with ICE, often via a gateway into SIP.",
        "RFC 8825 family, WebRTC",
        ["Browser", "Gateway", "SIP agent"],
        [
            (0, 1, "SDP offer", "req", "The browser offers ICE candidates and DTLS-SRTP fingerprints."),
            (1, 0, "answer", "ok", "The gateway answers and anchors or translates the media toward the SIP side."),
            (1, 2, "SIP INVITE", "req", "The SIP leg is a normal INVITE. Its Call-ID will not equal the browser peer connection id. You need the gateway's correlation."),
            (0, 1, "DTLS-SRTP", "media", "If ICE fails, the SIP leg can still look answered while the browser sends nothing."),
        ],
        chart="mos", icon="media", keys=[["DTLS-SRTP", "Browser media"], ["ICE", "Path selection"], ["Gateway", "Correlation point"], ["SIP Call-ID", "Other leg"]], audio=True)

    add("cube-b2bua", "CUBE as a B2BUA",
        "CUBE terminates one SIP dialog and starts another. Call-IDs differ per leg. In flow-through mode, RTP anchors on CUBE so it can do SRTP, transcoding, and recording.",
        "Cisco IOS XE CUBE configuration guide",
        ["CUCM", "CUBE", "ITSP"],
        [
            (0, 1, "INVITE leg A", "req", "CUCM sends INVITE to the dial-peer that targets CUBE. This Call-ID belongs to leg A."),
            (1, 0, "100 Trying", "prov", "CUBE answers 100 on leg A while it hunts an outbound dial-peer."),
            (1, 2, "INVITE leg B", "req", "CUBE sends a new INVITE to the ITSP. New Call-ID, new From tag. Early offer or delayed offer follows the dial-peer."),
            (2, 1, "180 / 183", "prov", "The ITSP alerts or sends early media. CUBE translates that into a response on leg A."),
            (1, 0, "180 / 183", "prov", "CUCM sees the translated response. Ringback is either local or the early RTP CUBE is anchoring."),
            (2, 1, "200 OK", "ok", "The ITSP answers leg B."),
            (1, 0, "200 OK", "ok", "CUBE answers leg A. Two dialogs are up."),
            (0, 1, "ACK", "req", "ACK is consumed on leg A and generated on leg B. It is not one end-to-end ACK."),
            (1, 2, "ACK", "req", "Leg B is confirmed."),
            (0, 2, "RTP via CUBE", "media", "With media flow-through, packets are Phone to CUBE to ITSP. CUCM is not in the audio path unless an MTP was inserted."),
            (0, 1, "BYE", "bye", "BYE on one leg is translated. CUBE clears the other leg."),
        ],
        chart="codec", icon="cube", keys=[["Two Call-IDs", "B2BUA"], ["Dial-peer", "Both legs"], ["Flow-through", "RTP on CUBE"], ["MTP", "Only if required"]], audio=True)

    add("cube-delayed", "CUBE delayed offer to the provider",
        "Some providers require a delayed offer. CUBE can receive an early offer from CUCM and send a delayed offer onward. The ACK toward the provider then carries the answer.",
        "RFC 3264 and CUBE SIP profiles",
        ["CUCM", "CUBE", "ITSP"],
        [
            (0, 1, "INVITE + SDP", "req", "CUCM early-offers to CUBE."),
            (1, 2, "INVITE", "req", "CUBE sends the ITSP an INVITE with no SDP because that dial-peer is delayed offer."),
            (2, 1, "200 + SDP", "ok", "The provider offers in the 200."),
            (1, 2, "ACK + SDP", "req", "CUBE answers in the ACK on leg B."),
            (1, 0, "200 OK", "ok", "Leg A is answered with an SDP that matches what CUBE can actually send."),
        ],
        chart="codec", icon="cube", keys=[["Early offer", "SDP in INVITE"], ["Delayed offer", "SDP in 200"], ["Answer", "In the ACK"], ["Profile", "Do not strip the body you need"]])

    add("cube-failover", "Outbound dial-peer failover",
        "A preference list only helps if the failure is a response CUBE is willing to hunt on. A 200 OK to a black hole will not hunt.",
        "Cisco CUBE dial-peer configuration",
        ["CUCM", "CUBE", "Peer A", "Peer B"],
        [
            (0, 1, "INVITE", "req", "The inbound dial-peer matches."),
            (1, 2, "INVITE", "req", "Outbound dial-peer A is tried first."),
            (2, 1, "503", "err", "Peer A refuses. CUBE ACKs the 503 and may hunt if hunting is enabled for that cause."),
            (1, 3, "INVITE", "req", "Dial-peer B is next. The caller still has one dialog with CUBE."),
            (3, 1, "200 OK", "ok", "Peer B answers. Hunting stops."),
        ],
        icon="cube", keys=[["Preference", "Hunt order"], ["503", "Often hunts"], ["200 + silence", "Does not hunt"], ["OPTIONS", "Can busy-out a peer"]])

    add("cube-ha", "CUBE box-to-box failover",
        "Active/standby CUBE shares a virtual address. Calls that were checkpointed can survive a switchover. Calls that were not checkpointed drop.",
        "Cisco CUBE high availability",
        ["CUCM", "Active", "Standby"],
        [
            (0, 1, "INVITE", "req", "Signaling is aimed at the virtual IP, not at a box-specific address."),
            (1, 2, "checkpoint", "note", "The active box checkpoints the dialog to the standby when that feature is on."),
            (1, 2, "failover", "err", "The standby takes the virtual IP. A call without a checkpoint is cleared."),
            (0, 2, "RTP", "media", "Media resumes only for checkpointed calls, and only if both boxes were ready to anchor it."),
        ],
        icon="cube", keys=[["VIP", "One address"], ["Checkpoint", "Mid-call state"], ["RG", "Redundancy group"], ["Split brain", "Two actives, one disaster"]])

    add("sbc-topo", "SBC topology choices",
        "The SBC is the policy point: topology hiding, media anchoring, and the only place you should rewrite SDP. A second rewrite by a firewall ALG undoes it.",
        "SBC design practice",
        ["Inside", "SBC", "Outside"],
        [
            (0, 1, "INVITE", "req", "Inside addresses and headers are still the enterprise view."),
            (1, 2, "INVITE", "req", "The SBC hides topology: new Call-ID, stripped internal headers, public c= line."),
            (0, 1, "RTP", "media", "Flow-through anchors media. Flow-around lets RTP bypass the SBC and then the SBC cannot record or transcode it."),
            (2, 1, "RTCP", "media", "If you need end-to-end RTCP XR, topology hiding and media anchoring change what the probes can see."),
        ],
        icon="cube", keys=[["Flow-through", "Anchor media"], ["Flow-around", "Bypass media"], ["ALG", "Leave it off"], ["Public c=", "The outside address"]])

    add("cucm-route", "CUCM route pattern",
        "Digit analysis searches the line CSS first, then the device CSS. The first match wins. A pattern that is too wide steals calls from a more specific one that appears later.",
        "Cisco Unified CM dial-plan guide",
        ["Phone", "Line CSS", "Device CSS", "Route list", "Trunk"],
        [
            (0, 1, "digits", "note", "The phone sends the dialed digits in the INVITE Request-URI."),
            (1, 2, "CSS order", "note", "CUCM concatenates the line CSS and then the device CSS. Partitions are searched in that order."),
            (2, 3, "pattern", "note", "The first matching translation or route pattern wins, including its urgent priority."),
            (3, 4, "route group", "note", "A route list tries route groups in order. The group picks a trunk or gateway member."),
            (4, 4, "INVITE", "req", "CUCM sends the INVITE with calling and called transformations from the pattern and the route group."),
        ],
        layout="ladder", chart="none", icon="route",
        keys=[["Line CSS", "Searched first"], ["Device CSS", "Searched second"], ["Partition", "Where the pattern lives"], ["Route list", "Hunt the trunks"]])

    add("cucm-onnet", "CUCM on-net call",
        "Two phones on the same cluster signal through CUCM and send RTP to each other. CUCM is not in the audio path unless an MTP, transcoder, or TRP is invoked.",
        "Cisco Unified CM",
        ["Phone A", "CUCM", "Phone B"],
        [
            (0, 1, "INVITE", "req", "Phone A is registered. The INVITE hits CUCM."),
            (1, 1, "DA", "note", "Digit analysis finds Phone B's directory number in a partition Phone A's CSS can see."),
            (1, 2, "INVITE", "req", "CUCM calls Phone B. This is a new leg."),
            (2, 1, "180", "prov", "Phone B rings."),
            (2, 1, "200", "ok", "Phone B answers."),
            (1, 0, "200", "ok", "CUCM answers Phone A."),
            (0, 2, "RTP", "media", "RTP goes phone to phone. If you see CUCM's address in SDP, an MTP was inserted."),
        ],
        chart="codec", icon="phone", keys=[["DN", "Directory number"], ["Partition", "Visibility"], ["MTP", "CUCM in media"], ["RTP", "Phone to phone"]], audio=True)

    add("cucm-reg", "Phone registration",
        "A phone that cannot register cannot place a reliable call. The path is PoE and VLAN, DHCP options, then TFTP or HTTPS config, then SIP or SCCP registration.",
        "Cisco endpoint and CUCM docs",
        ["Phone", "DHCP", "TFTP", "CUCM"],
        [
            (0, 1, "DHCP", "note", "The phone needs an address and option 150 or 66 for the TFTP server, unless it was staged with a name."),
            (1, 2, "TFTP 6970", "note", "CUCM serves phone files on UDP 69 and HTTP 6970. The file names the CUCM nodes."),
            (2, 3, "REGISTER", "req", "A SIP phone sends REGISTER. An SCCP phone uses TCP 2000. TLS uses the secure ports configured on the cluster."),
            (3, 0, "200 OK", "ok", "The phone is registered. Until this 200, a dialed call is a local failure, not a dial-plan failure."),
        ],
        icon="phone", keys=[["DHCP 150", "TFTP list"], ["6970", "CUCM HTTP files"], ["5060", "SIP register"], ["2000", "SCCP"]])

    add("cucm-srst", "SRST fallback",
        "When the phone loses CUCM, SRST on the gateway keeps a subset of dialing alive. When CUCM returns, phones must re-home. A phone stuck in SRST is a WAN-recovery fault.",
        "Cisco SRST",
        ["Phone", "WAN", "SRST", "CUCM"],
        [
            (0, 3, "keepalive", "note", "The phone watches CUCM. Missed keepalives start the fallback timer."),
            (0, 2, "fallback", "err", "The phone registers to the local SRST router. Only the configured dial peers and a limited feature set exist."),
            (3, 0, "CUCM returns", "ok", "When the WAN path to CUCM works again, the phone re-registers to the cluster and leaves SRST."),
        ],
        icon="phone", keys=[["Keepalive", "Loss starts the timer"], ["SRST", "Local dial tone"], ["Re-home", "Back to CUCM"], ["Feature loss", "Expected while fallen back"]])

    add("cucm-em", "Extension Mobility",
        "Extension Mobility swaps the device profile onto the phone. The line CSS can change at login. A failure after login is often the user profile, not the phone's device CSS.",
        "Cisco Extension Mobility",
        ["User", "Phone", "CUCM"],
        [
            (0, 1, "login", "note", "The user signs in on the phone or through the service."),
            (1, 2, "profile", "note", "CUCM applies the device profile: lines, CSS, and softkeys."),
            (2, 1, "reset line", "ok", "The line registers with the profile's directory number. Calls now use that line CSS first."),
            (0, 1, "logout", "note", "Logout restores the logout profile. A phone left logged in keeps the previous user's class of service."),
        ],
        icon="phone", keys=[["Device profile", "What login applies"], ["Line CSS", "Searched first"], ["Logout profile", "The empty phone"], ["EMCC", "Cross-cluster is a separate design"]])

    add("cucm-hunt", "Hunt group",
        "A hunt pilot has its own CSS, then a line group. A loop happens when a member forwards back to the pilot. RNA must land somewhere that does not return.",
        "Cisco Unified CM hunt lists",
        ["Caller", "Hunt pilot", "Line group", "Member"],
        [
            (0, 1, "INVITE", "req", "The pilot number matches."),
            (1, 2, "algorithm", "note", "The line group rings the next member by broadcast, longest idle, or circular order."),
            (2, 3, "ring", "prov", "The member rings. RNA advances only if the hunt is allowed to try the next member."),
            (3, 1, "RNA", "err", "If the member's forward-no-answer target is the pilot, the hunt loops. Point RNA at a final destination."),
        ],
        icon="queue", keys=[["Pilot", "The number"], ["Line group", "The members"], ["RNA", "Must exit"], ["Hunt CSS", "Not the caller's CSS"]])

    add("cucm-moh", "Music on hold",
        "Hold is a re-INVITE. The MOH audio is a stream from the MOH server, selected by the holder's source. Silence on hold means that stream is not reaching the held party.",
        "Cisco MOH",
        ["Holder", "CUCM", "MOH", "Held"],
        [
            (0, 1, "re-INVITE", "req", "The holder sends a hold re-INVITE."),
            (1, 2, "select", "note", "CUCM picks the MOH source from the user's audio source or the default."),
            (2, 3, "RTP", "media", "MOH RTP is sent to the held party's address. Multicast MOH requires the network to carry that group. Unicast MOH is a normal stream."),
            (0, 1, "resume", "ok", "A second re-INVITE restores sendrecv and stops the MOH stream."),
        ],
        chart="codec", icon="media", keys=[["User source", "Which audio"], ["Multicast", "Network must carry it"], ["Unicast", "One stream"], ["Hold re-INVITE", "The trigger"]], audio=True)

    add("cucm-conf", "Conference bridge",
        "An ad-hoc conference allocates a bridge resource. When the bridge is full, the conference fails even though both calls were fine alone.",
        "Cisco conferencing",
        ["Host", "CUCM", "Bridge", "Parties"],
        [
            (0, 1, "Conf", "note", "The host presses conference. CUCM needs a media resource from the host's MRGL."),
            (1, 2, "allocate", "note", "A software or hardware bridge port is reserved. Exhaustion returns a failure, not a new dial tone."),
            (2, 3, "RTP", "media", "Each party sends RTP to the bridge, not to each other. The bridge mixes."),
            (0, 1, "drop", "bye", "When the host drops, the remaining parties follow the conference drop policy."),
        ],
        chart="erlang", icon="media", keys=[["MRGL", "Which resources"], ["Bridge port", "One per party"], ["Mixer", "RTP to the bridge"], ["Exhausted", "A capacity fault"]])

    add("cucm-mtp", "When an MTP is inserted",
        "An MTP anchors media on CUCM. It is required for some DTMF and protocol mismatches. It is also a capacity limit and a single place for one-way audio.",
        "Cisco media resources",
        ["Phone", "MTP", "Trunk"],
        [
            (0, 1, "INVITE", "req", "CUCM decides an MTP is required, often for DTMF or early offer conversion."),
            (1, 2, "INVITE", "req", "The trunk side sees the MTP address in SDP, not the phone."),
            (0, 1, "RTP", "media", "Phone sends RTP to the MTP."),
            (1, 2, "RTP", "media", "The MTP sends RTP to the trunk. If the MTP is out of sessions, the call fails or proceeds without the feature you needed."),
        ],
        chart="codec", icon="media", keys=[["MRGL", "Where the MTP lives"], ["SDP c=", "MTP address"], ["DTMF", "A common reason"], ["Sessions", "A hard cap"]])

    add("unity-mwi", "Unity Connection and MWI",
        "Forward to voicemail is a call forward, then a SIP or SCCP integration. The message-waiting lamp is a separate notify. A caller who reached voicemail did not prove that MWI works.",
        "Cisco Unity Connection",
        ["CUCM", "Unity", "Phone"],
        [
            (0, 1, "forward", "req", "CUCM forwards the unanswered call to the voicemail pilot."),
            (1, 1, "greeting", "media", "Unity plays the greeting and takes the message. The redirecting number selects the mailbox."),
            (1, 0, "MWI", "note", "Unity tells CUCM to light the lamp. CUCM notifies the phone. A failure here leaves a message and a dark lamp."),
            (2, 1, "retrieve", "req", "The user dials the pilot. The calling number selects the mailbox."),
        ],
        icon="phone", keys=[["Pilot", "Voicemail number"], ["Redirecting", "Which mailbox"], ["MWI", "Separate signal"], ["Pilot CSS", "Must reach Unity"]])

    add("cucm-cli", "CUCM command line checks",
        "The appliance shell is how you prove NTP, replication, certificates, and disk without guessing from the GUI. These commands read state. They are not a Linux course.",
        "Cisco Unified OS administration",
        ["Admin", "Publisher"],
        [
            (0, 1, "utils ntp status", "note", "Clock skew breaks certificates and CDRs. Look for a synchronized source."),
            (0, 1, "utils dbreplication runtimestate", "note", "A pattern that exists on the publisher and not on a subscriber is often replication, not CSS."),
            (0, 1, "show status", "note", "Disk, CPU, and load. A full logging partition stops CDR and can destabilize the node."),
            (0, 1, "show cert list", "note", "Confirm the certificate you think the phone trusts is the one installed, and note the expiry."),
        ],
        layout="ladder", icon="cert",
        keys=[["NTP", "First"], ["Replication", "Second"], ["Disk", "Logging partition"], ["Cert", "Expiry and trust"]])

    add("cucm-failover", "CUCM node failover",
        "Phones keep a list of CUCM nodes. When the primary stops answering, they register to the next. Active calls may survive. New calls wait for the re-register.",
        "Cisco Unified CM groups",
        ["Phone", "Subscriber A", "Subscriber B"],
        [
            (0, 1, "REGISTER", "req", "The phone is on subscriber A, the first server in its Unified CM group."),
            (1, 0, "silence", "err", "A stops responding. The phone waits through its fallback timer."),
            (0, 2, "REGISTER", "req", "The phone registers to subscriber B."),
            (0, 2, "INVITE", "req", "New calls use B. A call that was already up can continue phone to phone until a feature needs CUCM."),
        ],
        icon="phone", keys=[["CM group", "Ordered list"], ["Fallback", "Timer, not instant"], ["Active RTP", "May continue"], ["Re-home", "When A returns"]])

    add("mra-register", "Mobile and Remote Access registration",
        "MRA has two Expressway roles. The phone trusts the Expressway edge certificate, then traverses to the core, then registers to CUCM. A missing intermediate on the edge fails before CUCM sees a REGISTER.",
        "Cisco Expressway MRA",
        ["Client", "Expressway-E", "Expressway-C", "CUCM"],
        [
            (0, 1, "TLS", "req", "The client connects to Expressway-E on the public name. The certificate chain must include intermediates."),
            (1, 2, "traversal", "note", "E traverses to C over the traversal zone. Both zones must be up."),
            (2, 3, "REGISTER", "req", "C presents the registration to CUCM. CUCM must list the traversal domain."),
            (3, 0, "200 OK", "ok", "The client is registered. Service discovery and registration are different steps. A domain that resolves is not a registration."),
        ],
        icon="cert", keys=[["Exp-E", "Public edge"], ["Exp-C", "Inside"], ["Chain", "Send intermediates"], ["Traversal", "Both zones up"]])

    add("mra-call", "MRA call media",
        "On MRA, media often hairpins on Expressway. A call that registers and then has no audio is a traversal media path, a firewall port, or an ICE failure, not a CSS problem.",
        "Cisco Expressway MRA",
        ["Remote", "Expressway", "Inside phone"],
        [
            (0, 1, "INVITE", "req", "Signaling traverses E and C to CUCM, then to the inside phone."),
            (1, 2, "INVITE", "req", "CUCM completes digit analysis as usual."),
            (0, 1, "RTP", "media", "Media is anchored or traversed at Expressway. The firewall must allow that media range."),
            (1, 2, "RTP", "media", "The inside phone sends RTP toward Expressway, not toward the remote private address."),
        ],
        chart="mos", icon="media", keys=[["Traversal", "Media ports"], ["TURN", "If ICE needs it"], ["CSS", "Still CUCM's job"], ["No audio", "After a good REGISTER"]], audio=True)

    add("e164", "E.164 and directory numbers",
        "Store a global number and present a local one. The dial plan normalizes what the user dialed into the form the route pattern expects. Mixed forms cause partial matches.",
        "E.164 and CUCM dial-plan practice",
        ["User dials", "Translation", "Route"],
        [
            (0, 1, "+E.164", "note", "A directory number or a pattern in global form, with a leading plus, is unambiguous."),
            (1, 1, "normalize", "note", "A translation pattern strips access codes and adds the country code before the route pattern sees the digits."),
            (1, 2, "route", "req", "The route pattern matches the normalized number. The gateway may need a different presentation for the provider."),
        ],
        icon="route", keys=[["+E.164", "Global form"], ["Translation", "Normalize first"], ["Presentation", "What the provider sees"], ["CSS", "Must include the pattern"]])

    add("dial-plan", "Dial-plan order",
        "Urgent patterns, translations, and the CSS order decide which pattern wins. A test call that matches the wrong pattern is working as configured.",
        "Cisco Unified CM dial plan",
        ["Digits", "Translation", "Route pattern", "Gateway"],
        [
            (0, 1, "analyze", "note", "CUCM waits for inter-digit timeout unless the match is urgent."),
            (1, 2, "transform", "note", "Translation patterns change digits and can restart analysis."),
            (2, 3, "route", "req", "The winning route pattern selects the route list."),
            (3, 3, "called party", "note", "The gateway or trunk transformation is the last change before the provider."),
        ],
        icon="route", keys=[["Urgent", "Skip the wait"], ["Translation", "Can restart"], ["CSS order", "Line then device"], ["Discard digits", "PreDot and others"]])

    add("wx-lgw-out", "Webex Calling outbound via Local Gateway",
        "The Webex app signals Webex Calling, not the gateway. The gateway is a trunk the location uses for premises PSTN. CUBE is still a B2BUA toward the carrier.",
        "Webex Calling port reference and Local Gateway guide",
        ["Webex app", "Webex Calling", "Local Gateway", "PSTN"],
        [
            (0, 1, "dial", "req", "The app sends the call into Webex Calling. The location decides the PSTN path."),
            (1, 2, "SIP TLS", "req", "Certificate-based trunks: the gateway sends SIP TLS to Webex Calling on TCP 5062, and Webex Calling connects to the listen port you set. Registration-based trunks: the gateway registers toward TCP 8934 and that session is reused."),
            (2, 3, "INVITE", "req", "The Local Gateway, usually CUBE, places a new call leg to the ITSP or to CUCM. New Call-ID."),
            (3, 2, "18x / 200", "ok", "Progress and answer return on the PSTN leg."),
            (2, 1, "18x / 200", "ok", "CUBE translates them toward Webex Calling."),
            (0, 3, "SRTP / RTP", "media", "Media between Webex and the gateway is SRTP. The PSTN leg is whatever that peer negotiated. Webex Calling is not a silent extra RTP hop you can ignore."),
        ],
        chart="codec", icon="cloud",
        keys=[["TCP 5062", "Certificate trunk to Webex"], ["TCP 8934", "Registration trunk"], ["Listen port", "You choose, certificate inbound"], ["SRTP", "Cloud side"]],
        audio=True)

    add("wx-lgw-in", "Webex Calling inbound via Local Gateway",
        "An inbound PSTN call hits the gateway first, then Webex Calling, then the user. The called number must be a number Webex Calling owns for that location.",
        "Webex Calling Local Gateway",
        ["PSTN", "Local Gateway", "Webex Calling", "User"],
        [
            (0, 1, "INVITE", "req", "The carrier sends the inbound call to the gateway."),
            (1, 2, "INVITE", "req", "The gateway sends it to Webex Calling over the trunk. The called number is the Webex Calling number, in the form the trunk expects."),
            (2, 3, "alert", "prov", "Webex Calling alerts the app or the desk device."),
            (3, 2, "200 OK", "ok", "The user answers. ACK is per leg because the gateway is a B2BUA."),
            (0, 3, "media", "media", "SRTP on the Webex side, carrier media on the PSTN side, anchored on the gateway when you flow through."),
        ],
        icon="cloud", keys=[["Called number", "Must match Webex"], ["Trunk", "Location PSTN"], ["B2BUA", "Two Call-IDs"], ["SRTP", "Toward Webex"]])

    add("wx-plan", "Webex Calling plan",
        "A Cisco Calling Plan keeps PSTN inside Webex Calling. There is no Local Gateway on that call. If you expected the CUBE to see it, the location is not using premises PSTN.",
        "Webex Calling PSTN options",
        ["User", "Webex Calling", "Cisco PSTN"],
        [
            (0, 1, "dial", "req", "The user dials. The location's PSTN connection is a calling plan, not a premises trunk."),
            (1, 2, "PSTN", "req", "Webex Calling hands the call to the Cisco calling-plan carrier."),
            (2, 1, "200 OK", "ok", "Answer returns inside the cloud path."),
            (0, 1, "media", "media", "Media stays on the Webex Calling media path. A CUBE trace will be empty, and that is expected."),
        ],
        icon="cloud", keys=[["Calling plan", "Cloud PSTN"], ["Premises", "Local Gateway instead"], ["Location", "The switch"], ["CUBE trace", "Empty on purpose"]])

    add("teams-dr-out", "Teams Direct Routing outbound",
        "The Teams client talks to Phone System. Phone System selects an SBC from the voice routing policy. The SBC then places the PSTN leg. Media bypass is optional and separate.",
        "Microsoft Learn, Plan Direct Routing",
        ["Teams client", "Phone System", "SBC", "PSTN"],
        [
            (0, 1, "dial", "req", "The client signals Microsoft 365, not the SBC."),
            (1, 1, "route", "note", "The online voice routing policy, PSTN usage, and route pick the SBC."),
            (1, 2, "INVITE", "req", "Phone System sends SIP TLS to the SBC FQDN on the port you set as SipSignalingPort. The SBC sends SIP TLS to sip.pstnhub.microsoft.com on 5061, and can fail over to sip2 and sip3."),
            (2, 3, "INVITE", "req", "The SBC, a B2BUA, places the carrier leg with its own Call-ID."),
            (3, 2, "200 OK", "ok", "The carrier answers."),
            (2, 0, "media", "media", "Without media bypass, media goes through a Teams media processor (UDP 3478–3481 and 49152–53247). With media bypass, a supported path can run direct from client to SBC."),
        ],
        chart="codec", icon="team",
        keys=[["5061", "SBC to Microsoft"], ["SipSignalingPort", "Microsoft to SBC"], ["sip.pstnhub", "Primary FQDN"], ["Bypass", "Separate media path"]],
        audio=True)

    add("teams-dr-in", "Teams Direct Routing inbound",
        "The carrier hits your SBC. The SBC sends the INVITE to Microsoft on 5061. The number must be assigned to a user or a resource account that the voice route can reach.",
        "Microsoft Learn, Direct Routing",
        ["PSTN", "SBC", "Phone System", "Teams user"],
        [
            (0, 1, "INVITE", "req", "Inbound PSTN arrives at the certified SBC."),
            (1, 2, "INVITE :5061", "req", "The SBC sends SIP TLS to the Phone System FQDN on port 5061."),
            (2, 3, "alert", "prov", "Teams alerts the user or the call queue resource account."),
            (3, 2, "200 OK", "ok", "Answer. Media follows bypass or the media processor, same as outbound."),
        ],
        icon="team", keys=[["5061", "Toward Microsoft"], ["Resource account", "Queues and attendants"], ["SBC cert", "Public name"], ["OPTIONS", "Trunk health"]])

    add("teams-options", "Teams OPTIONS and failover",
        "Direct Routing uses SIP OPTIONS as a heartbeat. If OPTIONS fails, new calls leave that SBC. Existing calls are a different question.",
        "Microsoft Learn, Direct Routing",
        ["SBC", "sip", "sip2", "sip3"],
        [
            (0, 1, "OPTIONS", "req", "The SBC probes sip.pstnhub.microsoft.com."),
            (1, 0, "200 OK", "ok", "A 200 keeps the trunk eligible."),
            (0, 1, "timeout", "err", "Missed OPTIONS mark the path down."),
            (0, 2, "OPTIONS", "req", "The SBC fails over to sip2, then sip3. Signaling failover is not the same as media bypass."),
        ],
        icon="team", keys=[["OPTIONS", "Heartbeat"], ["sip / sip2 / sip3", "Three FQDNs"], ["5061", "SBC source to Microsoft"], ["Enabled", "A drained SBC takes no new calls"]])

    add("teams-bypass", "Teams media bypass",
        "Media bypass lets the client send SRTP directly to the SBC when the network allows it. The signaling path does not change. A firewall that allows 5061 and blocks the media range looks like a successful call with no audio.",
        "Microsoft Learn, media bypass",
        ["Teams client", "SBC", "Media processor"],
        [
            (0, 1, "signaling", "req", "Signaling still goes through Phone System to the SBC."),
            (0, 1, "SRTP direct", "media", "With bypass on, and a candidate that works, media is client to SBC."),
            (0, 2, "SRTP relay", "media", "Without bypass, or when the direct path fails, media uses the Teams media processor."),
            (1, 1, "PSTN", "note", "The SBC still has a separate PSTN media leg. Bypass does not remove the carrier."),
        ],
        chart="mos", icon="media", keys=[["Signaling", "Unchanged"], ["Bypass on", "Client to SBC"], ["Processor", "The fallback"], ["IPv6", "Bypass is not supported on IPv6"]], audio=True)

    add("teams-plan", "Teams Calling Plan and Operator Connect",
        "Calling Plan and Operator Connect do not use your Direct Routing SBC. A trace on that SBC will be empty. The number's PSTN type is the first fact to collect.",
        "Microsoft Teams PSTN connectivity",
        ["User", "Phone System", "PSTN provider"],
        [
            (0, 1, "dial", "req", "The user dials. Phone System looks at the number's PSTN connectivity."),
            (1, 2, "provider", "req", "Calling Plan uses Microsoft's carrier. Operator Connect uses the operator you selected. Direct Routing would have used your SBC instead."),
            (2, 1, "answer", "ok", "Answer and media stay on that provider path."),
        ],
        icon="team", keys=[["Calling Plan", "Microsoft carrier"], ["Operator Connect", "Your operator"], ["Direct Routing", "Your SBC"], ["Number type", "Check it first"]])

    add("walk-call-setup", "End-to-end call setup",
        "This is the walkthrough to replay on a bridge: phone to CUCM, CUCM to CUBE, CUBE to the carrier, then RTP that skips CUCM.",
        "RFC 3261 and Cisco CUCM plus CUBE",
        ["Phone", "CUCM", "CUBE", "PSTN"],
        [
            (0, 1, "INVITE", "req", "The phone sends an early-offer INVITE to CUCM."),
            (1, 1, "digit analysis", "note", "Line CSS, then device CSS. The route pattern points at a route list and a SIP trunk to CUBE."),
            (1, 2, "INVITE", "req", "CUCM sends a new INVITE to CUBE. CUCM is a back-to-back user agent here."),
            (2, 3, "INVITE", "req", "CUBE matches an outbound dial-peer and sends another INVITE to the provider. Third Call-ID."),
            (3, 2, "100 Trying", "prov", "The provider accepts the request for processing."),
            (3, 2, "180 or 183", "prov", "180 is local ringback. 183 with SDP is early media. Know which one you asked for."),
            (2, 1, "18x", "prov", "CUBE translates the response toward CUCM."),
            (1, 0, "18x", "prov", "The phone rings or plays the early stream."),
            (3, 2, "200 OK", "ok", "The called party answers."),
            (2, 1, "200 OK", "ok", "CUBE answers CUCM."),
            (1, 0, "200 OK", "ok", "CUCM answers the phone. Each leg gets its own ACK."),
            (0, 2, "ACK", "req", "ACK stops at each B2BUA and is regenerated. Do not look for one ACK across all three Call-IDs."),
            (0, 3, "RTP", "media", "Audio is phone to CUBE to provider when CUBE is flow-through. CUCM's IP should not appear in the media path."),
            (0, 1, "BYE", "bye", "Hangup clears each leg in turn."),
        ],
        chart="qos", icon="route", keys=[["3 Call-IDs", "Phone, CUCM, CUBE"], ["CSS", "Line then device"], ["Flow-through", "RTP on CUBE"], ["ACK", "Per leg"]], audio=True)

    add("walk-failover", "Signaling failover walkthrough",
        "Failover is a timer plus a second path. Practice which calls die and which calls move before you promise a customer that nothing drops.",
        "CUCM groups and CUBE HA",
        ["Phone", "Primary", "Secondary"],
        [
            (0, 1, "steady", "ok", "Registration and the active dialog sit on the primary."),
            (1, 0, "failure", "err", "The primary stops. Keepalives fail. This is not instantaneous."),
            (0, 2, "re-register", "req", "The phone or the trunk uses the next configured peer."),
            (0, 2, "new call", "ok", "New calls work after registration. A mid-call that was not checkpointed drops and must be redialed."),
        ],
        icon="migration", keys=[["Timer", "Not instant"], ["Next peer", "Must be configured"], ["New calls", "After register"], ["Mid-call", "Only if checkpointed"]])

    add("ucce-comp", "UCCE comprehensive call",
        "CVP stays in the signaling path, asks ICM for instructions, and extends a VRU leg to Cisco VVB. The agent leg is another transfer. CUIC is not in the audio path.",
        "Cisco CVP 15 configuration guide, comprehensive model",
        ["Ingress", "CVP", "ICM", "VVB", "Agent"],
        [
            (0, 1, "SIP INVITE", "req", "The ingress gateway sends the call to the CVP call server. This is the switch leg."),
            (1, 2, "route request", "note", "CVP, as routing client, asks ICM over the VRU PG. ICM runs the script."),
            (2, 1, "Send to VRU", "note", "Send to VRU returns a VRU label. Type 10 Network VRU is the model Cisco documents to simplify this handoff. A correlation id matches the VRU leg on the models that use one."),
            (1, 3, "VRU leg", "req", "CVP extends the call to Cisco VVB, usually with a re-INVITE, so CVP stays in signaling and keeps the call license. REFER would step CVP out."),
            (3, 3, "VoiceXML", "media", "VVB fetches VoiceXML from the CVP VXML server and plays prompts or collects digits."),
            (2, 1, "agent label", "note", "When an agent is ready, ICM returns an agent label."),
            (1, 4, "to CUCM", "req", "CVP transfers to the agent DN on CUCM. The phone rings. Finesse shows the call."),
            (4, 0, "RTP", "media", "Audio is between the caller side and the agent. CUIC reads reporting data beside this path. It does not carry the voice."),
        ],
        chart="kpi", icon="queue",
        keys=[["Switch leg", "Ingress to CVP"], ["VRU leg", "CVP to VVB"], ["re-INVITE", "CVP stays"], ["Finesse", "Agent desktop"]])

    add("ucce-rona", "UCCE ring-no-answer",
        "RONA returns the call to the queue when the agent does not answer. If the script has nowhere to go, the caller sits in silence or the call drops.",
        "Cisco UCCE scripting",
        ["Caller", "CVP", "ICM", "Agent"],
        [
            (0, 3, "ring", "prov", "The agent device rings and Finesse offers the call."),
            (3, 2, "no answer", "err", "The RNA timer expires."),
            (2, 2, "requery", "note", "ICM requeries. The script must queue again or send the call to another target."),
            (2, 1, "label", "req", "CVP moves the call to the next label. The caller should hear queue treatment, not dead air."),
        ],
        chart="kpi", icon="queue", keys=[["RNA timer", "How long the phone rings"], ["Requery", "Script must handle it"], ["Queue", "Treatment again"], ["Finesse", "Agent goes not-ready in many designs"]])

    add("pcce", "Packaged CCE path",
        "PCCE is UCCE in a packaged model with a fixed capacity and SPOG for administration. The call still runs CVP, ICM, and Finesse. The package does not remove the legs.",
        "Cisco Packaged CCE design guide",
        ["Ingress", "CVP", "PCCE", "Finesse"],
        [
            (0, 1, "INVITE", "req", "Ingress still lands on CVP."),
            (1, 2, "script", "note", "The packaged router runs the script. Capacity is the 2000, 4000, or 12000 agent model you bought, not an unbounded cluster."),
            (2, 3, "agent", "ok", "Finesse delivers the call. SPOG is how you administer. It is not a hop in the audio path."),
        ],
        chart="kpi", icon="queue", keys=[["SPOG", "Admin, not audio"], ["2000/4000/12000", "Packaged sizes"], ["CVP", "Still there"], ["CUIC", "Reporting beside the call"]])

    add("cuic", "CUIC is beside the call",
        "CUIC shows intervals and live data from the reporting path. A chart that moves does not prove the audio leg. A chart that does not move does not mean the call failed.",
        "Cisco Unified Intelligence Center",
        ["Call", "AW/HDS", "CUIC"],
        [
            (0, 1, "write", "note", "ICM writes historical rows on the interval. Live data is a separate feed."),
            (1, 2, "query", "note", "CUIC runs a report. The join key is the routercallkey or the contact identifiers the report was built to use."),
            (2, 2, "read", "note", "Use the report to pick a call, then open the CVP and Finesse logs for that id. Do not debug RTP inside CUIC."),
        ],
        chart="kpi", icon="proof", keys=[["Interval", "Historical"], ["Live", "A different feed"], ["RouterCallKey", "Join key"], ["Not RTP", "CUIC is not the path"]])

    add("cc-route", "Queue then agent",
        "Every contact center in this campus does the same four moves: identify the contact, run a flow, queue against a skill, deliver to an agent who is ready. The product names change. The proof does not.",
        "Contact-center routing practice",
        ["Entry", "Flow", "Queue", "Agent"],
        [
            (0, 1, "arrive", "req", "A number, a chat, or a callback request creates a contact with an id."),
            (1, 2, "decide", "note", "The flow sets attributes and chooses a queue. Hours, holidays, and intent belong here."),
            (2, 3, "ready", "ok", "The longest-waiting contact goes to the longest-idle ready agent, or whatever the platform's selection is."),
            (3, 3, "RONA", "err", "If the agent does not answer, the contact returns to queue and the agent state must change or the same miss repeats."),
        ],
        chart="kpi", icon="queue", keys=[["Contact id", "The join key"], ["Queue", "The wait"], ["Ready", "Agent state"], ["RONA", "Back to queue"]])

    add("wxcc-in", "Webex Contact Center inbound",
        "A Webex Contact Center call hits an entry point, runs a Flow Designer flow, waits in a queue, and is offered to a team. The agent desktop is where you prove delivery.",
        "Webex Contact Center administrator guide",
        ["Caller", "Entry point", "Flow", "Queue", "Agent"],
        [
            (0, 1, "PSTN or Webex", "req", "The call arrives on the entry-point number. Telephony may be Webex Calling or the contact-center PSTN."),
            (1, 2, "flow", "note", "Flow Designer plays prompts, collects digits, and sets variables."),
            (2, 3, "queue", "note", "The contact waits against a queue tied to a team."),
            (3, 4, "offer", "ok", "A ready agent on that team is offered the contact. RONA returns it if they do not answer."),
            (4, 0, "media", "media", "Audio is between the caller and the agent desktop or device. The flow is not a mixer."),
        ],
        chart="kpi", icon="queue", keys=[["Entry point", "The front door"], ["Flow", "Flow Designer"], ["Team", "Who can take it"], ["Interaction", "The id in the desktop"]])

    add("wxcc-flow", "Webex CC flow steps",
        "A flow is a script with a start and a queue. If the queue activity is never reached, agents will be idle while callers hear treatment or nothing.",
        "Webex Contact Center Flow Designer",
        ["Start", "Hours", "Prompt", "Queue"],
        [
            (0, 1, "entry", "note", "The entry point selects this flow."),
            (1, 2, "open?", "note", "Hours and holiday checks branch first. A wrong time zone sends everyone to closed."),
            (2, 3, "queue", "ok", "Queue is the activity that creates wait time and makes agents eligible."),
            (3, 3, "agent", "ok", "Delivery is after the queue, not inside the prompt."),
        ],
        chart="kpi", icon="queue", keys=[["Entry point", "Binds the flow"], ["Time zone", "Hours"], ["Queue activity", "Required"], ["RONA", "After delivery"]])

    add("connect-in", "Amazon Connect inbound",
        "Connect starts a contact flow on a claimed number, queues against a routing profile, and writes a contact trace record after the contact. ContactId is the key.",
        "Amazon Connect administrator guide",
        ["Caller", "Contact flow", "Queue", "Agent"],
        [
            (0, 1, "number", "req", "The claimed phone number points at a contact flow."),
            (1, 2, "blocks", "note", "The flow sets attributes, checks hours, and transfers to a queue. A Lambda that runs past the block timeout takes the error branch."),
            (2, 3, "offer", "ok", "An agent with that queue in the routing profile, in Available state, is offered the contact."),
            (3, 3, "CTR", "note", "After the contact, the contact trace record carries ContactId, queue, and agent. That is the capture, not a guess from CloudWatch alone."),
        ],
        chart="kpi", icon="cloud", keys=[["ContactId", "Join key"], ["Routing profile", "Which queues"], ["Available", "Agent state"], ["CTR", "The record"]])

    add("genesys-in", "Genesys Cloud inbound",
        "An Architect flow answers the call, then a queue receives it. The conversation id is what you paste into a bridge.",
        "Genesys Cloud resource center",
        ["Caller", "Architect", "Queue", "Agent"],
        [
            (0, 1, "DID", "req", "The number is assigned to an Architect inbound flow."),
            (1, 2, "transfer", "note", "The flow transfers to a queue. Schedules and emergency groups branch before that."),
            (2, 3, "ALERTING", "ok", "A matching agent is alerted. The conversation id stays stable across the transfer."),
            (3, 3, "connected", "media", "Audio connects. Wrap-up is after disconnect and is not part of the audio path."),
        ],
        chart="kpi", icon="cloud", keys=[["Conversation id", "Join key"], ["Architect", "The flow"], ["Queue", "The wait"], ["Schedule", "Time zone included"]])

    add("nice-in", "NICE CXone inbound",
        "A point of contact lands on a script. The script queues to a skill. The agent must have that skill and be available. The contact id joins the script log to the agent leg.",
        "NICE CXone",
        ["Caller", "Script", "Skill", "Agent"],
        [
            (0, 1, "point of contact", "req", "The number or digital entry starts the script."),
            (1, 2, "queue", "note", "The script selects a skill and begins queue music or messages."),
            (2, 3, "deliver", "ok", "An available agent with the skill is offered the contact."),
            (3, 3, "contact id", "note", "Keep the contact id. Disposition and recording are after the conversation and use that id."),
        ],
        chart="kpi", icon="queue", keys=[["Point of contact", "Entry"], ["Skill", "The queue"], ["Contact id", "Join key"], ["Unavailable", "Will not be offered"]])

    add("five9-in", "Five9 inbound",
        "An inbound number maps to a campaign. The IVR script runs, then a skill is queued. The agent must be assigned to that skill.",
        "Five9 administrator",
        ["Caller", "Campaign", "IVR", "Skill", "Agent"],
        [
            (0, 1, "DNIS", "req", "The dialed number selects the inbound campaign."),
            (1, 2, "IVR", "note", "The script plays prompts and sets variables."),
            (2, 3, "skill", "note", "The skill is the queue."),
            (3, 4, "offer", "ok", "A ready agent assigned to the skill receives the call. The call id in the agent desktop is the capture key."),
        ],
        chart="kpi", icon="queue", keys=[["Campaign", "Inbound container"], ["DNIS", "Number map"], ["Skill", "Queue"], ["Call id", "Desktop key"]])

    add("twilio-in", "Twilio Flex inbound",
        "A number or SIP domain hits a Studio flow or a Function, which creates a TaskRouter task. Flex reserves a worker. Call SID and Task SID are different ids. Keep both.",
        "Twilio Studio, TaskRouter, and Flex",
        ["Caller", "Studio", "TaskRouter", "Flex"],
        [
            (0, 1, "webhook", "req", "The number's voice URL runs Studio or a Function. A slow webhook retries and can double-create work."),
            (1, 2, "task", "note", "TaskRouter creates a task with attributes the workflow matches to a queue."),
            (2, 3, "reservation", "ok", "A worker with a matching activity is reserved. The Flex UI accepts or rejects."),
            (3, 0, "media", "media", "Audio is the Twilio voice leg. The task is the routing object. Do not expect one id to be both."),
        ],
        chart="kpi", icon="cloud", keys=[["Call SID", "Voice leg"], ["Task SID", "Routing"], ["Workflow", "Queue choice"], ["Worker", "The agent"]])

    add("zoom-phone", "Zoom Phone call",
        "Zoom Phone registers the device to Zoom, applies the site dial plan, and sends PSTN through Zoom or through a bring-your-own carrier peer. The carrier peer is not in the path when the site uses Zoom PSTN.",
        "Zoom Phone administration",
        ["Device", "Zoom Phone", "PSTN or BYOC"],
        [
            (0, 1, "register", "req", "The phone or the app registers to Zoom Phone."),
            (1, 1, "dial plan", "note", "The site dial plan normalizes the number."),
            (1, 2, "PSTN", "req", "Zoom PSTN or the BYOC trunk takes the external leg. Internal users stay inside Zoom Phone."),
            (0, 1, "media", "media", "Media is between the device and Zoom, then onward. A BYOC SBC trace is empty unless that site uses BYOC."),
        ],
        icon="cloud", keys=[["Site", "Dial plan scope"], ["BYOC", "Your carrier peer"], ["Zoom PSTN", "No SBC of yours"], ["Call log", "The id in the admin portal"]])

    add("avaya-aura", "Avaya Aura SIP path",
        "Session Manager is the SIP core. Communication Manager still owns many station and trunk features. Adaptation on Session Manager can rewrite headers. A bad adaptation is a real outage.",
        "Avaya Aura Session Manager and Communication Manager",
        ["Endpoint", "Session Manager", "Communication Manager", "Trunk"],
        [
            (0, 1, "INVITE", "req", "The endpoint sends INVITE to Session Manager."),
            (1, 2, "route", "note", "Sequencing and the dial pattern send the call to Communication Manager when CM must process it."),
            (2, 3, "trunk", "req", "CM or Session Manager sends the call to the trunk. Entity links and adaptations change headers here."),
            (3, 2, "200 OK", "ok", "Answer returns along the same sequence."),
        ],
        icon="route", keys=[["SM", "SIP routing"], ["CM", "Features"], ["Adaptation", "Header rewrite"], ["Entity link", "Trust between servers"]])

    add("ringcentral", "RingCentral call",
        "The device registers to RingCentral. The dial plan and the digital line live in the cloud. A bring-your-own carrier changes only the PSTN edge.",
        "RingCentral admin",
        ["Device", "RingCentral", "PSTN"],
        [
            (0, 1, "register", "req", "The phone or app is online to RingCentral."),
            (1, 1, "dial", "note", "The user dials. The company dial plan and the user's permissions apply."),
            (1, 2, "PSTN", "req", "External calls use RingCentral PSTN or the connected carrier."),
            (0, 1, "media", "media", "Media goes to RingCentral. A local SBC capture stays empty unless you inserted one."),
        ],
        icon="cloud", keys=[["Digital line", "The user"], ["Company number", "Entry"], ["Permissions", "Class of service"], ["Call log", "Admin portal"]])

    add("eight-eight", "8x8 call",
        "8x8 is a cloud PBX. Registration, dial plan, and PSTN are in the 8x8 cloud unless you have a specific carrier interconnect. Prove the call with the 8x8 call id.",
        "8x8 admin console",
        ["Device", "8x8", "PSTN"],
        [
            (0, 1, "register", "req", "The endpoint is registered."),
            (1, 2, "route", "req", "Internal calls stay in 8x8. External calls take the configured PSTN."),
            (2, 1, "answer", "ok", "Answer and media return through 8x8."),
        ],
        icon="cloud", keys=[["Extension", "User"], ["Site", "Dial scope"], ["PSTN", "8x8 or interconnect"], ["Call id", "Support capture"]])

    add("mitel", "Mitel hybrid call",
        "Mitel deployments are often a controller plus SIP trunks. Name the controller and the trunk. A cloud user and a premises set do not share a dial plan unless you built that integration.",
        "Mitel administration",
        ["Set", "Controller", "SIP trunk"],
        [
            (0, 1, "seize", "req", "The set sends the call to the Mitel controller."),
            (1, 1, "dial", "note", "Class of service and the ARS or digit map select the route."),
            (1, 2, "INVITE", "req", "A SIP trunk carries the external call. It is a normal SIP dialog from here."),
            (2, 0, "RTP", "media", "Media may anchor on the controller or go direct, depending on the trunk programming."),
        ],
        icon="phone", keys=[["COS", "Permissions"], ["ARS", "Route choice"], ["SIP trunk", "External"], ["Anchor", "Check SDP"]])

    add("dialogflow", "Virtual agent then a person",
        "A virtual agent is a leg in front of the queue, not a replacement for the queue. When it must escape, it has to hand the same contact id and the collected slots to a person.",
        "Dialogflow CX and contact-center telephony",
        ["Caller", "Telephony", "CX session", "Agent"],
        [
            (0, 1, "INVITE", "req", "The contact center or the gateway opens the virtual-agent leg."),
            (1, 2, "session", "note", "A CX session starts. The session id is the join key for prompts, intents, and latency."),
            (2, 1, "fulfill", "media", "Prompts stream back as audio. Barge-in and no-input are events, not SIP failures."),
            (2, 3, "escalate", "req", "Escalation transfers to a queue and must pass the session result. A transfer that drops the slots makes the agent start over."),
        ],
        icon="cloud", keys=[["Session id", "CX join key"], ["No-input", "Not a SIP 408"], ["Escalate", "To a queue"], ["Slots", "Must survive the transfer"]])

    add("ccaas-generic", "CCaaS contact path",
        "If you do not know the product yet, still name the entry, the flow, the queue, and the agent id. Those four exist on every platform in this track.",
        "Contact-center practice",
        ["Entry", "Flow", "Queue", "Agent"],
        [
            (0, 1, "contact", "req", "Something creates a contact and an id."),
            (1, 2, "flow", "note", "A flow decides the queue."),
            (2, 3, "ready agent", "ok", "A ready agent with the skill receives it."),
            (3, 3, "id", "note", "Write the id down before you change anything."),
        ],
        chart="kpi", icon="cloud", keys=[["Entry", "Number or channel"], ["Flow", "Decision"], ["Queue", "Wait"], ["Agent id", "Who got it"]])

    add("e911-cer", "Emergency Responder call",
        "CER learns the switch port, maps it to an ERL, and picks an ELIN so the PSAP can call back. CUCM must be able to route 911 to that path. On-site notification is a separate action.",
        "Cisco Emergency Responder and Kari's Law",
        ["Phone", "CUCM", "CER", "Gateway", "PSAP"],
        [
            (0, 2, "discover", "note", "CER learns the phone's switch port, typically from switch discovery, and maps that port to an ERL."),
            (0, 1, "911", "req", "The phone dials 911. The calling search space must be able to reach the emergency pattern."),
            (1, 2, "route", "note", "CUCM routes the call to CER. CER selects the ELIN for that ERL."),
            (2, 3, "ELIN", "req", "The gateway sends the call onward with the ELIN as the calling number."),
            (3, 4, "PSAP", "ok", "The PSAP receives a callback number that ALI maps to a dispatchable location. Ray Baum's Act is why that location has to be specific."),
            (2, 2, "on-site", "note", "Kari's Law: someone on site is notified at the same time. That page or call is not the PSAP leg."),
        ],
        icon="emergency", keys=K_E911)

    add("e911-held", "Webex Calling emergency location",
        "The client asks the emergency service for a location with HELD, then the emergency call carries that location. A stale hotel network will return yesterday's building.",
        "Webex Calling emergency calling, RFC 5985 HELD",
        ["Client", "HELD", "Webex Calling", "PSAP"],
        [
            (0, 1, "HELD", "note", "The client sends a location request. The network identifier, BSSID, chassis port, or civic address selects the location."),
            (1, 0, "location", "ok", "A location comes back. If the network is unknown, the result is a default or a failure. Do not treat that as a successful test."),
            (0, 2, "911", "req", "The emergency call goes through Webex Calling with that location."),
            (2, 3, "PSAP", "ok", "The provider delivers the call and the location. On-site notification still has to fire for Kari's Law."),
        ],
        icon="emergency", keys=[["HELD", "Location request"], ["BSSID / port", "Network id"], ["Civic", "The address"], ["On-site", "Kari notification"]])

    add("e911-teams", "Teams dynamic emergency calling",
        "Teams matches the client network to an emergency address in the location information service. Direct Routing can add PIDF-LO only when the SBC and the gateway are set for it.",
        "Microsoft Learn, dynamic emergency calling",
        ["Teams client", "LIS", "Phone System", "SBC or provider"],
        [
            (0, 1, "network", "note", "The client reports subnet, BSSID, or switch chassis and port."),
            (1, 0, "address", "ok", "LIS returns the emergency address for that network. A nomadic client on a new network does not keep the office address."),
            (0, 2, "911", "req", "Phone System places the emergency call."),
            (2, 3, "PIDF-LO", "note", "On Direct Routing, PIDF-LO is passed when the SBC is configured with PidfLoSupported and the trunk agrees. Calling Plan uses Microsoft's emergency path instead."),
        ],
        icon="emergency", keys=[["LIS", "Network to address"], ["Emergency address", "Civic"], ["PIDF-LO", "Direct Routing option"], ["Nomadic", "Retest after roam"]])

    add("e911-kari", "On-site notification",
        "Kari's Law requires notification to a person on site when 911 is dialed, without a prefix. The PSAP call and the security-desk call are two legs. Test both.",
        "Kari's Law and Ray Baum's Act",
        ["Caller", "PBX", "PSAP", "Security"],
        [
            (0, 1, "911", "req", "The user dials 911, not 9-911, unless 911 itself is the pattern you built and tested."),
            (1, 2, "PSAP leg", "req", "One leg goes to the public safety answering point with a callback number and a dispatchable location."),
            (1, 3, "notify", "note", "A second action alerts on-site staff with the caller's location. If this leg fails, the PSAP call can still look fine."),
        ],
        icon="emergency", keys=K_E911)

    add("qos-path", "QoS marking path",
        "Mark voice bearer as EF, DSCP 46, as close to the phone as you trust. Re-mark at the WAN edge if the access layer is not trusted. A provider that remarks EF to best effort will show up as jitter, not as a link-down.",
        "RFC 3246 and Cisco collaboration QoS",
        ["Phone", "Access", "WAN edge", "Provider"],
        [
            (0, 1, "DSCP 46", "note", "The phone marks RTP as EF. Signaling is commonly CS3, DSCP 24, on a Cisco collaboration design."),
            (1, 2, "trust", "note", "The access switch trusts the voice VLAN or re-marks. An untrusted port that keeps the phone's mark is a choice. An untrusted port that zeros it is a different choice."),
            (2, 3, "LLQ", "note", "The WAN edge puts EF in the priority queue. The priority class needs a policer so it cannot starve the link."),
            (3, 3, "remark", "err", "If the provider remarks EF to 0, your queuing no longer sees voice. Measure DSCP before and after the provider handoff."),
        ],
        chart="qos", icon="qos", keys=K_QOS, audio=True)

    add("qos-trust", "Trust boundary",
        "Trust a mark only from a device you control. A PC on the voice VLAN can stamp EF on a backup job and starve the priority queue.",
        "Cisco QoS SRND practice",
        ["Endpoint", "Switch", "Router"],
        [
            (0, 1, "mark", "note", "The phone marks on the voice VLAN. The PC port should be remarked to best effort or a scavenger class."),
            (1, 2, "trust", "note", "The uplink trusts the switch. The router classifies on DSCP."),
            (2, 2, "police", "note", "Police the priority class. A full EF queue that is mostly backups is a trust bug, not a need for a bigger queue."),
        ],
        chart="qos", icon="qos", keys=K_QOS)

    add("qos-wifi", "Wi-Fi voice",
        "Wi-Fi voice needs WMM access categories, not just a strong signal. Voice belongs in the voice queue. A sticky roam or a power-save client sounds like packet loss.",
        "Wi-Fi multimedia, voice design",
        ["Phone", "AP", "Controller", "WAN"],
        [
            (0, 1, "WMM", "note", "The client uses the voice access category. Without WMM, frames wait with bulk data."),
            (1, 2, "roam", "note", "A roam that takes too long drops RTP. Design the overlap and the fast-roam method."),
            (2, 3, "DSCP", "note", "The controller must map the WMM category back to DSCP 46 on the wired side, or the WAN will not see EF."),
        ],
        chart="mos", icon="qos", keys=[["WMM", "Voice AC"], ["DSCP 46", "On the wire"], ["Roam", "A loss burst"], ["Power save", "Gaps in RTP"]], audio=True)

    add("qos-sdwan", "SD-WAN and voice",
        "An SD-WAN overlay can look up while it brownouts voice. The application policy has to match RTP, not only the SIP port, and the path must stay inside the delay budget.",
        "SD-WAN voice policy",
        ["Branch", "Overlay", "Hub"],
        [
            (0, 1, "classify", "note", "Match RTP, not only TCP 5061. Media is UDP and will miss a policy that names only SIP."),
            (1, 1, "path", "note", "The overlay picks a path. A lossy cheaper path is the wrong choice for EF even if the SLA color is green."),
            (1, 2, "deliver", "media", "Measure one-way delay, loss, and jitter on the overlay. Interface up is not the same as a usable voice path."),
        ],
        chart="qos", icon="qos", keys=[["RTP", "Classify media"], ["EF", "Still DSCP 46"], ["Brownout", "Up but lossy"], ["150 ms", "Budget the overlay"]], audio=True)

    add("ipv6-media", "One address family per media leg",
        "The SDP answer selects an address for that stream. An IPv4 c= line does not carry IPv6 RTP. A guest network that is IPv6-only will not reach an IPv4-only media server.",
        "RFC 3264 and ICE",
        ["Offer", "Answer", "Media"],
        [
            (0, 1, "c=", "req", "The offer lists the addresses it can use. ICE may list both families as candidates."),
            (1, 0, "selected", "ok", "The answer or the nominated pair picks one. That pair is the media path."),
            (0, 2, "RTP", "media", "Packets use that family. If one side has no address in the chosen family, the call signals and stays silent."),
        ],
        icon="route", keys=[["c=", "Connection address"], ["ICE pair", "One family"], ["IPv4-only", "Cannot send IPv6"], ["Silent 200", "Often this"]])

    add("access-path", "Phone boot path",
        "A phone with no power, no VLAN, or no DHCP never reaches CUCM. Check those before you open a SIP trace.",
        "Cisco IP phone boot",
        ["Switch", "DHCP", "TFTP", "CUCM"],
        [
            (0, 0, "PoE", "note", "The port must supply power or the phone needs a cube. No lights, no SIP."),
            (0, 1, "voice VLAN", "note", "The phone learns the voice VLAN from CDP or LLDP. A missing VLAN puts it on the data network or nowhere."),
            (1, 2, "options", "note", "DHCP gives an address, a gateway, and option 150 for TFTP."),
            (2, 3, "config", "ok", "The phone downloads its config and registers. Only then does dial tone mean the cluster."),
        ],
        icon="phone", keys=[["PoE", "Power first"], ["Voice VLAN", "CDP or LLDP"], ["Option 150", "TFTP"], ["6970", "Config files"]])

    add("mig-dual-run", "Dual-run a number",
        "Dual-run means one number can be moved back by a routing change you already rehearsed. A canary cohort proves the new path before the rest of the site.",
        "Migration practice",
        ["Carrier", "Old", "New", "Canary"],
        [
            (0, 1, "today", "note", "The number still completes on the old platform. Capture a Call-ID there."),
            (0, 2, "canary", "req", "Move a small cohort, not the executives first, by translation or by carrier routing."),
            (2, 3, "prove", "ok", "Place a test call. Save the new Call-ID, the media path, and the agent or user who answered."),
            (0, 1, "rollback", "bye", "Rollback is the route change in reverse. If you cannot say that sentence, you are not ready to cut."),
        ],
        icon="migration", keys=[["Canary", "Small cohort"], ["Two Call-IDs", "Old and new"], ["Rollback", "A route, rehearsed"], ["Evidence", "Before the window"]])

    add("mig-port", "Number port",
        "A FOC date is a carrier event. Until the port completes, calls still hit the old carrier. After it completes, SMS and CNAM can lag. Test the voice path the hour of the port.",
        "Local number portability",
        ["Old carrier", "LNP", "New carrier", "PBX"],
        [
            (0, 1, "before", "note", "Calls complete on the old carrier. Record a control call."),
            (1, 2, "FOC", "req", "At the firm order commit, routing in the public network moves."),
            (2, 3, "deliver", "ok", "The new carrier delivers to your trunk. Your dial plan must already accept the number."),
            (3, 3, "after", "note", "Voice can work while caller ID name and messaging still show the old provider. Those are separate."),
        ],
        icon="migration", keys=[["FOC", "The minute that matters"], ["Control call", "Before"], ["Test call", "After"], ["CNAM", "May lag"]])

    add("mig-rollback", "Rollback drill",
        "A rollback you have not timed is a wish. Run it once with the same people who will be awake during the window.",
        "Migration practice",
        ["Detect", "Decide", "Reverse", "Prove"],
        [
            (0, 1, "trigger", "err", "Name the metric that aborts the window: failure rate, no audio, emergency call fail."),
            (1, 2, "reverse", "note", "The reverse action is a route, a trunk, or a DNS target you can reach without a change ticket you do not have."),
            (2, 3, "prove", "ok", "The control call succeeds on the old path and you have its id."),
        ],
        icon="migration", keys=[["Trigger", "Written down"], ["Reverse", "One change"], ["Timer", "How long it took"], ["Control call", "The proof"]])

    add("mig-trunk", "SIP trunk cutover",
        "Move the trunk only after a test number works on the new peer. Keep OPTIONS up on both peers until the cut is proven.",
        "SIP trunk migration",
        ["CUCM", "Old peer", "New peer"],
        [
            (0, 1, "steady", "ok", "Production uses the old dial-peer or route group."),
            (0, 2, "test", "req", "A test pattern uses the new peer. Compare SDP, codecs, and DTMF."),
            (0, 2, "cut", "req", "The production route list prefers the new peer."),
            (0, 1, "back", "bye", "The old peer stays built so preference can flip back."),
        ],
        icon="cube", keys=[["Test pattern", "First"], ["OPTIONS", "Both peers"], ["Preference", "The cut"], ["Old peer", "Stays until hypercare"]])

    add("mig-upgrade", "CUCM upgrade path",
        "An upgrade from 12 to 14 or 15 is a maintenance window with a reboot and a database migration. Phones re-register. AXL clients break if they still speak the old schema.",
        "Cisco Unified CM upgrade guide",
        ["Publisher", "Subscribers", "Phones", "AXL clients"],
        [
            (0, 0, "backup", "note", "Take the backup and confirm you can read it before you start."),
            (0, 1, "switch", "note", "The publisher upgrades, then subscribers. Replication must catch up before you call it done."),
            (1, 2, "re-register", "ok", "Phones come back. A phone that does not is a firmware or a trust-list problem, not a dial-plan problem."),
            (3, 0, "AXL", "err", "Update AXL clients to the new schema. An old WSDL fails writes after the upgrade."),
        ],
        icon="cert", keys=[["Backup", "Before"], ["Replication", "After"], ["Phones", "Re-register"], ["AXL schema", "Update clients"]])

    add("mig-vm", "Voicemail move",
        "Move the mailbox and the message-waiting path together. A user who can leave a message on the new system and still lights the old lamp is half migrated.",
        "Voicemail migration",
        ["CUCM", "Old VM", "New VM", "Phone"],
        [
            (0, 1, "today", "note", "The pilot points at the old system. MWI comes from there."),
            (0, 2, "pilot", "req", "Cut the pilot to the new system for the canary users."),
            (2, 3, "MWI", "ok", "Prove the lamp follows a new message and clears when the message is read."),
            (0, 1, "back", "note", "Rollback is the pilot and the MWI switch, both."),
        ],
        icon="phone", keys=[["Pilot", "The forward target"], ["MWI", "Separate"], ["Mailbox", "Must exist first"], ["Canary", "A few users"]])

    add("mig-e911", "Emergency calling during a cut",
        "Do not cut a site until a test emergency call from that site reaches the right location and notifies on-site staff. A successful normal call does not prove this.",
        "Kari's Law, Ray Baum's Act",
        ["Site", "Old path", "New path", "Notify"],
        [
            (0, 1, "baseline", "note", "You already know the old ELIN and the old notification target."),
            (0, 2, "test", "req", "Place the test call the way the carrier allows, from a phone on that floor."),
            (2, 3, "notify", "ok", "On-site notification fires with the right location."),
            (0, 1, "hold", "err", "If either leg fails, the site stays on the old emergency path."),
        ],
        icon="emergency", keys=K_E911)

    add("mig-sso", "Identity cutover",
        "An identity provider outage locks the desktop and leaves the phone registered. Test a call and a desktop login as separate proofs.",
        "SSO and contact-center desktops",
        ["IdP", "Desktop", "Phone", "Agent"],
        [
            (0, 1, "token", "note", "The agent desktop needs a token. The phone does not."),
            (1, 3, "login", "ok", "Login works and the agent can go ready."),
            (2, 3, "call", "ok", "A call still arrives if the IdP is down, or it does not, depending on the platform. Know which, and write it down."),
            (0, 1, "expiry", "err", "A certificate or a secret on the scheduled job expires quietly. Alarm on the date."),
        ],
        icon="cert", keys=[["IdP", "Desktop"], ["Phone", "May stay up"], ["Secret expiry", "Alarm it"], ["Ready state", "The real test"]])

    add("qos-drop", "EF starvation",
        "If the priority queue is full of the wrong traffic, voice drops while the interface looks fine. Check who is marked EF before you buy bandwidth.",
        "Cisco LLQ",
        ["Backup", "Switch", "Priority queue", "Voice"],
        [
            (0, 1, "marked EF", "err", "A bulk flow is marked DSCP 46 because a port trusts everything."),
            (1, 2, "police", "note", "The priority queue fills. The policer drops. Voice is in that queue too."),
            (3, 2, "loss", "media", "RTP loss rises. The interface is up. Jitter and drops are in the class, not in line protocol."),
            (1, 1, "fix", "ok", "Remark the access port. Voice stays EF. The backup does not."),
        ],
        chart="qos", icon="qos", keys=K_QOS, audio=True)

    # Symptom trees
    tree("ts-one-way", "One-way audio",
         "One-way audio means signaling finished and one RTP direction did not. Start at SDP, then counters, then the filter in the middle.",
         "RFC 3264 and RTP",
         [
             ("200 and ACK", "note", "Confirm both legs reached 200 OK and ACK. If ACK is missing, this is not one-way audio yet."),
             ("SDP c= and m=", "note", "Compare address and port in each direction. A private c= line that nobody rewrote will fail one way."),
             ("RTP counters", "media", "One side's packets-sent increases. The other side's packets-received does not. That names the dead direction."),
             ("Middlebox", "err", "NAT, ACL, SIP ALG, or asymmetric routing sits on that direction. Change one of those."),
             ("Recapture", "ok", "The same Call-ID should show both directions after the change."),
         ],
         chart="mos", icon="media", keys=K_RTP, audio=True)

    tree("ts-ringback", "No ringback",
         "Missing ringback is either a missing 180, a 183 with no media, or a phone that was told not to play local ringback.",
         "RFC 3960",
         [
             ("Which 18x", "note", "180 without SDP means the caller should play local ringback. 183 with SDP means the network should play it."),
             ("Early RTP", "media", "If you negotiated 183, capture RTP before 200 OK. Silence means the early stream is not arriving."),
             ("Local ringback", "note", "If a 183 suppressed local ringback and then sent no audio, the caller hears nothing. That is a configuration pair, not a mystery."),
             ("One change", "ok", "Either restore local ringback or fix the early-media path. Then place one call."),
         ],
         icon="media", audio=True)

    tree("ts-busy", "Fast busy or reorder",
         "Reorder means the switch or the trunk refused the call. Find the final SIP response or the ISDN cause before you touch QoS.",
         "RFC 3261",
         [
             ("Final response", "err", "404, 484, 486, 503, or an ISDN cause. Write the number down."),
             ("Which hop", "note", "The Via or the trunk that generated it is the leg. A 503 from the carrier is not a CUCM CSS bug."),
             ("Pattern", "note", "If CUCM generated a 404, digit analysis did not find a pattern in the CSS. That is a dial-plan fault."),
             ("Prove", "ok", "After one change, the same digits should return 180 or 183 instead of that final error."),
         ],
         chart="sip", icon="phone", audio=True)

    tree("ts-dead-air", "Dead air after answer",
         "The call was answered and neither side hears audio. Both RTP directions are missing or the bridge inserted itself and failed.",
         "RTP",
         [
             ("Answered", "ok", "200 OK and ACK on the leg you own."),
             ("Both counters", "media", "Packets sent and received on each hop. Dead air is both directions or a mixer that is silent."),
             ("MTP or bridge", "note", "If SDP points at CUCM or a conference bridge, that resource must have a free port and a working codec."),
             ("Codec", "note", "The payload in RTP must be the payload in the answer. A mismatch is silence, not noise."),
         ],
         chart="codec", icon="media", audio=True)

    tree("ts-dtmf", "DTMF not detected",
         "The digit method that left the phone is not the method the IVR is listening for. Name the method before you change codecs.",
         "RFC 4733",
         [
             ("Method", "note", "RFC 4733 events, SIP INFO, KPML, or in-band tones. The offer shows which one was agreed."),
             ("Payload", "note", "Telephone-event must be in the answer. A transcoder that cannot pass events will eat them."),
             ("One digit", "media", "Capture a single digit end to end. If it leaves the phone and never arrives, the SBC conversion is the leg."),
             ("IVR log", "ok", "The IVR log for that contact id should show the digit after the fix."),
         ],
         icon="media", audio=True)

    tree("ts-fax", "Fax over IP failed",
         "T.38 and G.711 passthrough are different contracts. A SIP profile that strips the T.38 re-INVITE breaks fax and leaves voice working.",
         "T.38 and T.30",
         [
             ("Which mode", "note", "Confirm both sides agreed T.38 or both stayed on G.711. A mid-call re-INVITE switches to T.38."),
             ("CNG and CED", "media", "1100 Hz calling tone and 2100 Hz answer tone should be visible if you are still in audio."),
             ("Re-INVITE", "req", "If the re-INVITE is rejected, the profile or the peer refused T.38. Voice will still work."),
             ("One page", "ok", "Send one page after a single change. A long document hides the result."),
         ],
         icon="media", audio=True)

    tree("ts-cert", "Certificate failure",
         "TLS fails before SIP. The name, the chain, or the date is wrong. A packet capture of the handshake tells you which.",
         "TLS and SIP",
         [
             ("Name", "note", "The name in the certificate must match the name the client dialed."),
             ("Chain", "note", "The server must send intermediates. A client that only has the root cannot build the chain."),
             ("Clock", "err", "Not-before and not-after are absolute. NTP skew makes a good certificate look invalid."),
             ("Then SIP", "ok", "Only after the handshake do you look at REGISTER or INVITE."),
         ],
         icon="cert", keys=[["Name", "Must match"], ["Chain", "Intermediates"], ["NTP", "Not-before"], ["5061", "SIP TLS"]])

    tree("ts-dns", "DNS and SRV",
         "A trunk that uses a name fails when that name fails. NXDOMAIN and a stale resolver look like a peer outage.",
         "RFC 3263",
         [
             ("Name", "note", "Write the exact FQDN the dial-peer or trunk uses."),
             ("SRV then A", "note", "SIP locates a service with SRV, then an address. A missing SRV and a present A record are different faults."),
             ("Which resolver", "note", "The gateway's resolver, not your laptop. Query from the box that places the call."),
             ("Failover", "ok", "A second SRV target should be used only after the first is actually unreachable."),
         ],
         icon="route", keys=[["SRV", "RFC 3263"], ["A or AAAA", "The address"], ["NXDOMAIN", "Name is gone"], ["TTL", "Stale cache"]])

    tree("ts-repl", "Database replication",
         "A change on the publisher that a subscriber has not learned yet looks like a partition the phone cannot see. Check replication before you rebuild the CSS.",
         "Cisco Unified CM",
         [
             ("Where saved", "note", "Confirm the pattern exists on the publisher."),
             ("Runtime state", "note", "utils dbreplication runtimestate shows who is behind."),
             ("Which node", "note", "The phone is registered to a specific subscriber. That node must have the row."),
             ("Retest", "ok", "After replication catches up, reset one phone and place one call."),
         ],
         icon="cert")

    tree("ts-echo", "Echo",
         "Echo is a reflection with delay. Gateways cancel it on TDM legs. A pure IP call that echoes is usually a device playing speaker into mic, not a QoS queue.",
         "Voice quality",
         [
             ("Which leg", "note", "IP to IP, or IP to TDM. The canceler lives on the TDM gateway."),
             ("Delay", "note", "Echo that is almost immediate is local. Echo after a beat is the far end coming back."),
             ("Canceler", "note", "Confirm the echo canceler is on and covering the tail length you actually have."),
             ("One call", "ok", "Retest the same path. A different path is a different fault."),
         ],
         chart="mos", icon="media", audio=True)

    tree("ts-jitter", "Jitter",
         "Jitter is delay variation. The jitter buffer hides a little of it and adds delay. When it underruns, you hear gaps. The queue that caused it is upstream of the phone.",
         "ITU-T G.114 and RTP",
         [
             ("Where", "note", "RTCP or the phone stats name the direction and the size."),
             ("Queue", "note", "Look at the WAN class. A burst in the priority queue or a remarked DSCP matches the time of the complaint."),
             ("Buffer", "note", "A deeper jitter buffer trades delay for fewer gaps. It does not fix a saturated link."),
             ("Measure again", "ok", "The same call path should show a smaller jitter figure after one change."),
         ],
         chart="mos", icon="qos", keys=K_QOS, audio=True)

    tree("ts-loss", "Packet loss",
         "Loss is missing RTP sequence numbers. A policer, a bad Wi-Fi roam, or a full queue does this. The SIP ladder will look clean.",
         "RFC 3550",
         [
             ("Sequence", "media", "Gaps in RTP sequence numbers are loss. Reordering is a different pattern."),
             ("Which hop", "note", "Compare counters on the phone and on the SBC. The hop where received stops growing is the leg."),
             ("Class", "note", "Drops in the LLQ class, Wi-Fi retries, or an overlay brownout. Interface up is not evidence."),
             ("Retest", "ok", "One call, same codec, loss back under the design target."),
         ],
         chart="mos", icon="qos", audio=True)

    tree("ts-mos", "MOS fell",
         "MOS is an outcome. Codec, loss, and delay are the causes. Change one cause and read MOS again. Do not average it with a different path.",
         "ITU-T G.107 teaching model",
         [
             ("Codec", "note", "G.711 and G.729 do not share an impairment. Know which payload was answered."),
             ("Loss and delay", "note", "Read them from RTCP or the endpoint, not from a WAN average."),
             ("One variable", "note", "Change codec or fix loss, not both, or you will not know which helped."),
             ("Same path", "ok", "Repeat the call on the same two endpoints."),
         ],
         chart="mos", icon="qos", audio=True)

    tree("ts-refer", "REFER failed",
         "202 Accepted only means the transfer was requested. NOTIFY carries the result. A failed INVITE to the target is the actual fault.",
         "RFC 3515",
         [
             ("202", "ok", "The REFER was accepted. Keep looking."),
             ("NOTIFY", "note", "The sipfrag status is the result of the new INVITE."),
             ("Target", "err", "The new INVITE has its own Call-ID. That ladder is the one that failed."),
             ("Replaces", "note", "Attended transfer adds Replaces. A target that ignores Replaces rings a second time or rejects the call."),
         ],
         icon="sip", keys=[["202", "Accepted"], ["NOTIFY", "Result"], ["New Call-ID", "The target leg"], ["Replaces", "Attended"]])

    tree("ts-alg", "SIP ALG rewrote SDP",
         "A firewall SIP ALG rewrites SDP with a second opinion. Turn it off and let the SBC own the rewrite. Two rewrites produce one-way audio.",
         "SDP c=",
         [
             ("Compare c=", "note", "Capture in front of the firewall and behind it. If c= changed twice, an ALG is in the path."),
             ("Disable ALG", "note", "The SBC already rewrites SDP for the outside."),
             ("One call", "media", "RTP should arrive at the address the SBC wrote."),
             ("Leave it off", "ok", "Document the ALG change so the next firewall refresh does not turn it back on."),
         ],
         icon="route", keys=K_RTP, audio=True)

    tree("ts-srtp", "SRTP mismatch",
         "A call that negotiates RTP/AVP on one leg and RTP/SAVP on the other needs a translator or it stays silent. Optional SRTP that falls back will look like a policy bug.",
         "RFC 3711",
         [
             ("Profile", "note", "Read m= on both legs. SAVP and AVP are not interchangeable."),
             ("Crypto", "note", "a=crypto suites must overlap for SDES. DTLS-SRTP uses a fingerprint instead."),
             ("Fallback", "err", "If the policy says SRTP required and the peer falls back to RTP, the call should fail, not quietly downgrade."),
             ("Retest", "ok", "Both legs show the same profile and decoded audio."),
         ],
         icon="cert", audio=True)

    tree("ts-ghost", "Ghost INVITEs",
         "INVITEs you did not place are scans, loops, or a device retrying a failed call. The source and the Request-URI tell you which.",
         "RFC 3261",
         [
             ("Source", "note", "The Via and the real socket address. Spoofed UDP is possible. TLS is harder to spoof."),
             ("Request-URI", "note", "A scan walks extensions. A loop repeats one number with climbing CSeq or a new Call-ID each time."),
             ("Loop", "err", "A forward or a translation that returns to itself. Break the forward."),
             ("Edge", "ok", "An SBC admit list drops the rest. Do not only block on CUCM."),
         ],
         icon="sip", keys=[["Request-URI", "Who they asked for"], ["Via", "Who sent it"], ["Loop", "A forward"], ["Admit", "SBC list"]])

    tree("ts-toll", "Toll fraud",
         "A catch-all pattern plus a trunk is a billing event. Close the pattern, then look for the calls that already left.",
         "Dial-plan security",
         [
             ("Pattern", "err", "Find the route pattern that matched. A trailing dot that is too wide is the usual hole."),
             ("CSS", "note", "Who can reach that pattern: a phone, a trunk, a voicemail port, a conference."),
             ("CDR", "note", "Call detail for the window: calling number, called number, duration, trunk."),
             ("Close", "ok", "Restrict the pattern and place a test call that must now fail."),
         ],
         icon="emergency", keys=[["Pattern", "What matched"], ["CSS", "Who can dial it"], ["CDR", "What already left"], ["Trunk", "The exit"]])

    tree("ts-rec", "Recording did not resume",
         "A compliance pause that never resumes is a stuck flag, not a missing recorder. The call id should show pause and resume as two events.",
         "SIPREC, RFC 7866, and contact-center recording",
         [
             ("Pause event", "note", "The desktop or the SIPREC session shows pause at a time."),
             ("Resume", "err", "There should be a resume when the payment segment ends. If the event never left the desktop, the recorder is innocent."),
             ("Media", "media", "After resume, the forked stream should contain audio again."),
             ("One call", "ok", "A test call that pauses and resumes, with both timestamps."),
         ],
         icon="proof")

    tree("ts-mra", "MRA certificate chain",
         "Expressway-E must send the intermediate certificates. Clients fail the TLS handshake and never send REGISTER.",
         "Cisco Expressway MRA",
         [
             ("Name", "note", "The public name on the certificate matches the service discovery name."),
             ("Chain", "err", "Capture the handshake. If the intermediate is missing, the client cannot build a path to a root it trusts."),
             ("Zones", "note", "Traversal zones E and C are a later check. They do not matter until TLS succeeds."),
             ("REGISTER", "ok", "One client registers and places one on-net call."),
         ],
         icon="cert")

    tree("ts-ha", "SBC high-availability split brain",
         "Two active SBCs own the same virtual address. Neighbors flap and calls land on a box that does not have the dialog.",
         "CUBE high availability",
         [
             ("Who is active", "err", "Both boxes claim active. The redundancy group heartbeat is down or the WAN between them is split."),
             ("VIP", "note", "Neighbors ARP the virtual address and get two answers."),
             ("Heartbeat", "note", "Restore the link used for the redundancy group before you move traffic."),
             ("One active", "ok", "One box owns the VIP. A new test call completes and a checkpointed call still exists."),
         ],
         icon="cube")

    tree("ts-queue", "Queue starvation",
         "Agents are idle in one queue while another queue never reaches them. Skill assignment, priority, or an omnichannel flood is holding the pool.",
         "Contact-center routing",
         [
             ("Which queue", "note", "The contact's queue and priority, from the contact id."),
             ("Who is ready", "note", "Agents who can take that queue and are actually ready, not just logged in."),
             ("What they took instead", "err", "A higher-priority queue or a digital channel consumed them."),
             ("One change", "ok", "Priority or staffing. The next interval should show offers to the starved queue."),
         ],
         chart="kpi", icon="queue")

    tree("ts-loc", "Emergency location mismatch",
         "The call completed and the location was wrong. That is a failed emergency test even though someone answered.",
         "Ray Baum's Act",
         [
             ("Where from", "note", "The switch port, BSSID, or subnet the client actually used."),
             ("What mapped", "err", "The ERL, emergency address, or HELD result for that network id."),
             ("What the PSAP got", "note", "The callback number and the location delivered, plus whether on-site notification fired."),
             ("Fix the map", "ok", "Correct one network id. Retest from that floor, not from a lab bench."),
         ],
         icon="emergency", keys=K_E911)

    tree("ts-ntp", "Clock skew",
         "Certificates, CDRs, and logs lie when the clock steps. Fix NTP before you chase a storm of not-yet-valid errors.",
         "NTP and TLS",
         [
             ("Offset", "err", "Read the offset on the host that failed, not on your laptop."),
             ("Step", "note", "A step backward makes certificates look not-yet-valid and reorders logs."),
             ("Source", "note", "One source, reachable, not a peer that is itself unsynchronized."),
             ("Retest TLS", "ok", "The handshake succeeds and the log timestamps match the call."),
         ],
         icon="cert")

    tree("ts-oauth", "Token expiry",
         "A desktop or a scheduled job fails when the secret expires. Calls that do not need that token keep working, which hides the fault.",
         "OAuth",
         [
             ("Which token", "note", "User login, app registration, or a job secret. They expire on different dates."),
             ("Symptom", "err", "401 or an interactive login loop. Not a SIP 407 unless you are looking at a SIP challenge."),
             ("Renew", "note", "Renew and store the date where someone will see it."),
             ("Prove", "ok", "The same user or job succeeds, and a phone call still works."),
         ],
         icon="cert")

    tree("ts-license", "License exhaustion",
         "A license or a session license that runs out fails the next call or the next agent login. Existing calls often stay up.",
         "Capacity",
         [
             ("Counter", "err", "The license or session counter at the time of the failure."),
             ("Who needs one", "note", "Agent login, trunk session, MTP, or recording port. Name which counter hit the cap."),
             ("Free one", "note", "A controlled release or an added license. Do not restart the cluster as the first move."),
             ("Next call", "ok", "A new call or login succeeds and the counter is under the cap."),
         ],
         chart="erlang", icon="proof")

    tree("ts-tftp", "Phone did not get its config",
         "Registration never starts if the file does not download. DHCP option 150 and HTTP 6970 are the usual CUCM path.",
         "Cisco phone boot",
         [
             ("IP", "note", "The phone has an address in the voice VLAN."),
             ("Option 150", "note", "It points at a CUCM node that is actually up."),
             ("File", "err", "The phone requests its config. A 404 means the name is wrong or the phone was never inserted."),
             ("REGISTER", "ok", "After the file, REGISTER gets a 200."),
         ],
         icon="phone", keys=[["Option 150", "TFTP server"], ["6970", "HTTP config"], ["File name", "SEP plus MAC"], ["REGISTER", "Only after the file"]])

    tree("ts-pri", "PRI or T1 down",
         "A red alarm or a D-channel down is a circuit fault. SIP will not ring a gateway that has no B-channels.",
         "ISDN PRI",
         [
             ("Alarm", "err", "LOS, LOF, AIS, or a D-channel down. Read it on the gateway."),
             ("Channels", "note", "Busy-out versus a true outage. A full PRI returns a cause. A dead PRI does not answer."),
             ("One call", "note", "Place a call and capture the ISDN cause if signaling is up."),
             ("Carrier", "ok", "The loop or the channel is clean and a test call completes."),
         ],
         icon="route")

    tree("ts-cpu", "CUCM CPU spike",
         "A node at high CPU delays SIP and skin updates. Find the process before you reboot. A reboot hides the evidence.",
         "Cisco Unified CM",
         [
             ("Which node", "note", "The subscriber the phones are registered to, or the publisher."),
             ("Process", "err", "The process using the CPU. A trace level left at debug is a common cause."),
             ("Scope", "note", "Lower the trace or stop the job. Do not change the dial plan in the same minute."),
             ("Stable", "ok", "CPU falls and a test call completes on that node."),
         ],
         icon="cert")

    tree("ts-hunt-loop", "Hunt loop",
         "A member that forwards back to the pilot will ring until a counter saves you. Point the final forward outside the hunt.",
         "Cisco hunt lists",
         [
             ("Pilot", "note", "The number that was dialed."),
             ("Member forward", "err", "The member's CFA or CFNA target. If it is the pilot, you have the loop."),
             ("Final", "note", "Set a final destination that is not in the line group."),
             ("One call", "ok", "RNA lands on the final destination once."),
         ],
         icon="queue")

    tree("ts-midcall", "Mid-call drop",
         "A call that dies after answer lost a re-INVITE, a timer, or a failover that was not checkpointed. The BYE or the timeout names which.",
         "RFC 3261",
         [
             ("Who sent BYE", "note", "A BYE is a decision. A timeout is a dead peer or a failed re-INVITE."),
             ("re-INVITE", "err", "Hold, codec change, or transfer. A rejected re-INVITE can drop the call if the peer treats it as fatal."),
             ("Session timer", "note", "A session refresh that gets no answer will clear the dialog."),
             ("One scenario", "ok", "Repeat the same hold or transfer. The dialog stays up."),
         ],
         chart="sip", icon="sip")

    tree("ts-setup-delay", "Slow call setup",
         "Delay before ring is digit analysis, DNS, a hunting trunk, or a remote proxy. It is not jitter. Jitter happens after audio starts.",
         "RFC 3261",
         [
             ("Timestamp", "note", "INVITE to first 18x. That interval is the setup delay."),
             ("Where it waited", "note", "Inter-digit timeout, SRV lookup, or a peer that never sent 100 Trying."),
             ("100 Trying", "prov", "If your side never sent or received 100, the INVITE is retransmitting and the user waits."),
             ("One hop", "ok", "Fix the hop that owned the gap. Measure the same interval again."),
         ],
         chart="sip", icon="sip")

    tree("ts-rona", "Agent RONA loop",
         "The agent is offered and does not answer, often because the headset slept. The contact returns to queue and the same agent is offered again if state did not change.",
         "Contact center",
         [
             ("Offer", "note", "The contact id shows an offer to a named agent."),
             ("State", "err", "After RONA the agent should leave ready. If they stay ready, the loop is in the platform setting or the USB headset never answered."),
             ("Headset", "note", "A USB power-save device that does not pick up is a RONA factory."),
             ("Next offer", "ok", "The next offer goes to a different ready agent."),
         ],
         chart="kpi", icon="queue")

    tree("ts-sso", "Desktop SSO only",
         "The identity provider is down. Phones still work. Agents cannot go ready. Treat the desktop and the call path as two systems.",
         "SSO",
         [
             ("Phone", "ok", "A registered phone can still call. Prove it so you do not restart CUCM."),
             ("Desktop", "err", "The login page or the token endpoint fails."),
             ("IdP", "note", "Status of the identity provider and the certificate it presents."),
             ("Ready", "ok", "After the IdP returns, one agent goes ready and receives a queued contact."),
         ],
         icon="cert")

    tree("ts-dst", "Schedule and time zone",
         "A holiday or a daylight-saving boundary evaluated in the wrong zone sends callers to closed, or keeps them in open. The flow is doing what the clock told it.",
         "Contact-center schedules",
         [
             ("Zone", "note", "The zone on the schedule, not the zone on your laptop."),
             ("Boundary", "err", "The hour the complaint started. DST and holiday eves live here."),
             ("Branch", "note", "The flow took the closed or the open branch. The log shows which."),
             ("Retest", "ok", "A test at that wall-clock time takes the branch you wanted."),
         ],
         icon="queue")

    tree("ts-lgw", "Local Gateway media blackhole",
         "Webex Calling registration or TLS is up and RTP is not. Signaling TCP can be fine while UDP media is filtered.",
         "Webex Calling Local Gateway",
         [
             ("TLS", "ok", "The trunk is established. Certificate or registration is not the current fault."),
             ("SDP", "note", "The addresses in SDP are the ones you meant: the gateway's outside address and the Webex media address."),
             ("UDP", "err", "Media is UDP. A firewall that allows the SIP port and denies the media range produces this exact symptom."),
             ("Both ways", "ok", "RTP counters increase in both directions on one test call."),
         ],
         chart="codec", icon="cloud", audio=True)

    tree("ts-bypass", "Media bypass blocked",
         "Teams signaling works and direct media does not. The firewall or a new zone blocks the bypass range, so the call must use the media processor or it stays silent.",
         "Microsoft media bypass",
         [
             ("Bypass flag", "note", "The SBC is set for media bypass and the user is in scope."),
             ("Path", "err", "Client to SBC UDP is blocked. The processor path may also be blocked if someone locked the zone too tightly."),
             ("One path", "note", "Open the path you intend to use. Do not open every UDP port as the experiment."),
             ("Audio", "ok", "A bypass user and a non-bypass user both have two-way audio, on purpose."),
         ],
         chart="mos", icon="team", audio=True)

    tree("ts-stir", "STIR verification failed",
         "Verification fails when the signed identity and the delivered calling number disagree. An SBC that strips PAI and keeps Identity will do this.",
         "RFC 8224",
         [
             ("Identity present", "note", "The header arrived at the verifier. If it did not, transit stripped it."),
             ("Calling number", "err", "The number in the token and the number in From or PAI must match what the signer covered."),
             ("Clock", "note", "The token date is checked. Skew fails good signatures."),
             ("One call", "ok", "A signed test call verifies after the header policy is corrected."),
         ],
         icon="cert")

    tree("ts-turn", "Home agent needs TURN",
         "The browser cannot punch a direct media path through CGNAT or a SASE client. TURN relays it. If the relay is full, the agent is silent with a healthy SIP leg.",
         "RFC 8656",
         [
             ("ICE result", "note", "The selected candidate is relay, or there is no selected pair."),
             ("Capacity", "err", "TURN allocations at that moment. A full relay fails new agents and leaves old ones up."),
             ("SASE", "note", "A client that hairpins into a cloud firewall changes the candidate set. Include it in the test."),
             ("Audio", "ok", "The agent hears the caller and the allocation count is under the cap."),
         ],
         chart="mos", icon="media", audio=True)

    tree("ts-codec", "Codec mismatch",
         "The answer selected a payload the sender is not using, or a transcoder was required and none was free.",
         "RFC 3264",
         [
             ("Offer", "note", "Payloads offered."),
             ("Answer", "ok", "The single payload answered."),
             ("On the wire", "err", "The RTP payload type actually sent. If it is not the answer, that side is wrong."),
             ("Transcoder", "note", "If the two legs legally differ, a transcoder in the MRGL must have a session left."),
         ],
         chart="codec", icon="media", audio=True)

    tree("ts-park", "Call park failed",
         "Park is a hold against a slot number. If the slot is full or the retrieval CSS cannot see it, the call looks dropped.",
         "Cisco call park",
         [
             ("Park", "note", "The call left the phone and should be on a park number."),
             ("Slot", "err", "The park range is exhausted, or the retrieval partition is not in the CSS."),
             ("Retrieve", "req", "Dial the park number from a phone whose CSS includes that partition."),
             ("Back", "ok", "The original caller is still there and audio returns."),
         ],
         icon="phone")
    tree("ts-presence", "Presence state",
         "Presence is a separate subscription from the call. A call can work while the lamp is wrong. The subscription id is the thing to capture.",
         "SIP presence and CUCM",
         [
             ("Call", "ok", "Confirm the call itself is fine so you do not debug RTP."),
             ("State", "err", "The published state and the state the watcher shows. They differ at a specific hop."),
             ("Subscribe", "note", "The watcher has to be allowed to subscribe. A privacy or CSS rule blocks the lamp and not the call."),
             ("One watcher", "ok", "After one policy change, that watcher sees the new state."),
         ],
         icon="phone")
    tree("ts-rate", "API rate limit",
         "A 429 or a retry storm is the platform protecting itself. The contact may still be up. Stop the retry before you scale the dependency.",
         "HTTP APIs",
         [
             ("Status", "err", "429, a vendor throttle, or a timeout. Read the body. It names the limit."),
             ("Who retries", "note", "A webhook, a Lambda, or a screen-pop client. Retries multiply the load."),
             ("Back off", "note", "Honor Retry-After. A tight loop is how Monday morning freezes a CRM."),
             ("One contact", "ok", "A single test contact completes and the error rate falls."),
         ],
         icon="cloud")
    tree("ts-scim", "SCIM left a zombie",
         "A partial delete removes the directory user and leaves the agent still routable. The contact center id and the directory id have to be compared.",
         "SCIM provisioning",
         [
             ("Directory", "note", "The user is gone or disabled in the identity store."),
             ("Agent", "err", "The agent record still exists and can be set ready."),
             ("Join", "note", "The SCIM id and the agent id. The delete event did not reach the second system."),
             ("Disable", "ok", "The agent cannot go ready, and a new contact is not offered to them."),
         ],
         icon="cert")
    tree("ts-report-join", "Report join broke",
         "Renaming a skill changes the key historical reports join on. Live calls can be fine while yesterday's report splits in two.",
         "Contact-center reporting",
         [
             ("Live", "ok", "A call still queues and delivers. This is not an audio fault."),
             ("Key", "err", "The report joins on a name that changed. Old rows use the old name."),
             ("Map", "note", "Keep a map from the old key to the new key, or freeze the name."),
             ("Interval", "ok", "One interval after the change shows a single queue, not two."),
         ],
         chart="kpi", icon="proof")
    tree("ts-licc", "LICC on this fault",
         "Name the leg, copy the identifier, read the counter, take one capture. Then change one thing.",
         "Campus method",
         [
             ("Leg", "note", "The hop that failed, in one sentence from this section's title."),
             ("Identifier", "note", "Call-ID, ContactId, conversation id, or RouterCallKey."),
             ("Counter", "note", "The counter that should have moved and did not, or moved the wrong way."),
             ("Capture", "ok", "One ladder, one RTP sample, or one report interval. Then a single change."),
         ],
         icon="proof")

    tree("evidence-pack", "Evidence pack",
         "A pack someone else can read beats a verbal recap. The claim, the id, and the capture belong together.",
         "Campus method",
         [
             ("Claim", "note", "One sentence: what failed, for whom, since when."),
             ("Leg", "note", "The hop you believe failed."),
             ("Identifier", "note", "The id that joins the systems."),
             ("Capture", "ok", "The file, the report interval, or the command output. Link the vendor document you would re-check."),
         ],
         icon="proof")

    tree("design-read", "Read a design",
         "A design is a set of failure domains, a capacity unit, and an identity boundary. If those three are missing, the drawing is decoration.",
         "Design practice",
         [
             ("Failure domain", "note", "What dies together: a node, a site, a trunk, an identity provider."),
             ("Capacity", "note", "The unit: erlangs, agents, sessions, or trunks, with the formula you would use."),
             ("Identity", "note", "Who authenticates, and what still works when that system does not."),
             ("Proof", "ok", "The test call or the report that would show the design is still true."),
         ],
         chart="erlang", icon="route")

    tree("practice-loop", "Drill loop",
         "Answer from memory, then check the ladder, then write the miss as a new check. A drill you did not score did not happen.",
         "Campus practice",
         [
             ("Closed book", "note", "Say the leg and the identifier before you open the notes."),
             ("Compare", "note", "Open the matching flow and mark what you skipped."),
             ("Write the miss", "note", "One line you will look for next time."),
             ("One more", "ok", "A second question on the same miss. Then stop."),
         ],
         icon="proof")

    tree("reference-loop", "Use a source",
         "Names drift. The glossary in this campus is a start. The vendor's current document is the one you cite before a change.",
         "Vendor documentation",
         [
             ("Term", "note", "The product's word, not a nickname."),
             ("Document", "note", "The current guide for that version, not a blog from a different release."),
             ("What you will re-check", "note", "One behavior: a port, a timer, a header."),
             ("Then the lab", "ok", "Confirm it on a non-production call if you can."),
         ],
         icon="cert")

    tree("licc-path", "LICC",
         "Leg, identifier, counter, capture. This is the habit that keeps a bridge honest.",
         "Campus method",
         [
             ("Leg", "note", "Which hop failed. Phone, CUCM, CUBE, carrier, flow, or agent."),
             ("Identifier", "note", "Call-ID, RouterCallKey, ContactId, or conversation id."),
             ("Counter", "note", "Packets, a queue count, a license, a registration."),
             ("Capture", "ok", "The ladder or the interval that shows the counter."),
         ],
         icon="proof")

    tree("study-path", "Study order",
         "SIP before products. Products before the platform you operate. Emergency and QoS before you call yourself done.",
         "Campus study order",
         [
             ("SIP ladder", "note", "Read offer, answer, ACK, and BYE until you can draw them."),
             ("CUCM and CUBE", "note", "CSS, route pattern, dial-peer, and the two Call-IDs."),
             ("Your cloud", "note", "Webex Calling or Teams, then the contact center you run."),
             ("Prove", "ok", "E911, QoS, and one troubleshooting drill with LICC."),
         ],
         icon="proof")

    tree("names-matter", "Use the product's names",
         "A bridge wastes time when two people use different words for the same object. Use the name in the admin guide.",
         "Campus naming",
         [
             ("Object", "note", "Route pattern, dial-peer, entry point, skill, or voice route. Pick the product's noun."),
             ("Not a nickname", "note", "SBC is not always CUBE. Calling Plan is not Direct Routing."),
             ("Version", "note", "Behavior changes between releases. Name the version you are looking at."),
             ("Then debug", "ok", "Search the current document for that noun."),
         ],
         icon="cert")

    tree("call-path-map", "Call-path map",
         "Draw the signaling hops and the media hops as two lines. They are not the same line on a CUCM and CUBE call.",
         "Campus map",
         [
             ("Signaling", "note", "Phone, CUCM, CUBE, provider. Or client, cloud, SBC, provider."),
             ("Media", "media", "Who is in RTP. CUCM is usually out. CUBE is usually in when it flow-through."),
             ("Identifier", "note", "One id per signaling leg."),
             ("Where you capture", "ok", "The hop you can actually span."),
         ],
         icon="route", audio=True)

    tree("call-path-full", "Full call-path map",
         "Add registration, emergency, and the reporting system beside the call. They fail independently.",
         "Campus map",
         [
             ("Register", "note", "How the endpoint finds call control."),
             ("Call", "req", "Signaling and media, drawn apart."),
             ("Emergency", "note", "Location and on-site notification, not the normal route pattern."),
             ("Report", "note", "CUIC, CTR, or the vendor call log. Beside the call, not inside RTP."),
         ],
         icon="route")

    add("campus-tour", "Campus tour",
        "Start with the ladder, then the border, then the cloud or the contact center you run. The visuals on each section are the same method: a picture, the numbers, and a step-through.",
        "UC Lab",
        ["SIP", "CUCM", "CUBE", "Cloud or CC"],
        [
            (0, 1, "Dialog", "req", "Learn INVITE, 18x, 200, ACK, BYE, and where RTP actually flows."),
            (1, 2, "Border", "note", "CUCM chooses the route. CUBE starts a new dialog toward the carrier."),
            (2, 3, "Your platform", "ok", "Webex, Teams, UCCE, or the CCaaS you operate. The id changes. The legs do not."),
            (3, 3, "Proof", "note", "Emergency location and the QoS mark are part of done, not extras."),
        ],
        chart="qos", icon="proof", keys=[["476", "Sections"], ["14", "Tracks"], ["LICC", "The habit"], ["Offline", "This file"]], audio=True)


def load_sections() -> list[dict]:
    text = HTML.read_text(encoding="utf-8")
    key = "window.SECTIONS = "
    i = text.index(key) + len(key)
    depth = 0
    in_str = False
    esc = False
    for j, ch in enumerate(text[i:], i):
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
                return json.loads(text[i:j + 1])
    raise SystemExit("SECTIONS did not parse")


ID_MAP = {
    "home": "campus-tour",
    "learning-path": "study-path",
    "method": "licc-path",
    "mindmap": "call-path-map",
    "mindmap-master": "call-path-full",
    "naming": "names-matter",
    "hub-sip": "sip-basic",
    "proto-sip-master": "sip-basic",
    "found-4": "sip-proxy",
    "found-5": "rtp-plane",
    "found-9": "nat-media",
    "found-10": "sip-tls",
    "found-2": "e164",
    "found-3": "dial-plan",
    "proto-rtp-master": "srtp-sdes",
    "hub-cube-sbc": "cube-b2bua",
    "prod-cube": "cube-b2bua",
    "arch-sbc-topologies": "sbc-topo",
    "vend-sbc": "sbc-topo",
    "vend-sbc-generic": "sbc-topo",
    "hub-cucm": "cucm-route",
    "prod-cucm": "cucm-onnet",
    "hub-expressway": "mra-register",
    "prod-expressway": "mra-call",
    "prod-unity": "unity-mwi",
    "found-15": "dialogflow",
    "vd-webex-calling-call-flow": "wx-lgw-out",
    "vd-webex-calling-architecture": "wx-lgw-out",
    "vd-webex-calling-overview": "wx-lgw-out",
    "prod-webex": "wx-lgw-out",
    "webex-calling-advanced": "wx-lgw-in",
    "cucm-webex-calling-cutover": "mig-trunk",
    "vd-teams-phone-call-flow": "teams-dr-out",
    "vd-teams-phone-architecture": "teams-dr-out",
    "prod-teams": "teams-dr-out",
    "ms-teams-phone-pstn": "teams-plan",
    "hub-icm-ucce": "ucce-comp",
    "prod-ucce": "ucce-comp",
    "hub-pcce": "pcce",
    "cuic-reporting": "cuic",
    "found-6": "cc-route",
    "found-13": "ts-rec",
    "hub-webex-cc": "wxcc-in",
    "prod-wxcc": "wxcc-in",
    "webex-cc-flow-designer": "wxcc-flow",
    "hub-amazon-connect": "connect-in",
    "prod-connect": "connect-in",
    "amazon-connect-contact-flows": "connect-in",
    "prod-genesys": "genesys-in",
    "prod-nice": "nice-in",
    "prod-zoom": "zoom-phone",
    "hub-e911-redsky": "e911-held",
    "found-11": "e911-cer",
    "found-12": "stir-shaken",
    "hub-qos": "qos-path",
    "found-8": "qos-path",
    "net-qos": "qos-path",
    "found-0": "access-path",
    "found-1": "access-path",
    "cucm-cli": "cucm-cli",
    "proto-ice-master": "ice",
    "webrtc-agent-desktop": "webrtc",
    "net-wifi-voice": "qos-wifi",
    "net-sdwan": "qos-sdwan",
    "ipv-accuracy": "ipv6-media",
    "net-ipv6": "ipv6-media",
    "hub-migrations": "mig-dual-run",
    "found-14": "mig-dual-run",
    "trick-0": "ts-one-way",
    "hub-sev-troubleshoot": "ts-one-way",
    "sev-one-way": "ts-one-way",
}

SYMPTOM = [
    (r"one-way|blackhole|asymmetr|silent|dead air|no audio|media black", "ts-one-way"),
    (r"ringback|early media|183", "ts-ringback"),
    (r"fast busy|reorder|486|503", "ts-busy"),
    (r"dead air|after answer", "ts-dead-air"),
    (r"dtmf|rfc 2833|kpml", "ts-dtmf"),
    (r"fax|t\.38|t38", "ts-fax"),
    (r"cert|tls|certificate", "ts-cert"),
    (r"dns|nxdomain|srv", "ts-dns"),
    (r"replicat", "ts-repl"),
    (r"echo", "ts-echo"),
    (r"jitter", "ts-jitter"),
    (r"packet loss|loss burst", "ts-loss"),
    (r"\bmos\b", "ts-mos"),
    (r"refer|transfer", "ts-refer"),
    (r"\balg\b|sdp c=", "ts-alg"),
    (r"srtp|suite mismatch", "ts-srtp"),
    (r"ghost|phantom", "ts-ghost"),
    (r"toll fraud|catch-all", "ts-toll"),
    (r"record", "ts-rec"),
    (r"mra|expressway", "ts-mra"),
    (r"split brain|cube ha|failover drops", "ts-ha"),
    (r"queue starv|idle agent|omni", "ts-queue"),
    (r"e911|elin|location|nomadic", "ts-loc"),
    (r"ntp|clock", "ts-ntp"),
    (r"oauth|token|secret", "ts-oauth"),
    (r"license|exhaust", "ts-license"),
    (r"tftp|option 150", "ts-tftp"),
    (r"pri|t1|e1|isdn", "ts-pri"),
    (r"cpu", "ts-cpu"),
    (r"hunt", "ts-hunt-loop"),
    (r"mid-call|midcall|drop", "ts-midcall"),
    (r"setup delay|post-dial", "ts-setup-delay"),
    (r"rona|headset", "ts-rona"),
    (r"sso|idp", "ts-sso"),
    (r"dst|timezone|time zone|holiday", "ts-dst"),
    (r"local gateway|lgw", "ts-lgw"),
    (r"media bypass", "ts-bypass"),
    (r"stir|shaken|pai", "ts-stir"),
    (r"turn|webrtc|cgnat", "ts-turn"),
    (r"codec|transcoder|g\.729|g729", "ts-codec"),
    (r"moh|music", "cucm-moh"),
    (r"conference", "cucm-conf"),
    (r"extension mobility|\bem\b|emcc", "cucm-em"),
    (r"analog|fxo|fxs", "ts-pri"),
    (r"voicemail|unity|mwi", "unity-mwi"),
    (r"upgrade|axl", "mig-upgrade"),
    (r"qos|dscp|ef starved|queue drop|remarked ef|\bef\b", "qos-drop"),
    (r"rate limit|webhook retr|pagination", "ts-rate"),
    (r"scim|zombie", "ts-scim"),
    (r"skill rename|historical report", "ts-report-join"),
    (r"dialogflow|alias", "dialogflow"),
    (r"avaya|adaptation|diversion", "avaya-aura"),
    (r"number port|sms/cli|partial number", "mig-port"),
    (r"ipv6", "ipv6-media"),
    (r"rtcp|topology hiding", "sbc-topo"),
    (r"retention|legal hold|storage", "evidence-pack"),
    (r"canary", "mig-dual-run"),
    (r"hairpin|\bnat\b", "nat-media"),
    (r"call park|\bpark\b", "ts-park"),
    (r"presence", "ts-presence"),
    (r"regex|dial-plan|dial plan", "dial-plan"),
    (r"jabber", "mra-register"),
    (r"webex app", "wx-lgw-out"),
    (r"teams client", "teams-dr-out"),
    (r"multi-vendor|interop", "sbc-topo"),
    (r"pimg", "unity-mwi"),
    (r"agent-state|agent state", "ts-rona"),
    (r"lambda", "connect-in"),
    (r"crm context|screen pop", "ccaas-generic"),
]

TOPIC = [
    (r"early media|prack|100rel", "sip-prack"),
    (r"\bhold\b|sendonly", "sip-hold"),
    (r"attended", "sip-attended"),
    (r"\brefer\b|transfer", "sip-refer"),
    (r"cancel", "sip-cancel"),
    (r"407|401|digest", "sip-407"),
    (r"options keepalive", "sip-options"),
    (r"delayed offer", "sip-delayed"),
    (r"dtmf|2833|4733", "sip-dtmf"),
    (r"stir|shaken", "stir-shaken"),
    (r"srtp|sdes", "srtp-sdes"),
    (r"\brtp\b|rtcp", "rtp-plane"),
    (r"\bnat\b|latch", "nat-media"),
    (r"\bice\b|stun|turn", "ice"),
    (r"webrtc", "webrtc"),
    (r"codec|bandwidth|g\.711|mos", "codec-neg"),
    (r"cube|dial-peer", "cube-b2bua"),
    (r"route pattern|digit analysis|\bcss\b", "cucm-route"),
    (r"extension mobility", "cucm-em"),
    (r"srst", "cucm-srst"),
    (r"hunt", "cucm-hunt"),
    (r"music on hold|\bmoh\b", "cucm-moh"),
    (r"conference|mtp|transcoder", "cucm-mtp"),
    (r"unity|voicemail", "unity-mwi"),
    (r"expressway|mra", "mra-register"),
    (r"local gateway|webex calling", "wx-lgw-out"),
    (r"direct routing", "teams-dr-out"),
    (r"operator connect|calling plan", "teams-plan"),
    (r"\bteams\b", "teams-dr-out"),
    (r"webex cc|wxcc|flow designer", "wxcc-in"),
    (r"\bucce\b|\bcvp\b|\bicm\b|finesse", "ucce-comp"),
    (r"\bpcce\b", "pcce"),
    (r"\bcuic\b", "cuic"),
    (r"amazon connect|contact flow", "connect-in"),
    (r"genesys", "genesys-in"),
    (r"\bnice\b|cxone", "nice-in"),
    (r"five9", "five9-in"),
    (r"twilio|\bflex\b", "twilio-in"),
    (r"zoom", "zoom-phone"),
    (r"avaya", "avaya-aura"),
    (r"ringcentral", "ringcentral"),
    (r"8x8", "eight-eight"),
    (r"mitel", "mitel"),
    (r"dialogflow|virtual agent", "dialogflow"),
    (r"e911|emergency|redsky|held", "e911-held"),
    (r"\bqos\b|dscp|lldq|llq", "qos-path"),
    (r"wi-fi|wifi", "qos-wifi"),
    (r"sd-wan|sdwan", "qos-sdwan"),
    (r"ipv6", "ipv6-media"),
    (r"dual-run|canary", "mig-dual-run"),
    (r"porting|foc|lnp", "mig-port"),
    (r"rollback", "mig-rollback"),
    (r"trunk cut|sip trunk cut", "mig-trunk"),
    (r"upgrade", "mig-upgrade"),
    (r"number port", "mig-port"),
    (r"erlang|sizing|occupancy|service level", "design-read"),
]

GROUP = {
    "Start here": "licc-path",
    "SIP and media": "sip-basic",
    "CUCM and CUBE": "cube-b2bua",
    "Webex Calling and Teams Phone": "wx-lgw-out",
    "Contact center — UCCE and PCCE": "ucce-comp",
    "CCaaS and UCaaS platforms": "ccaas-generic",
    "Emergency calling": "e911-cer",
    "Voice network and QoS": "qos-path",
    "Migrations": "mig-dual-run",
    "Troubleshooting": "ts-licc",
    "Evidence habits": "evidence-pack",
    "Design notes": "design-read",
    "Practice": "practice-loop",
    "Reference": "reference-loop",
}


def first_match(blob: str, rules: list[tuple[str, str]]) -> str | None:
    for pat, fid in rules:
        if re.search(pat, blob):
            return fid
    return None


def assign(sec: dict) -> str:
    # Match the title and id only. Many section summaries repeat the same
    # words ("rollback", "Teams") and would steal the wrong diagram.
    blob = f"{sec['id']} {sec['title']}".lower()
    if sec["id"] in ID_MAP:
        return ID_MAP[sec["id"]]
    if sec["group"] == "Troubleshooting" or sec["id"].startswith(("trick", "sev")):
        return first_match(blob, SYMPTOM) or "ts-licc"
    if sec["group"] == "Migrations":
        hit = first_match(blob, [
            (r"rollback", "mig-rollback"),
            (r"port|foc", "mig-port"),
            (r"e911|emergency", "mig-e911"),
            (r"voicemail|\bvm\b|mwi", "mig-vm"),
            (r"sso|identity", "mig-sso"),
            (r"upgrade", "mig-upgrade"),
            (r"trunk", "mig-trunk"),
            (r"dual-run|canary|cutover", "mig-dual-run"),
        ])
        return hit or "mig-dual-run"
    return first_match(blob, TOPIC) or GROUP.get(sec["group"], "licc-path")


def main() -> None:
    # The campus catalog is the per-section generator. This file keeps the
    # earlier hand-authored ladders for reference; running it refreshes the page.
    import runpy
    runpy.run_path(str(Path(__file__).with_name("build-section-flows.py")), run_name="__main__")
    return
    build()
    for flow in FLOWS:
        if flow["id"].startswith("sip-") and not flow.get("header"):
            flow["header"] = "invite"
        if flow["id"] in {"cube-b2bua", "walk-call-setup", "wx-lgw-out", "teams-dr-out", "rtp-plane"} and not flow.get("header"):
            flow["header"] = "sdp"
    known = {f["id"] for f in FLOWS}
    sections = load_sections()
    mapping = {}
    missing = []
    for sec in sections:
        fid = assign(sec)
        if fid not in known:
            missing.append((sec["id"], fid))
            fid = "ts-licc"
        mapping[sec["id"]] = fid
    if missing:
        raise SystemExit(f"unknown flows: {missing[:10]}")
    payload = {
        "catalog": FLOWS,
        "sectionFlow": mapping,
    }
    # Write JS without email-like tokens. JSON from our data uses no addresses.
    text = (
        "/* Generated by scripts/build-visual-catalog.py. Do not edit by hand. */\n"
        "window.UC_FLOW_CATALOG = "
        + json.dumps(FLOWS, ensure_ascii=True, separators=(",", ":"))
        + ";\nwindow.UC_SECTION_FLOW = "
        + json.dumps(mapping, ensure_ascii=True, separators=(",", ":"))
        + ";\n"
    )
    OUT.write_text(text, encoding="utf-8")
    from collections import Counter
    c = Counter(mapping.values())
    print(f"flows {len(FLOWS)} sections {len(mapping)} distinct used {len(c)} bytes {OUT.stat().st_size}")
    charts = sum(1 for s in sections if next(f for f in FLOWS if f["id"] == mapping[s["id"]])["chart"] != "none")
    headers = sum(1 for s in sections if next(f for f in FLOWS if f["id"] == mapping[s["id"]]).get("header"))
    audio = sum(1 for f in FLOWS if f.get("audio"))
    print(f"chart sections {charts} header sections {headers} audio flows {audio}")
    print("top", c.most_common(12))


if __name__ == "__main__":
    main()
