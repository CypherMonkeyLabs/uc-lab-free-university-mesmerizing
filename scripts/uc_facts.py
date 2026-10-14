"""Teaching facts, the boss exam, and the extra call-flow scenarios."""

from __future__ import annotations

from facts_a import FACTS_A
from facts_b import FACTS_B
from facts_c import FACTS_C
from facts_d import FACTS_D

FACTS = FACTS_A + FACTS_B + FACTS_C + FACTS_D


def node(node_id: str, label: str, sub: str) -> dict:
    return {"id": node_id, "label": label, "sub": sub}


def step(src: str, dst: str, kind: str, label: str, note: str) -> dict:
    return {"f": src, "t": dst, "kind": kind, "label": label, "note": note}


SCENARIOS = [
    {
        "id": "blind",
        "title": "Blind transfer",
        "why": "A blind transfer sends the caller to the target and drops the transferor without a consult. The new leg has its own dialog.",
        "nodes": [node("a", "Phone A", "transferor"), node("cucm", "CUCM", "REFER"), node("c", "Phone C", "target")],
        "steps": [
            step("a", "cucm", "sip", "REFER", "A transfers the held party without talking to C first."),
            step("cucm", "c", "sip", "INVITE", "CUCM starts a new dialog toward the target."),
            step("c", "cucm", "sip", "180", "C is alerting. A has already asked to leave."),
            step("c", "cucm", "sip", "200", "C answered. This 200 is not A's original INVITE."),
            step("a", "c", "rtp", "RTP", "Media is between the transferred party and C, not through the transferor."),
        ],
    },
    {
        "id": "consult",
        "title": "Consult transfer",
        "why": "Consult lets the transferor talk to the target first. Hold is a re-INVITE. The transfer completes only after that second conversation.",
        "nodes": [node("a", "Phone A", "consults"), node("cucm", "CUCM", "hold"), node("c", "Phone C", "consult")],
        "steps": [
            step("a", "cucm", "sip", "re-INVITE", "A holds the original party. SDP goes sendonly or inactive."),
            step("cucm", "c", "sip", "INVITE", "The consult is a new dialog to C."),
            step("c", "cucm", "sip", "200", "A and C can talk. The original caller is still on hold."),
            step("a", "cucm", "sip", "REFER", "A completes the transfer. C is already known."),
            step("a", "c", "rtp", "RTP", "After completion the original caller and C share media."),
        ],
    },
    {
        "id": "conference",
        "title": "Ad-hoc conference",
        "why": "A conference bridge is a media resource. Audio from each phone goes to the bridge, which is not how a normal two-party call works.",
        "nodes": [node("a", "Phone A", "host"), node("cucm", "CUCM", "CFB"), node("b", "Phone B", "party")],
        "steps": [
            step("a", "cucm", "sip", "INVITE", "A presses conference. CUCM selects a bridge from the media resource group."),
            step("cucm", "b", "sip", "re-INVITE", "B is pointed at the bridge instead of directly at A."),
            step("a", "cucm", "rtp", "RTP", "A's audio goes to the conference bridge."),
            step("b", "cucm", "rtp", "RTP", "B's audio goes to the same bridge. CUCM signaling is still not the mixer."),
        ],
    },
    {
        "id": "hunt",
        "title": "Hunt group",
        "why": "The caller dials a hunt pilot. A line group chooses the member. One busy phone is not the end of the hunt.",
        "nodes": [node("a", "Caller", "pilot"), node("cucm", "CUCM", "line group"), node("b1", "Member 1", "busy"), node("b2", "Member 2", "answers")],
        "steps": [
            step("a", "cucm", "sip", "INVITE", "Digit analysis matches the hunt pilot, not a person's directory number."),
            step("cucm", "b1", "sip", "INVITE", "The line group tries member 1 according to its distribution."),
            step("b1", "cucm", "sip", "486", "Busy here is this member only."),
            step("cucm", "b2", "sip", "INVITE", "The group tries the next member."),
            step("b2", "a", "rtp", "RTP", "The member who answers owns the media."),
        ],
    },
    {
        "id": "cti-rp",
        "title": "CTI route point",
        "why": "A CTI route point has no audio of its own. An application returns a destination. If nothing answers, look at the CTI application.",
        "nodes": [node("a", "Caller", "SIP"), node("cucm", "CUCM", "RP"), node("app", "CTI app", "route"), node("ag", "Agent", "target")],
        "steps": [
            step("a", "cucm", "sip", "INVITE", "The dialed number is a CTI route point, not a phone."),
            step("cucm", "app", "sip", "Route", "CUCM asks the application where to send the call."),
            step("app", "cucm", "sip", "Label", "The application returns a directory number or device."),
            step("cucm", "ag", "sip", "INVITE", "Only now does a phone ring."),
            step("a", "ag", "rtp", "RTP", "Media is between the caller and the chosen device. The route point is not a bridge."),
        ],
    },
    {
        "id": "mra",
        "title": "MRA through Expressway",
        "why": "Mobile and Remote Access crosses Expressway-E and then Expressway-C. The phone is not registered as if it were on the desk VLAN.",
        "nodes": [node("jab", "Jabber", "outside"), node("expe", "Exp-E", "edge"), node("expc", "Exp-C", "inside"), node("cucm", "CUCM", "register")],
        "steps": [
            step("jab", "expe", "sip", "INVITE", "The client hits the edge. Certificates and the traversal zone are in this hop."),
            step("expe", "expc", "sip", "INVITE", "Expressway-E hands the signaling to Expressway-C."),
            step("expc", "cucm", "sip", "INVITE", "Expressway-C speaks to CUCM. This Call-ID is not the outside leg."),
            step("cucm", "expc", "sip", "200", "CUCM accepts the call toward the inside destination."),
            step("jab", "cucm", "rtp", "RTP", "Media traverses the Expressway path. It is not a campus LAN shortcut."),
        ],
    },
    {
        "id": "failover",
        "title": "SIP trunk failover",
        "why": "A route list tries the next route group when the first trunk fails the call. OPTIONS staying green does not mean the INVITE succeeded.",
        "nodes": [node("ph", "Phone", "SIP"), node("cucm", "CUCM", "route list"), node("a", "CUBE A", "first"), node("b", "CUBE B", "next")],
        "steps": [
            step("ph", "cucm", "sip", "INVITE", "The route pattern points at a route list, not at one trunk."),
            step("cucm", "a", "sip", "INVITE", "The first route group selects CUBE A."),
            step("a", "cucm", "sip", "503", "This INVITE failed. Reachability probes can still look fine."),
            step("cucm", "b", "sip", "INVITE", "The list tries the next group."),
            step("ph", "b", "rtp", "RTP", "Audio follows the trunk that actually answered, not the one that was preferred."),
        ],
    },
    {
        "id": "ivr-agent",
        "title": "IVR to agent",
        "why": "A prompt is treatment. The agent leg starts when the script returns a destination. Do not debug the agent while the caller is still in the menu.",
        "nodes": [node("c", "Caller", "PSTN"), node("cvp", "CVP", "prompt"), node("icm", "ICM", "script"), node("ag", "Agent", "phone")],
        "steps": [
            step("c", "cvp", "sip", "INVITE", "Ingress lands on the voice browser."),
            step("cvp", "cvp", "sip", "Prompt", "The menu plays. A prompt is not a queue."),
            step("cvp", "icm", "sip", "Digits", "The script receives the choice."),
            step("icm", "cvp", "sip", "Label", "The script returns an agent or a queue label."),
            step("cvp", "ag", "sip", "INVITE", "Now the agent phone is a destination."),
            step("c", "ag", "rtp", "RTP", "Audio moves to the agent. The prompt leg is over."),
        ],
    },
    {
        "id": "callback",
        "title": "Courtesy callback",
        "why": "Callback hangs up the wait and places a new outbound call later. The original media does not stay up, and the queue position has to be real.",
        "nodes": [node("c", "Caller", "queued"), node("q", "Queue", "offer"), node("ag", "Agent", "ready")],
        "steps": [
            step("c", "q", "sip", "INVITE", "The caller is in queue, not yet with an agent."),
            step("q", "c", "sip", "Offer", "The platform offers a callback instead of hold music."),
            step("c", "q", "sip", "BYE", "The caller leaves. The contact remains queued."),
            step("q", "ag", "sip", "Reserve", "An agent becomes ready and takes the queued contact."),
            step("ag", "c", "sip", "INVITE", "This is a new call out to the caller. It can fail even though the queue was healthy."),
        ],
    },
    {
        "id": "hold",
        "title": "Hold and resume",
        "why": "Hold is a re-INVITE, usually sendonly or inactive. Music comes from a media resource. Resume is another re-INVITE back to sendrecv.",
        "nodes": [node("a", "Phone A", "holds"), node("cucm", "CUCM", "MOH"), node("b", "Phone B", "hears")],
        "steps": [
            step("a", "cucm", "sip", "re-INVITE", "A offers inactive or sendonly. The dialog stays up."),
            step("cucm", "b", "sip", "re-INVITE", "CUCM tells B the media source is changing."),
            step("cucm", "b", "rtp", "MOH", "Music is RTP from the music source, not from A's mouthpiece."),
            step("a", "cucm", "sip", "re-INVITE", "Resume offers sendrecv again."),
            step("a", "b", "rtp", "RTP", "Two-way audio returns on the original dialog."),
        ],
    },
    {
        "id": "park",
        "title": "Call park",
        "why": "Park places the caller on an orbit. Someone else dials that orbit to retrieve. Until then it is not a completed transfer.",
        "nodes": [node("a", "Phone A", "parks"), node("cucm", "CUCM", "orbit"), node("c", "Phone C", "retrieves")],
        "steps": [
            step("a", "cucm", "sip", "Park", "A parks the caller. A is no longer the media endpoint."),
            step("cucm", "cucm", "sip", "Orbit", "The caller waits on a park number, often with music."),
            step("c", "cucm", "sip", "INVITE", "C dials the orbit code."),
            step("cucm", "c", "sip", "200", "Retrieval answers the parked call."),
            step("c", "a", "rtp", "RTP", "Media is between the original caller and C."),
        ],
    },
    {
        "id": "shared",
        "title": "Shared line",
        "why": "A shared directory number rings every device that has it. The device that answers owns the media. The others stop alerting.",
        "nodes": [node("c", "Caller", "DN"), node("cucm", "CUCM", "shared"), node("p1", "Phone 1", "rings"), node("p2", "Phone 2", "answers")],
        "steps": [
            step("c", "cucm", "sip", "INVITE", "The called number is on more than one device."),
            step("cucm", "p1", "sip", "INVITE", "Phone 1 alerts."),
            step("cucm", "p2", "sip", "INVITE", "Phone 2 alerts on the same directory number."),
            step("p2", "cucm", "sip", "200", "Phone 2 answered. Phone 1 is released from alerting."),
            step("c", "p2", "rtp", "RTP", "Audio goes to the answering device only."),
        ],
    },
    {
        "id": "vm",
        "title": "Forward to voicemail",
        "why": "No-answer forward sends a new leg to the voicemail pilot. The greeting is RTP to voicemail, not to the phone that did not answer.",
        "nodes": [node("a", "Caller", "SIP"), node("cucm", "CUCM", "CFA/CFNA"), node("vm", "Voicemail", "pilot")],
        "steps": [
            step("a", "cucm", "sip", "INVITE", "The phone rings or is busy, according to the forward rule."),
            step("cucm", "vm", "sip", "INVITE", "CUCM extends the call to the voicemail pilot."),
            step("vm", "cucm", "sip", "200", "Voicemail answered. The mailbox greeting starts."),
            step("a", "vm", "rtp", "RTP", "The caller hears the greeting from voicemail."),
        ],
    },
    {
        "id": "early",
        "title": "Early offer",
        "why": "Early offer puts SDP in the INVITE. Delayed offer waits. An MTP is a crutch when a trunk demands an offer the caller did not send. This path already offers.",
        "nodes": [node("ph", "Phone", "SDP now"), node("cucm", "CUCM", "early"), node("cube", "CUBE", "trunk")],
        "steps": [
            step("ph", "cucm", "sip", "INVITE", "The INVITE already contains an SDP offer."),
            step("cucm", "cube", "sip", "INVITE", "CUCM can forward an offer without inventing one."),
            step("cube", "cucm", "sip", "200", "The answer SDP comes back in the 200."),
            step("ph", "cube", "rtp", "RTP", "Media follows the answered offer. No MTP was required just to create an offer."),
        ],
    },
    {
        "id": "fax",
        "title": "T.38 fax switchover",
        "why": "Fax often starts as a voice call and then re-invites into T.38. Voice working does not prove the image switchover.",
        "nodes": [node("fa", "Fax A", "voice first"), node("cube", "CUBE", "switch"), node("fb", "Fax B", "T.38")],
        "steps": [
            step("fa", "cube", "sip", "INVITE", "The call begins as audio so the fax tones have a path."),
            step("cube", "fb", "sip", "INVITE", "The far side answers as a voice call."),
            step("fa", "cube", "sip", "re-INVITE", "A fax tone triggers a T.38 offer."),
            step("cube", "fb", "sip", "200", "The far side accepts image media."),
            step("fa", "fb", "rtp", "T.38", "Page data uses the image session. A rejected re-INVITE drops the fax and leaves voice looking fine."),
        ],
    },
    {
        "id": "e911",
        "title": "Emergency call",
        "why": "The emergency route and the on-site notification are parallel. A 200 OK does not prove the civic location or the callback number.",
        "nodes": [node("ph", "Phone", "911"), node("cucm", "CUCM", "CSS"), node("gw", "Gateway", "PSAP"), node("sec", "Security", "notify")],
        "steps": [
            step("ph", "cucm", "sip", "INVITE", "The emergency pattern must be reachable from this line. A 9.@ in an earlier partition can steal it."),
            step("cucm", "gw", "sip", "INVITE", "The emergency route list selects the gateway."),
            step("gw", "cucm", "sip", "200", "A dialog completed. Location is a different object."),
            step("cucm", "sec", "sip", "Notify", "On-site notification runs beside the public-safety path."),
            step("ph", "gw", "rtp", "RTP", "Audio is on the emergency media path. The notification is not the audio."),
        ],
    },
    {
        "id": "teams-dr",
        "title": "Teams Direct Routing",
        "why": "Direct Routing means your SBC faces the carrier. Calling Plan and Operator Connect do not give you those dial-peers.",
        "nodes": [node("cl", "Teams", "client"), node("ms", "Teams Phone", "cloud"), node("sbc", "Your SBC", "carrier"), node("pstn", "PSTN", "ITSP")],
        "steps": [
            step("cl", "ms", "sip", "INVITE", "The client signals Microsoft, not your old subscriber."),
            step("ms", "sbc", "sip", "INVITE", "Direct Routing hands the PSTN leg to your SBC."),
            step("sbc", "pstn", "sip", "INVITE", "Your dial plan on the SBC selects the carrier."),
            step("pstn", "sbc", "sip", "200", "Answer is on the carrier leg."),
            step("cl", "sbc", "rtp", "RTP", "Media for this PSTN call anchors at your SBC."),
        ],
    },
    {
        "id": "wxcc",
        "title": "Webex Contact Center",
        "why": "An entry point and a flow are not an agent. The queue is where the contact waits. The analyzer report is beside that path.",
        "nodes": [node("c", "Caller", "PSTN"), node("wx", "Webex CC", "entry"), node("ag", "Agent", "desktop")],
        "steps": [
            step("c", "wx", "sip", "INVITE", "The number hits an entry point."),
            step("wx", "wx", "sip", "Flow", "The flow plays treatment and decides a queue."),
            step("wx", "wx", "sip", "Queue", "The contact waits. Waiting is not an agent conversation."),
            step("wx", "ag", "sip", "Offer", "An available agent is offered the contact."),
            step("c", "ag", "rtp", "RTP", "Audio is between the caller path and the agent. The report does not carry it."),
        ],
    },
    {
        "id": "pickup",
        "title": "Call pickup",
        "why": "Pickup answers a call that was ringing another phone. It does not repair a calling search space that never reached that phone.",
        "nodes": [node("c", "Caller", "rings B"), node("cucm", "CUCM", "pickup"), node("b", "Phone B", "alerting"), node("p", "Phone P", "picks up")],
        "steps": [
            step("c", "cucm", "sip", "INVITE", "B is alerting because B's partition was reachable."),
            step("cucm", "b", "sip", "180", "B rings. P has not answered anything yet."),
            step("p", "cucm", "sip", "Pickup", "P invokes pickup for that group."),
            step("cucm", "p", "sip", "200", "P is now the answering device."),
            step("c", "p", "rtp", "RTP", "Media moves to P. B stops ringing."),
        ],
    },
    {
        "id": "snr",
        "title": "Single number reach",
        "why": "Single number reach extends a call to a remote destination. The mobile leg is a PSTN call with its own media. If the desk answers, the mobile leg stops.",
        "nodes": [node("c", "Caller", "DN"), node("cucm", "CUCM", "SNR"), node("desk", "Desk", "rings"), node("mob", "Mobile", "PSTN")],
        "steps": [
            step("c", "cucm", "sip", "INVITE", "The enterprise number rings the desk and the remote destination."),
            step("cucm", "desk", "sip", "INVITE", "The desk phone alerts."),
            step("cucm", "mob", "sip", "INVITE", "CUCM places a PSTN call to the mobile."),
            step("mob", "cucm", "sip", "200", "The mobile answered first."),
            step("c", "mob", "rtp", "RTP", "Audio goes to the mobile through the gateway. The desk stops alerting."),
        ],
    },
]


def boss(question: str, choices: list[str], answer: int, why: str) -> dict:
    return {"q": question, "choices": choices, "answer": answer, "why": why}


BOSS = [
    boss(
        "A line's CSS lists the PSTN partition before the emergency partition. The user dials 911. What happens in this teaching model?",
        ["911 matches 9.@ in the earlier partition and never reaches the emergency pattern.", "CUCM always prefers 911 no matter the partition order.", "The call fails closed with no route.", "RTP is sent to CUIC."],
        0,
        "Partition order is the search. A match in an earlier partition stops the search.",
    ),
    boss(
        "An emergency call returns 200 OK and the dispatch address is the wrong building. What is still unproved?",
        ["The civic location and the callback identity.", "That SIP can complete a dialog.", "That the phone was registered.", "That a route pattern existed."],
        0,
        "Dialog success is not location success.",
    ),
    boss(
        "CUBE is in the path. Which identifier must you read per leg?",
        ["Call-ID. A B2BUA mints a new one.", "The original Via branch from the phone, unchanged end to end.", "The CUIC schedule id.", "The phone's button template."],
        0,
        "The ladder before CUBE is not the ladder after it.",
    ),
    boss(
        "A normal phone-to-CUBE-to-carrier call is connected. Where is the audio?",
        ["Phone to CUBE to the carrier, unless an MTP or transcoder is actually invoked.", "Through CUCM for every packet.", "Through the historical report.", "Inside a single Call-ID from the phone to the carrier."],
        0,
        "CUCM did the signaling. Media takes the SDP path.",
    ),
    boss(
        "The agent phone rings and Finesse shows no call. Where is the split?",
        ["Between the phone INVITE and the CTI desktop event.", "On the carrier, because the phone would not ring otherwise.", "In the QoS policy.", "In the voicemail pilot."],
        0,
        "PG, CTI, and Finesse are the desktop path.",
    ),
    boss(
        "OPTIONS to the trunk is green and INVITEs return 503. What is true?",
        ["OPTIONS is reachability. The INVITE can still hit a capacity or policy limit.", "The trunk is down, so ignore the 503.", "The phones are unregistered.", "The CSS is empty."],
        0,
        "A probe is not a call.",
    ),
    boss(
        "Voice is marked EF and chops whenever a backup runs. What is missing?",
        ["A queue that actually treats EF as priority while the link is congested.", "A longer directory number.", "A second From header.", "A new hunt pilot."],
        0,
        "The mark is a label. The queue is the behavior.",
    ),
    boss(
        "A trunk requires early offer and the caller sent no SDP. Why would an MTP show up?",
        ["CUCM needs something to create an offer. Confirm that this MTP is that reason, then decide if you still want it.", "MTPs are required on every phone.", "An MTP repairs a wrong CSS.", "An MTP encrypts RTP by itself."],
        0,
        "Do not leave an accidental media dependency in place.",
    ),
    boss(
        "Which transfer lets the transferor talk to the target before the original caller is connected?",
        ["Consult.", "Blind.", "A 180 Ringing with no REFER.", "Call pickup."],
        0,
        "Blind sends the caller onward without that conversation.",
    ),
    boss(
        "Which identifier joins a UCCE contact across router logs and CUIC?",
        ["RouterCallKey, with the day or time context the logs require.", "The agent's first name.", "The SIP Call-ID from the carrier only.", "The DSCP value."],
        0,
        "The report and the ladder are different stories until you join them.",
    ),
    boss(
        "You own the PSTN carrier and use Webex Calling. Which design has a local gateway?",
        ["Premises PSTN through a local gateway.", "Cisco Calling Plan.", "A CUIC-only deployment.", "A phone wallpaper package."],
        0,
        "Calling Plan does not put dial-peers on your SBC.",
    ),
    boss(
        "Teams Phone reaches the carrier through your SBC. What is that model called?",
        ["Direct Routing.", "Operator Connect, which does not use your SBC the same way.", "Cisco Calling Plan.", "A CUCM route filter."],
        0,
        "Name the PSTN model before you troubleshoot the trunk.",
    ),
    boss(
        "A caller is hearing a menu. What is not true yet?",
        ["An agent has been reserved.", "A prompt resource is in the path.", "Signaling has reached the voice browser.", "You can still capture this leg."],
        0,
        "Treatment is not an agent conversation.",
    ),
    boss(
        "The agent phone built-in bridge is disabled, and you still must record the PSTN audio. Where can the fork live?",
        ["At the SBC, if that is where the carrier media is anchored.", "Only on the phone bridge you just disabled.", "Inside the historical report.", "In a wrap-up code."],
        0,
        "Recording is a copy of media, not a row in a report.",
    ),
    boss(
        "Kari's Law, for an MLTS, requires which pair?",
        ["Direct access to emergency service without a prefix, and on-site notification.", "Only a longer SIP timer.", "Only DSCP EF.", "A conference bridge on every call."],
        0,
        "Notification does not replace the emergency route, and a 9 prefix requirement is the failure Kari's Law names.",
    ),
    boss(
        "A laptop at home uses VPN. Emergency discovery still shows the headquarters switch port. What is wrong?",
        ["The discovered location is not the person's location.", "TLS finished, so the address must be right.", "The codec is G.711.", "The route list has two groups."],
        0,
        "Network location and civic location diverged.",
    ),
    boss(
        "G.711 at 20 ms, counting IP, UDP, and RTP and not Ethernet, is about how much per call?",
        ["80 kbit/s.", "8 kbit/s.", "1.5 Mbit/s.", "64 bytes per second."],
        0,
        "160-byte payloads, 40 bytes of headers, 50 packets a second. Ethernet overhead makes it about 87.2 kbit/s.",
    ),
    boss(
        "What completes an INVITE transaction after the 200 OK?",
        ["ACK.", "BYE.", "A second 180.", "RTCP alone."],
        0,
        "The ACK finishes that transaction. Media is still a separate problem.",
    ),
    boss(
        "A 183 arrives and the caller hears silence. What do you open?",
        ["Early-media RTP and the SDP, not a hunt for a missing 180 as the only theory.", "The wallpaper file.", "The CUIC schedule.", "The phone's directory sort."],
        0,
        "183 often means early media. Silence is then a media fault.",
    ),
    boss(
        "Two CUBE dial-peers match. One is 911 preference 2. One is 9T preference 1. The digits are 911. Which wins in this teaching model?",
        ["911. Longest match beats a better preference on a shorter pattern.", "9T, because preference 1 always wins.", "Both, in a conference.", "Neither, because preferences differ."],
        0,
        "Length first, then preference.",
    ),
    boss(
        "Courtesy callback is best described as:",
        ["A later outbound call, after the caller has left the original media path.", "The original RTP stream paused for an hour.", "A shared line.", "A DSCP rewrite."],
        0,
        "The queue has to remember the contact. The return call is new.",
    ),
    boss(
        "Offered load in erlangs is:",
        ["Calls per hour times average handle time in seconds, divided by 3600.", "Agents times occupancy only.", "DSCP times packetization.", "Trunks times Call-ID count."],
        0,
        "That is the teaching load figure. Shrinkage is extra.",
    ),
    boss(
        "A safe number move starts with:",
        ["Both systems proving the path, and a rollback you have rehearsed.", "Deleting the old route the night before.", "Turning off QoS.", "A new Call-ID format."],
        0,
        "Dual-run is how you still have a way back.",
    ),
    boss(
        "LICC asks you to name, before the change:",
        ["One leg, one identifier, one counter, and one capture.", "A vendor logo.", "The caller's street address in the lab.", "A fresh dial plan from memory."],
        0,
        "That pack is what the next person can read.",
    ),
]
