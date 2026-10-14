#!/usr/bin/env python3
"""Add cited Webex Calling and Teams Phone lessons. Original modules stay."""

from __future__ import annotations

import json
import re
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRICULUM = ROOT / "campus" / "assets" / "curriculum"
SECTIONS = CURRICULUM / "sections"
MANIFEST = CURRICULUM / "manifest.js"
HTML = ROOT / "campus" / "uc-lab-free-university.html"
CHECKER = ROOT / "scripts" / "check-campus.py"
INTEGRITY = CURRICULUM / "integrity.json"

PORT = "https://help.webex.com/en-us/article/b2exve/Port-Reference-Information-for-Cisco-Webex-Calling"
WX = "https://help.webex.com/en-us/article/8jda92/Webex-Calling"
CUBE = "https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html"
CUCM = "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html"
DESIGN = "https://www.cisco.com/c/en/us/solutions/enterprise/design-zone-collaboration/index.html"
SRND = "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/srnd/collab12/collab12.html"
RFC3261 = "https://www.rfc-editor.org/rfc/rfc3261"
RFC3711 = "https://www.rfc-editor.org/rfc/rfc3711"
RFC4566 = "https://www.rfc-editor.org/rfc/rfc4566"
PHONE = "https://learn.microsoft.com/en-us/microsoftteams/setting-up-your-phone-system"
DR = "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-plan"
ROUTE = "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-voice-routing"
LMO = "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-media-optimization-configure"
SBA = "https://learn.microsoft.com/en-us/microsoftteams/direct-routing-survivable-branch-appliance"
E911 = "https://learn.microsoft.com/en-us/microsoftteams/configure-dynamic-emergency-calling"
CONSIDER = "https://learn.microsoft.com/en-us/microsoftteams/considerations-direct-routing"


def topic(tid, title, sub, lead, points, trap, lab, quiz, cite, actors):
    return {
        "id": tid,
        "title": title,
        "sub": sub,
        "lead": lead,
        "points": points,
        "trap": trap,
        "lab": lab,
        "quiz": quiz,
        "cite": cite,
        "actors": actors,
    }


def webex():
    rows = []
    add = rows.append
    add(topic(
        "wx-control-hub-sor", "Control Hub is the system of record", "Users, locations, numbers, devices",
        "Webex Calling administration starts in Control Hub. A change that exists only on the Local Gateway is not yet a user, a number, or a location.",
        [
            "Users, workspaces, numbers, and devices are Control Hub objects.",
            "A location owns the PSTN connection for the people placed in it.",
            "Calling analytics and call history are read from the org, not from a phone's local menu.",
            "Role-based admin access is part of the design. A full admin is not the canary account.",
        ],
        "Treating the Local Gateway CLI as the system of record. If Hub and the gateway disagree, inbound numbers follow Hub.",
        [
            "In a lab org, create one location and one user. Assign a synthetic extension.",
            "Place a test call on-net and record the call id from Control Hub.",
            "Change the user's location and write what the gateway did not learn by itself.",
            "Name the admin role you would give a help desk, and the role you would not.",
        ],
        [
            ("Where is the system of record for a Webex Calling user?", "Control Hub. The gateway is the PSTN edge, not the user database."),
            ("What does a location own?", "The PSTN connection and the dialing context for the people in that location."),
            ("Which identifier joins a Hub call history row to a gateway ladder?", "The Webex call id on one side and the SIP Call-ID on the gateway leg. They are not the same string across a B2BUA."),
            ("What fails if you only edit the gateway dial plan?", "Hub still routes from its number and location. The gateway change can black-hole a call Hub thinks is valid."),
        ],
        ("Webex Calling", WX),
        ["Admin", "Control Hub", "Location"],
    ))
    add(topic(
        "wx-locations", "Locations decide the PSTN", "One site, one connection type",
        "A Webex Calling location is the site boundary for dialing and for the PSTN choice. People in that location inherit it.",
        [
            "Calling Plan and a Local Gateway are selected per location, not per phone button.",
            "Extension length and outbound digit rules live with the location.",
            "Emergency location data is attached to the site, then tested.",
            "Two locations can use two different PSTN connections in one org.",
        ],
        "Moving a user between locations and expecting the old gateway dial-peer to follow them.",
        [
            "Create two lab locations with different PSTN connection types on paper, even if only one gateway exists.",
            "Place the same test user in location A and record the outbound path.",
            "Move the user to location B and record which path Hub selects.",
            "Write the rollback: which location the canary user returns to.",
        ],
        [
            ("What object selects Calling Plan versus a Local Gateway?", "The location's PSTN connection."),
            ("Do all users in an org share one PSTN type?", "No. Each location has its own connection."),
            ("What else moves when you change a user's location?", "Dialing context and the emergency site context. Re-test both."),
            ("What is a safe canary after a location move?", "One inbound DID and one outbound national call, plus the emergency test number your provider documents."),
        ],
        ("Webex Calling", WX),
        ["User", "Location", "PSTN"],
    ))
    add(topic(
        "wx-mt-versus-di", "Multi-tenant and Dedicated Instance", "Do not mix the runbooks",
        "Webex Calling multi-tenant is Hub-native calling. Dedicated Instance is a CUCM-class cloud with its own trunks, clusters, and failure domains.",
        [
            "Multi-tenant features are the Control Hub calling feature set.",
            "Dedicated Instance keeps CUCM administration patterns, including trunks toward a Local Gateway.",
            "A DI dial plan is not a location dial plan with a new name.",
            "Name the architecture in the first sentence of every ticket.",
        ],
        "Applying a multi-tenant Local Gateway checklist to a Dedicated Instance trunk, or the reverse.",
        [
            "Write two columns: multi-tenant and Dedicated Instance.",
            "List the admin UI, the PSTN edge, and the call identifier for each.",
            "Pick one failure, a registration flap, and say which log you open first in each column.",
            "Do not paste a production cluster name. Use lab labels.",
        ],
        [
            ("What is Dedicated Instance?", "A CUCM-class calling instance in Webex, not the same object as multi-tenant Webex Calling."),
            ("Where do you administer multi-tenant users?", "Control Hub."),
            ("Why does the first sentence of a ticket name the architecture?", "The evidence and the rollback differ. The wrong runbook changes the wrong box."),
            ("Does Dedicated Instance remove the need for a PSTN edge?", "No. Premises PSTN still needs a gateway or an equivalent trunk. Read the current design guide for that release."),
        ],
        ("Collaboration SRND", SRND),
        ["Hub", "Dedicated Instance", "Gateway"],
    ))
    add(topic(
        "wx-calling-plan", "Cisco Calling Plan", "Cloud PSTN, no customer gateway",
        "Cisco Calling Plan is cloud PSTN for that location. There is no customer Local Gateway to capture, and looking for one wastes the first half hour.",
        [
            "Numbers are assigned in Control Hub to users or workspaces.",
            "Outbound permission is a Hub policy, not a CUBE dial-peer.",
            "Media stays on the Webex Calling media path. SRTP is the expectation toward the cloud.",
            "Porting a number is a carrier record plus a Hub assignment. One without the other is a black hole.",
        ],
        "Debugging TCP 5062 on a Calling Plan location. That port is the certificate Local Gateway, and this location does not use one.",
        [
            "On paper, mark a location as Calling Plan.",
            "List the evidence you can collect: Hub call history, number assignment, and the client call id.",
            "List the evidence you will not find: a CUBE dial-peer for that call.",
            "Write the inbound test and the outbound test as two lines.",
        ],
        [
            ("Does Calling Plan use a customer Local Gateway?", "No."),
            ("Where do you look when a Calling Plan user cannot dial out?", "Hub outbound permission, the number, and the location. Not a dial-peer."),
            ("What still has to be true for inbound DID?", "The carrier points the number at Webex and Hub assigns that number."),
            ("Which port reference do you open for a Local Gateway, not for Calling Plan?", "The Webex Calling port reference. Calling Plan does not present TCP 5062 to your firewall."),
        ],
        ("Webex Calling ports", PORT),
        ["User", "Webex Calling", "Cloud PSTN"],
    ))
    add(topic(
        "wx-premises-pstn", "Premises PSTN", "Your carrier, your gateway",
        "Premises PSTN keeps the carrier trunk on a Local Gateway you operate. Webex Calling tells the gateway about the call. The carrier still sees your CUBE.",
        [
            "The location's PSTN connection points at the gateway, not at Cisco Calling Plan.",
            "Inbound DID must exist on the carrier, on the gateway translation, and on the Hub number.",
            "Outbound digits are normalized twice if you are careless: once in Hub and once on a dial-peer.",
            "A canary DID is a number you can call from a phone that is not on your LAN.",
        ],
        "Proving the trunk with an on-net extension call. That call never reaches the carrier.",
        [
            "Draw Hub, Local Gateway, and the carrier as three boxes.",
            "Mark which box owns the DID assignment.",
            "Place one inbound canary and one outbound canary. Synthetic numbers only.",
            "Write the Call-ID you expect to change at the gateway.",
        ],
        [
            ("Who operates the carrier-facing SBC in premises PSTN?", "You do. It is the Local Gateway, typically CUBE."),
            ("Why is an on-net call a weak trunk test?", "It can complete inside Webex Calling and never select the gateway."),
            ("Where can digit normalization happen twice?", "In the location dial plan and again on a CUBE translation or dial-peer."),
            ("What three places must agree on an inbound DID?", "The carrier, the gateway, and the Control Hub number assignment."),
        ],
        ("Cisco CUBE", CUBE),
        ["Webex Calling", "Local Gateway", "Carrier"],
    ))
    add(topic(
        "wx-lgw-certificate", "Certificate-based Local Gateway", "SIP TLS toward TCP 5062",
        "A certificate-based Local Gateway sends outbound SIP TLS toward TCP 5062. Trust is the certificate chain, not a registration username.",
        [
            "The gateway initiates the TLS connection to Webex.",
            "TCP 5062 is the signaling port for this trunk type. Do not substitute 5061 from a CUCM habit.",
            "The certificate must match the trust bundle the current Webex document names.",
            "A hard cut of the certificate drops registration-equivalent sessions. Overlap the new cert before you delete the old one.",
        ],
        "Configuring a registrar and a digest password on a certificate trunk, then wondering why it never registers.",
        [
            "Read the current port reference and write down 5062 next to the words certificate trunk.",
            "On a lab CUBE, display the trustpoint you would use. Do not paste a private key anywhere.",
            "Plan the overlap: new cert installed, calls still up, old cert removed only after a canary.",
            "Capture the TLS handshake failure text if the canary fails. That text is the evidence.",
        ],
        [
            ("Which TCP port does a certificate-based Local Gateway use toward Webex?", "TCP 5062."),
            ("What proves trust?", "The certificate chain named in the current Webex gateway guide, not a shared password."),
            ("Why does a CUCM 5061 habit mislead you?", "Webex Calling's certificate trunk port is 5062."),
            ("What is the safe way to rotate the certificate?", "Install and trust the new certificate before you remove the old one, then place the canary."),
        ],
        ("Webex Calling ports", PORT),
        ["Local Gateway", "Webex Calling", "PSTN"],
    ))
    add(topic(
        "wx-lgw-registration", "Registration Local Gateway", "TCP 8934 and a reused session",
        "A registration-based Local Gateway registers to Webex. The documented signaling port is TCP 8934, and that registration session is reused for calls.",
        [
            "The gateway is the registrant. Webex is the registrar for this trunk type.",
            "If the registration drops, new calls drop with it. Calls already up depend on the media path that was negotiated.",
            "Credentials and the outbound proxy belong in the lab notebook next to the port.",
            "Do not mix this trunk with a certificate trunk on the same location story.",
        ],
        "Looking for TCP 5062 on a registration trunk, or for a registration on a certificate trunk.",
        [
            "Write the trunk type at the top of the lab page: registration.",
            "Note TCP 8934 as the signaling port from the port reference.",
            "Simulate a registration loss in a lab and record whether a new call starts.",
            "Record one Call-ID from a call that used the registered session.",
        ],
        [
            ("Which port does the registration trunk use?", "TCP 8934, per the Webex Calling port reference."),
            ("What is reused?", "The registration session carries the call signaling."),
            ("What fails first when registration drops?", "New calls. Check whether existing media is a separate question."),
            ("How do you avoid the certificate-trunk mix-up?", "Write the trunk type before you choose a port or a debug command."),
        ],
        ("Webex Calling ports", PORT),
        ["Local Gateway", "Webex registrar", "PSTN"],
    ))
    add(topic(
        "wx-lgw-ports", "Ports you actually open", "Signaling is not the media range",
        "The Webex Calling port reference is the list you implement. A remembered CUCM port list is a different product.",
        [
            "Certificate trunks and registration trunks do not share a signaling port.",
            "Media is a UDP range in the current document. Copy the range into the firewall ticket with the date you read it.",
            "HTTPS to Webex services is not a substitute for the SIP signaling port.",
            "Return traffic matters. A policy that allows the outbound SYN and forgets the media pins one-way audio.",
        ],
        "Opening only TCP 5061 because that is what the last CUBE deployment used.",
        [
            "Open the port reference and write the access date on the lab page.",
            "Make two rows: signaling for your trunk type, and media.",
            "Compare those rows to the firewall request. Highlight any port you invented.",
            "After a test call, confirm the capture shows the ports you requested, not a different range.",
        ],
        [
            ("Why date the port reference?", "Webex updates the ranges. An undated memory is not a design."),
            ("Are signaling and media the same socket?", "No. SIP signaling and RTP are different ports and often different devices."),
            ("What does a one-way audio firewall look like?", "Signaling completes and one RTP direction is dropped."),
            ("Which document wins over a CUCM cheat sheet?", "The current Webex Calling port reference."),
        ],
        ("Webex Calling ports", PORT),
        ["Firewall", "Local Gateway", "Webex media"],
    ))
    add(topic(
        "wx-srtp-to-cloud", "SRTP toward Webex Calling", "The padlock is not the design",
        "Media toward Webex Calling is SRTP. A gateway that offers plain RTP toward the cloud fails the call or fails the policy, depending on what you negotiated.",
        [
            "SRTP is RTP protected as described in RFC 3711. The keys travel in the signaling, which is why the SIP leg must be protected too.",
            "The c= line still names an address. Encryption does not fix a black-hole route.",
            "A lock icon on a handset is not a packet capture.",
            "When you must prove media, capture on the gateway and redact the keys before the file leaves the lab.",
        ],
        "Seeing SRTP in the SDP and concluding the carrier leg is also encrypted. The carrier leg is a separate offer.",
        [
            "Place a lab call that leaves via the Local Gateway.",
            "On the Webex-facing dial-peer, note whether the offer is SRTP.",
            "On the carrier-facing dial-peer, note the offer separately.",
            "Write one sentence: which leg is SRTP, and which identifier is on that leg.",
        ],
        [
            ("What does RFC 3711 define?", "SRTP, the secure profile for RTP."),
            ("Does SRTP change the IP in the SDP connection line?", "No. Routing still has to deliver packets to that address."),
            ("Why can one call be encrypted on only one side of CUBE?", "CUBE is a B2BUA. Each leg has its own offer and answer."),
            ("What do you redact before sharing a capture?", "Keys, tokens, and any real phone numbers. The campus uses synthetic examples."),
        ],
        ("RFC 3711", RFC3711),
        ["Webex app", "Webex Calling", "Local Gateway"],
    ))
    add(topic(
        "wx-dial-plan-location", "Location dial plans", "How a site is allowed to dial",
        "The location dial plan decides which digits a person in that site may send, and how those digits are normalized before they hit the PSTN connection.",
        [
            "Internal extension length is a location choice. Do not assume four digits.",
            "Outbound national and international permissions are separate from the extension pattern.",
            "A steering digit you add in Hub must be stripped before the carrier, or the carrier rejects the request.",
            "Write the normalized E.164 form next to the digits the user dialed.",
        ],
        "Testing only the extension pattern and calling the PSTN dial plan done.",
        [
            "Pick a lab extension length and a lab national pattern.",
            "Dial the extension. Record that the gateway was not required.",
            "Dial a national lab number. Record the digits Hub handed the gateway.",
            "If a prefix appears, show the translation that removes it before the carrier.",
        ],
        [
            ("Where is extension length set for Webex Calling multi-tenant?", "On the location dial plan, not on a CUCM route pattern, unless you are on Dedicated Instance."),
            ("Why write both the dialed digits and the E.164 form?", "They diverge as soon as a prefix or a country code is added."),
            ("What happens if the steering digit reaches the carrier?", "The carrier may reject the number or route it somewhere unintended."),
            ("Which call proves the PSTN pattern?", "A call that selects the location's PSTN connection, not an on-net extension."),
        ],
        ("Webex Calling", WX),
        ["User", "Location dial plan", "Gateway"],
    ))
    add(topic(
        "wx-e164-numbers", "Numbers and E.164", "Assignment is not porting",
        "A number in Control Hub is an assignment. The carrier's record of who owns that DID is a different database. Both have to be true for inbound PSTN.",
        [
            "Store numbers in plus form in the design notes. The campus lab does the same for NANP and 011.",
            "An extension is not a DID. On-net success does not prove inbound PSTN.",
            "Unassigned numbers need an explicit treatment. Silence is a choice you should write down.",
            "Moving a DID between users is an assignment change plus a test call from outside.",
        ],
        "Declaring a port complete because Hub shows the digits. The carrier FOC is the other half.",
        [
            "List one lab DID, one lab extension, and the user each is assigned to.",
            "Call the extension from inside the org.",
            "Call the DID from outside the org, or write the carrier test you would schedule.",
            "Unassign the DID in the lab and record the treatment.",
        ],
        [
            ("What is the difference between an extension and a DID?", "An extension is on-net. A DID is a PSTN number the carrier must deliver."),
            ("What does plus-form mean here?", "A leading plus and the country code, so 011 or a national prefix has already been decided."),
            ("Why can Hub show a number that still fails inbound?", "The carrier may still point the number at the old platform."),
            ("What do you test after you move a DID between users?", "An inbound call from outside, not only the Hub assignment screen."),
        ],
        ("Webex Calling", WX),
        ["Carrier", "Control Hub", "User"],
    ))
    add(topic(
        "wx-outbound-permissions", "Outbound permissions", "Fraud is a routing problem",
        "Outbound calling permission is how Webex Calling stops a compromised account from dialing the world. It is a policy, and it needs an alert, not only a checkbox.",
        [
            "National, international, and premium destinations are different permissions.",
            "A location default and a user exception can disagree. Write which one wins.",
            "The canary account should not be the account with international permission.",
            "A sudden spike in international attempts is a counter worth paging on.",
        ],
        "Giving every user the same outbound class as the operator, then calling it simple.",
        [
            "Define two lab classes: internal only, and national.",
            "Place a user in internal only and attempt a national pattern. Record the rejection.",
            "Move the user to national and repeat. Record the path that is now selected.",
            "Name the counter or report you would alert on. Do not use a production account.",
        ],
        [
            ("Why are international and national different permissions?", "They have different fraud and cost blast radii."),
            ("Where can a user exception hide?", "On the user, overriding the location default. Check both."),
            ("What is a bad canary account?", "The account that is allowed to call every destination. A failure there does not prove a normal user works, and a success proves little about fraud control."),
            ("What do you page on?", "A spike in attempts your policy says should be blocked, not only completed calls."),
        ],
        ("Webex Calling", WX),
        ["User", "Permission", "PSTN"],
    ))
    add(topic(
        "wx-auto-attendant", "Auto attendants", "A menu is a destination",
        "A Webex Calling auto attendant answers, plays a menu, and transfers. It is not a contact-center queue and it is not Webex Contact Center.",
        [
            "The attendant has a number or extension and business hours.",
            "Each digit maps to a person, a hunt group, a call queue, or another menu.",
            "After-hours treatment is a separate path. Test it on purpose.",
            "The transfer is a new leg. Keep the original call id and the transferred call id.",
        ],
        "Calling the auto attendant a Webex Contact Center flow. The products do not share a script or a report.",
        [
            "Build a two-option lab menu: one person, one hunt group.",
            "Call during the open schedule and press each digit.",
            "Force the closed schedule and record the treatment.",
            "Write both call ids if the transfer creates a new leg.",
        ],
        [
            ("Is a Webex Calling auto attendant Webex Contact Center?", "No. Contact Center is a separate product."),
            ("What must you test besides the happy digit?", "The closed-hours path."),
            ("Why keep two call ids on a transfer?", "The answering leg and the transferred leg are different hops."),
            ("What is a menu item allowed to target?", "A person, a group, a queue, or another menu, as the current Hub feature allows."),
        ],
        ("Webex Calling", WX),
        ["Caller", "Auto attendant", "Target"],
    ))
    add(topic(
        "wx-hunt-group", "Hunt groups", "Who rings, and in what order",
        "A hunt group rings a set of people in an order you choose. It is not a queue with announced wait, and it is not a shared line.",
        [
            "Order matters: simultaneous, sequential, or the mode Hub currently offers. Write the mode you configured.",
            "A member who is available on a mobile client may answer before the desk you expected.",
            "No-answer forwarding on a member can steal the hunt. Check member forwarding.",
            "The pilot number is what you call. Member extensions are not the pilot.",
        ],
        "Debugging a hunt group by calling a member directly. That bypasses the group.",
        [
            "Create a lab hunt group with two members and a sequential order.",
            "Call the pilot. Confirm which member rings first.",
            "Decline on the first member and confirm the second rings.",
            "Turn on forwarding on one member and record whether the hunt still behaves.",
        ],
        [
            ("What number do you dial to test the group?", "The pilot, not a member extension."),
            ("How can one member's forwarding break the group?", "The hunt follows that member's forward instead of the next member."),
            ("Is a hunt group a call queue?", "No. A queue holds callers. A hunt rings members."),
            ("Why name the ring mode in the ticket?", "Simultaneous and sequential failures look different."),
        ],
        ("Webex Calling", WX),
        ["Caller", "Hunt group", "Member"],
    ))
    add(topic(
        "wx-call-queue-wx", "Webex Calling call queues", "Wait is a feature, not a contact center",
        "A Webex Calling call queue holds callers and rings agents who have joined the queue. It is still not Webex Contact Center. Reports, skills, and screen pop do not come from this object.",
        [
            "Agents join and leave. A user who exists but has not joined does not ring.",
            "Queue size and the overflow destination are the safety valve.",
            "Music or ringback while waiting is a setting. Silence usually means you did not choose one.",
            "Overflow and timeout are different timers. Test both.",
        ],
        "Staffing a Webex Calling queue as if it were an ICM precision queue.",
        [
            "Create a lab queue with two agents and a small overflow.",
            "Join one agent and call the queue. Record who rings.",
            "Leave the queue with that agent and call again.",
            "Fill the queue or expire the timeout and record the overflow destination.",
        ],
        [
            ("Does a Calling queue replace Webex Contact Center?", "No."),
            ("Why might an assigned agent not ring?", "They have not joined the queue, or their client is not available."),
            ("What is the difference between timeout and overflow?", "Timeout is how long one caller waits. Overflow is what happens when the queue cannot take another caller."),
            ("What do you record in the evidence note?", "Queue pilot, agent join state, and the call id."),
        ],
        ("Webex Calling", WX),
        ["Caller", "Call queue", "Agent"],
    ))
    add(topic(
        "wx-voicemail", "Voicemail", "The mailbox is not the no-answer timer",
        "Webex Calling voicemail answers when the no-answer or busy treatment says so. The mailbox, the greeting, and the notification are three settings.",
        [
            "No-answer seconds decide when the mailbox takes the call. The mailbox does not invent that timer.",
            "Message waiting indication has to reach the device you think the user watches.",
            "Transcription, if you enable it, is a feature with its own privacy note.",
            "A forwarded call that hits voicemail may show the forwarder's identity. Test it.",
        ],
        "Assuming voicemail failed because the phone rang forever. The no-answer timer was never set to divert.",
        [
            "Set a short lab no-answer timer on one user.",
            "Call them, decline to answer, and confirm the mailbox takes the call.",
            "Leave a message and confirm the waiting indicator on the device you named.",
            "Forward that user to a second user and see which mailbox answers.",
        ],
        [
            ("What setting actually sends a call to voicemail?", "The no-answer or busy treatment, including its timer."),
            ("Why can the lamp stay dark after a message?", "Indication is a separate path from the message store."),
            ("What do you test on a forwarded call?", "Which mailbox answered, and which identity the caller heard."),
            ("Where do you read that a message exists?", "The user's voicemail portal or the device indicator, not only the call history."),
        ],
        ("Webex Calling", WX),
        ["Caller", "User", "Voicemail"],
    ))
    add(topic(
        "wx-call-forward", "Call forward and simultaneous ring", "A second destination is a second leg",
        "Call forward and simultaneous ring send the call somewhere else. That somewhere else has its own permissions, its own voicemail, and its own failure.",
        [
            "Always, busy, and no-answer are different forwards.",
            "Simultaneous ring is not forward. Both destinations are offered.",
            "A forward to a PSTN number consumes outbound permission and a trunk.",
            "Loops happen when A forwards to B and B forwards to A. Hub may break the loop. Do not assume the timer.",
        ],
        "Testing forward-always by calling from the forwarded phone itself.",
        [
            "Set no-answer forward to a second lab user.",
            "Call from a third endpoint and wait out the timer.",
            "Switch to simultaneous ring and record which endpoint answers.",
            "Remove the forward and confirm the original user rings again.",
        ],
        [
            ("How is simultaneous ring different from forward-always?", "Simultaneous ring offers both. Forward-always does not offer the original destination."),
            ("Why can a forward to PSTN fail when on-net forward works?", "The PSTN leg needs permission and a working connection."),
            ("What is a forward loop?", "Two destinations that send the call to each other."),
            ("Which call is a fair test?", "A call from a third endpoint, not from the phone you just configured."),
        ],
        ("Webex Calling", WX),
        ["Caller", "User", "Target"],
    ))
    add(topic(
        "wx-shared-line", "Shared lines", "Appearance is not a hunt group",
        "A shared line puts the same number on more than one device. Any of those devices can answer. It does not hunt, and it does not queue.",
        [
            "Privacy and barge, if you enable them, are explicit features.",
            "A shared line on a workspace phone and on a user's app will both ring. That surprises people.",
            "Do not use a shared line when you wanted a hunt pilot.",
            "The call id is still one inbound call offered to multiple appearances.",
        ],
        "Building a small help desk as a shared line and then asking why there is no queue statistics.",
        [
            "Assign one lab number to two devices.",
            "Call it and answer on the second device.",
            "Confirm the first device shows the line in use.",
            "Write the sentence that distinguishes this from a hunt group.",
        ],
        [
            ("What rings when a shared line is called?", "Every device that has that appearance."),
            ("Does a shared line produce queue reports?", "No."),
            ("When would you choose a hunt group instead?", "When you want an ordered or simultaneous hunt of people, with a pilot that is not their personal line."),
            ("What should you tell the user who also has the line on the app?", "The app will ring too, unless you remove that appearance."),
        ],
        ("Webex Calling", WX),
        ["Caller", "Shared line", "Second device"],
    ))
    add(topic(
        "wx-call-park", "Call park", "The orbit is a number you must retrieve",
        "Call park places an active call on an orbit so someone else can retrieve it. If nobody retrieves it, the recall timer sends it back.",
        [
            "Park and retrieve are two actions with two different users in the usual test.",
            "The orbit number is not the user's extension.",
            "Recall is the safety path. Test it by waiting.",
            "A parked call still holds a media resource or a leg. It is not free.",
        ],
        "Hanging up to 'park' the call. That is a disconnect.",
        [
            "Answer a lab call and park it. Record the orbit.",
            "From a second endpoint, retrieve that orbit.",
            "Park again and let the recall timer fire. Record where the call returns.",
            "Write the orbit range your location uses.",
        ],
        [
            ("What is an orbit?", "The number that holds the parked call."),
            ("What happens if nobody retrieves it?", "Recall returns the call when the timer expires."),
            ("Why is hangup not park?", "Hangup sends BYE. Park keeps the call up."),
            ("Why does park still matter for capacity?", "The leg stays up until retrieve or recall."),
        ],
        ("Webex Calling", WX),
        ["User", "Park orbit", "Retriever"],
    ))
    add(topic(
        "wx-moh", "Music on hold", "Hold is a media change",
        "Music on hold replaces the call's media while the user holds. The far end should hear the source you selected, not silence and not the caller's own ringback.",
        [
            "Hold is a signaling event plus a new media source.",
            "The file or stream you uploaded is the source. The default may be silence.",
            "A gateway in the path can renegotiate. One-way hold audio is still a media problem.",
            "Do not upload music you do not have the rights to play. The campus does not ship a music file.",
        ],
        "Judging hold by the holder's own earpiece. The far end is the one who must hear it.",
        [
            "Place a lab call between two endpoints.",
            "Hold on one side. Ask the other side what they hear, or record the RTP source address change.",
            "Resume and confirm the original media returns.",
            "If a gateway is in the path, repeat the hold and watch for a re-INVITE.",
        ],
        [
            ("Who must hear music on hold?", "The party who was put on hold, not the person who pressed hold."),
            ("What signaling usually accompanies hold?", "A re-INVITE or an UPDATE that changes the media, depending on the leg."),
            ("Why can CUBE make hold look like one-way audio?", "The renegotiated stream toward the carrier may be blocked or not started."),
            ("What should you not upload as a test file?", "Commercial music you do not have rights to use."),
        ],
        ("RFC 3261", RFC3261),
        ["Holder", "Webex Calling", "Far end"],
    ))
    add(topic(
        "wx-mpp-registration", "MPP phones", "The device is a Control Hub object",
        "An MPP phone registers to Webex Calling as a device you claimed or assigned in Control Hub. Firmware channel and the user's line are separate.",
        [
            "A factory phone needs the onboarding path the current document describes. Do not invent a TFTP server from CUCM.",
            "The line on the phone is the user or workspace you assigned.",
            "Firmware is a channel. A phone on the wrong channel misses features and fixes.",
            "The phone can be up on the network and still unregistered to calling.",
        ],
        "Pointing an MPP phone at a CUCM TFTP server because that is how the last fleet worked.",
        [
            "In the lab notes, write the claim method you are allowed to use. Do not put a real activation code in a screenshot.",
            "Assign one line and confirm the phone shows registered in Hub.",
            "Place one on-net call.",
            "Record the firmware channel name without copying a serial number into the public notes.",
        ],
        [
            ("Is CUCM TFTP how an MPP phone reaches Webex Calling?", "No. Onboarding is a Control Hub device flow."),
            ("What is the difference between the phone and the line?", "The device registers. The line is the user or workspace assigned to it."),
            ("Why record the firmware channel?", "Behavior is channel-specific. A ticket without it cannot be matched to release notes."),
            ("What is a weak proof of registration?", "Link light on the switch. Registration is a Hub device state."),
        ],
        ("Webex Calling", WX),
        ["MPP phone", "Control Hub", "Webex Calling"],
    ))
    add(topic(
        "wx-webex-app", "Webex App calling", "The soft client is still a device",
        "Webex App places and receives Webex Calling calls. It is a device with its own network path, often a VPN or a home router, and it still uses the user's number.",
        [
            "The app and a desk phone can both be registered. Know which one you called.",
            "Media from the app uses the Webex media path. A VPN that excludes that path looks like one-way audio.",
            "Emergency calling from a soft client depends on the location you configured and tested, not on the app's guess.",
            "Sign-out is not a device delete. The user object remains.",
        ],
        "Blaming the Local Gateway for an app call that never left the cloud PSTN.",
        [
            "Register the app as the lab user.",
            "Call an on-net extension and record which client answered.",
            "If you have a desk phone on the same user, call again and see which endpoint rings.",
            "Write the network the app was on. Home, VPN, and office are different evidence.",
        ],
        [
            ("Can the app and a desk phone both ring?", "Yes, if both are assigned to the user or the line."),
            ("Why does VPN matter?", "Media to Webex can be hairpinned or dropped by a tunnel that does not allow it."),
            ("Does signing out delete the user?", "No."),
            ("What location evidence do you want for an app emergency test?", "The emergency address that was sent, and the test desk's reading of it."),
        ],
        ("Webex Calling", WX),
        ["Webex App", "Webex Calling", "Desk phone"],
    ))
    add(topic(
        "wx-hot-desking", "Hot desking", "The phone is a workplace, the user is a guest",
        "Hot desking lets a person sign into a shared phone. The calls belong to the signed-in user for that session, not to the last person who sat there.",
        [
            "The device stays. The line session changes.",
            "Sign-out must be part of the test, or the next person inherits the line.",
            "Emergency location should follow the device's site, which you confirm rather than assume.",
            "A failed sign-in leaves the phone as a workspace with whatever line it had.",
        ],
        "Resetting the phone because the previous user's calls still appear. You wanted sign-out.",
        [
            "Sign a lab user into a shared device.",
            "Place one call and confirm Hub attributes it to that user.",
            "Sign out and confirm the next call does not use that user.",
            "Write the site emergency address you expect this device to send.",
        ],
        [
            ("What changes when a user signs into a hot desk?", "The line session. The device stays."),
            ("What is the dangerous leftover?", "A session that was never signed out."),
            ("Whose emergency location should you verify?", "The device's site, with a test, not a hope."),
            ("Is a factory reset the first troubleshooting step?", "No. Sign-out and the Hub session are the first evidence."),
        ],
        ("Webex Calling", WX),
        ["User", "Shared phone", "Webex Calling"],
    ))
    add(topic(
        "wx-virtual-line", "Virtual lines", "A number without a new human",
        "A virtual line is a calling identity you can put on a device or an app without creating a second full person. It is still a number with permissions and voicemail.",
        [
            "The line has its own extension or DID.",
            "Assigning it to a phone adds an appearance. It does not create a hunt group.",
            "Outbound identity on that line should be tested. Caller ID surprises are common.",
            "Voicemail for the virtual line is not the user's personal mailbox unless you pointed it there.",
        ],
        "Using a virtual line as a contact-center agent login.",
        [
            "Create one lab virtual line and assign it as a second appearance.",
            "Call the virtual line's extension and answer on the device.",
            "Place an outbound call from that appearance and record the caller identity.",
            "Confirm which mailbox answers on no-answer.",
        ],
        [
            ("Does a virtual line require a second employee object?", "No. That is the point. It is still a calling identity."),
            ("What do you test on outbound?", "The caller ID the far end sees."),
            ("Is the personal mailbox automatic?", "No. Check where no-answer sends the virtual line."),
            ("What is it not?", "A hunt group, a queue, or a contact-center agent."),
        ],
        ("Webex Calling", WX),
        ["Caller", "Virtual line", "Device"],
    ))
    add(topic(
        "wx-recording", "Call recording", "The connector is a second destination",
        "Webex Calling recording sends a copy of the call to a recording provider. The provider, the announcement, and the storage are part of the design, not a checkbox at the end.",
        [
            "User, location, or compliance scope changes who is recorded. Write the scope.",
            "An announcement may be required by policy. The product setting is not legal advice.",
            "The recording id must join to the Webex call id or you cannot find the file.",
            "A failed recorder should have a known behavior: fail open or fail closed. Write which one you chose.",
        ],
        "Assuming the call history row is the recording. History is not the audio file.",
        [
            "In the lab notes, name the recorder as a box on the diagram.",
            "Place a test call you are allowed to record. Do not record a real customer.",
            "Find the file or the test event and write the id that joins it to the call.",
            "State fail open or fail closed for a recorder outage.",
        ],
        [
            ("Is call history the same as the recording?", "No."),
            ("What must join the file to the call?", "A shared id. Write which field."),
            ("Why write fail open or fail closed?", "A recorder outage either blocks calls or allows unrecorded calls. Both are decisions."),
            ("What should a lab never record?", "A real customer or anyone who has not agreed to a test."),
        ],
        ("Webex Calling", WX),
        ["User", "Webex Calling", "Recorder"],
    ))
    add(topic(
        "wx-emergency-location", "Emergency locations", "An address a responder can use",
        "Emergency calling uses the location you configured, not the building nickname in a spreadsheet. Webex Calling locations and emergency addresses have to be tested.",
        [
            "A dispatchable location is a civic address, not a floor nickname, unless the provider accepts that extra detail.",
            "Soft clients and desk phones can send different location evidence. Test the one the user actually has.",
            "On-site notification is a separate feature from the call to the PSAP.",
            "Use the provider's test number. Do not place a real emergency call as a drill.",
        ],
        "Calling a teammate and calling that an emergency test.",
        [
            "Write the lab address you configured. Use a lab address, not a home address, in shared notes.",
            "Identify the test number your provider documents.",
            "Place the test from the device type you are certifying.",
            "Record what the test desk showed, and who on site would have been notified.",
        ],
        [
            ("What is a dispatchable location?", "An address a responder can use."),
            ("Why is a teammate call not a test?", "It does not reach the emergency provider or the test desk."),
            ("What else do you prove besides the outbound call?", "On-site notification, if the design includes it."),
            ("Do the app and the desk phone share evidence automatically?", "Do not assume it. Test the client the user will have."),
        ],
        ("Webex Calling", WX),
        ["Device", "Webex Calling", "Emergency provider"],
    ))
    add(topic(
        "wx-survivability", "Site survivability", "What still works when the cloud path fails",
        "Survivability is the feature set that remains when a site loses its path to Webex Calling. It is release-specific. Write the matrix instead of saying the phones still work.",
        [
            "List the calls that still complete: local PSTN, internal, emergency.",
            "List the calls that do not: anything that needed the cloud.",
            "The gateway configuration for survivability is not the normal Local Gateway dial-peer.",
            "A test is a planned disconnect of the cloud path in a lab, not an accident in production.",
        ],
        "Quoting a survivability behavior from a different release or from CUCM SRST without checking the Webex document.",
        [
            "Make a three-row matrix: call type, works in survivability, evidence.",
            "In a lab, identify the command or cable that simulates the cloud path loss. Do not do this on a live DID.",
            "Place the emergency-path test your provider allows.",
            "Restore the path and confirm the canary uses the cloud again.",
        ],
        [
            ("Is survivability the same as CUCM SRST?", "No. Read the Webex survivability document for the release you run."),
            ("What belongs in the matrix?", "Which call types still complete, and how you proved it."),
            ("Why is a production cable pull a bad test?", "The blast radius is the site. Use a lab."),
            ("What do you prove after restoration?", "The canary uses the cloud path again, not the survivability path."),
        ],
        ("Cisco design zone", DESIGN),
        ["Phone", "Survivable gateway", "Webex Calling"],
    ))
    add(topic(
        "wx-certificate-overlap", "Certificate overlap", "Rotate without a registration black hole",
        "Replacing a Local Gateway certificate by deleting the old one first drops the TLS session. Overlap means the new certificate is trusted before the old one is removed.",
        [
            "Install the new certificate on the gateway and in any trust store the guide names.",
            "Confirm the new chain validates. A hostname mismatch is the usual failure.",
            "Only then remove the old certificate.",
            "The canary is a new call after the removal, not only a show command.",
        ],
        "Scheduling the certificate change in the same minute as a dial-plan change. You will not know which one broke the canary.",
        [
            "Write the overlap order on one page.",
            "In a lab, note the trustpoint name. Do not export the private key into the notes.",
            "Place a canary before the change and after the old cert is gone.",
            "If it fails, save the TLS error text and change nothing else.",
        ],
        [
            ("What does overlap mean?", "The new certificate works before the old one is removed."),
            ("What is the usual TLS failure?", "A name on the certificate that is not the name Webex expects."),
            ("Why not combine the change with a dial-plan edit?", "You lose the single-variable test."),
            ("What is the canary?", "A new call after the old certificate is gone."),
        ],
        ("Webex Calling ports", PORT),
        ["Local Gateway", "Webex Calling", "Canary"],
    ))
    add(topic(
        "wx-cube-dial-peers", "CUBE dial-peers for the Local Gateway", "Incoming and outgoing are different peers",
        "CUBE selects an incoming dial-peer for the leg from Webex and an outgoing dial-peer for the carrier, or the reverse. One peer rarely does both jobs well.",
        [
            "Bind signaling and media to the interface you mean.",
            "Translation profiles change digits. Show them in the ticket.",
            "Early offer and DTMF interworking are explicit. An MTP is a choice.",
            "The Webex-facing peer and the carrier-facing peer can use different transports.",
        ],
        "Debugging only the outgoing peer when the incoming peer matched a default and never hit your configuration.",
        [
            "Draw two dial-peers and label which leg each serves.",
            "Write the destination pattern or URI match for each. Use lab patterns.",
            "Place one call and record which peer CUBE selected, from the debug you are allowed to run in a lab.",
            "Change one translation and repeat the canary.",
        ],
        [
            ("Why two dial-peers?", "Incoming match and outgoing match are separate decisions."),
            ("What does bind change?", "The source address CUBE uses for that leg."),
            ("When do you involve an MTP?", "When the legs cannot agree on DTMF or early offer and you have decided to invoke one."),
            ("What is a default incoming peer?", "A peer CUBE uses when your specific match missed. It hides mistakes."),
        ],
        ("Cisco CUBE", CUBE),
        ["Webex Calling", "CUBE", "Carrier"],
    ))
    add(topic(
        "wx-directory-sync", "Directory sync", "The IdP is not the calling user",
        "Directory sync creates or updates people in the identity store. A calling user also needs a calling license and a number. Sync alone does not place a call.",
        [
            "Account enabled and calling enabled are different states.",
            "A deleted directory user may leave a number assigned. Check the number after offboarding.",
            "Attributes you map, especially the phone number, can fight a manual Hub edit.",
            "Test with a lab account in the directory, not with a privileged admin.",
        ],
        "Re-syncing the directory as a fix for a Local Gateway registration failure.",
        [
            "Name the attribute that becomes the Webex user.",
            "Enable calling on one lab user and assign a lab extension.",
            "Remove the extension and record whether the identity account remains.",
            "Write the offboarding order: number, device, then account.",
        ],
        [
            ("Does directory sync assign a calling number?", "Not by itself. Calling entitlement and number assignment are further steps."),
            ("What can a mapped phone attribute overwrite?", "A manual number edit in Hub, on the next sync."),
            ("Why is re-sync the wrong fix for a gateway?", "The gateway does not authenticate as a directory user."),
            ("What is the offboarding order?", "Release the number and the device, then the account, so the DID does not stay pointed at a deleted person."),
        ],
        ("Webex Calling", WX),
        ["Directory", "Control Hub", "User"],
    ))
    add(topic(
        "wx-analytics", "Calling analytics", "A tile is a query",
        "Control Hub calling analytics shows quality and completion for the org. A tile without the filter, the interval, and the call id is not evidence you can defend.",
        [
            "Quality metrics do not name the firewall rule that dropped RTP. They tell you to go look.",
            "A single bad call still has a call id. Open that call, not only the average.",
            "Compare the Hub time to the gateway log time before you join them.",
            "Export or screenshot the filter with the result.",
        ],
        "Declaring the network healthy because the org-wide MOS average is fine.",
        [
            "Open calling analytics on a lab org or a screenshot from a lab.",
            "Write the interval and the filter.",
            "Pick one call id and say which gateway log you would join it to.",
            "Note the clock source.",
        ],
        [
            ("What makes an analytics tile evidence?", "The filter, the interval, and a call id you can join."),
            ("Does a good average clear one site?", "No. Averages hide a site."),
            ("Why mention the clock?", "Hub and CUBE may not stamp in the same zone."),
            ("What does poor quality not tell you?", "Which hop dropped or delayed the packets. That is a capture."),
        ],
        ("Webex Calling", WX),
        ["User", "Control Hub", "Gateway log"],
    ))
    add(topic(
        "wx-one-way-audio", "One-way audio", "Signaling made it, media did not",
        "One-way audio means SIP completed and one RTP direction did not. The SDP connection address and the firewall are the first two facts, not a phone reset.",
        [
            "Write which party hears the other.",
            "Read the c= line and the port on the silent direction.",
            "A NAT that rewrites SIP but not the SDP produces exactly this symptom.",
            "SRTP does not change the diagnosis. You still need packets in both directions.",
        ],
        "Resetting the Local Gateway because the 200 OK looked slow.",
        [
            "Place a lab call with one silent direction, or describe a lab you can build with a closed ACL.",
            "Record the address in the SDP for the silent direction.",
            "Record whether packets arrived at that address.",
            "Change one ACL or route and repeat. Do not change the dial plan in the same step.",
        ],
        [
            ("What has already succeeded in one-way audio?", "SIP signaling, far enough to negotiate media."),
            ("Which SDP line names the address that must receive RTP?", "The connection line, c=."),
            ("How does NAT cause it?", "Signaling is rewritten and the media address inside SDP is not."),
            ("What is the wrong first action?", "A device reset or a second config change before the capture."),
        ],
        ("RFC 4566", RFC4566),
        ["Caller", "Local Gateway", "Callee"],
    ))
    add(topic(
        "wx-qos-marking", "QoS toward Webex", "Mark only at a trust boundary you own",
        "Webex media should be marked and queued on the network you operate. A marking the phone sets and the switch strips is not a policy.",
        [
            "Write the DSCP you intend and the interface that is allowed to set it.",
            "Re-marking at the WAN edge is a different policy. Say so.",
            "Bandwidth math still includes headers. G.711 at 20 ms is 80 kbit/s at layer 3.",
            "A speed test is not the voice class.",
        ],
        "Trusting the app's marking after a VPN encapsulate. The outer header is what the WAN sees.",
        [
            "Write the trusted interface for a lab site.",
            "State the DSCP for media and for signaling separately if your policy splits them.",
            "Calculate one G.711 call at layer 3 and with an 18-byte Ethernet header.",
            "Say what a VPN would do to that marking.",
        ],
        [
            ("Where is a marking trusted?", "On an interface you configured to trust it."),
            ("What is G.711 at 20 ms at layer 3?", "80 kbit/s, before Ethernet."),
            ("Why can a VPN hide the voice DSCP?", "The outer header is a different packet."),
            ("What document do you date for Webex media ranges?", "The current port reference, because QoS ACLs follow those ports."),
        ],
        ("Webex Calling ports", PORT),
        ["Phone", "Trusted switch", "WAN"],
    ))
    add(topic(
        "wx-number-cutover", "Number cutover", "Dual-run, then the carrier, then the canary",
        "Moving a DID to Webex Calling is a state change. Old platform, dual-run, and Webex-only are three states. The carrier FOC is not the same minute as your route change unless you planned that risk.",
        [
            "Write the state of the canary DID before the window.",
            "Inbound and outbound are separate tests.",
            "Voicemail, recording, and emergency move on their own checklists.",
            "The rollback owner puts the canary back and proves it with a call from outside.",
        ],
        "Deleting the number on the old platform before the first successful inbound call to Webex.",
        [
            "Pick one lab DID and write its state.",
            "List inbound test, outbound test, emergency test, and voicemail test as four lines.",
            "Name the rollback owner and the first command or carrier ticket they run.",
            "Do not schedule a real port in this exercise. The lab is the checklist.",
        ],
        [
            ("What are the three number states?", "Old platform, dual-run, and Webex-only."),
            ("Why split inbound and outbound tests?", "They depend on different carrier records and different routes."),
            ("What else moves besides the DID?", "Voicemail, recording, and emergency location."),
            ("What does rollback prove?", "An outside caller reaches the old destination again."),
        ],
        ("Cisco design zone", DESIGN),
        ["Old PBX", "Carrier", "Webex Calling"],
    ))
    add(topic(
        "wx-di-peering", "Dedicated Instance peering", "A cloud CUCM still has trunks",
        "Dedicated Instance peering connects that CUCM-class cloud to your network. It is not a multi-tenant location toggle. Trunks, regions, and the Local Gateway still exist in that design.",
        [
            "Name the peering type from the current DI document before you draw it.",
            "Call control is the DI cluster. Control Hub is still where you see the subscription, not every CUCM route pattern.",
            "A trunk from DI to CUBE is a SIP trunk with CUCM security profiles, not a registration to TCP 8934.",
            "Failure of the peering is a site event. Write the survivability story separately.",
        ],
        "Using the multi-tenant certificate-trunk port as the DI trunk port without reading the DI guide.",
        [
            "Draw DI, the peering, CUBE, and the carrier.",
            "Label which box is CUCM administration.",
            "Write the evidence for a trunk-down event: CUCM trunk status and a CUBE peer.",
            "State one thing you would not do: apply a Calling Plan checklist.",
        ],
        [
            ("Is Dedicated Instance multi-tenant Webex Calling?", "No."),
            ("Where do route patterns live in that architecture?", "On the DI call control, in the CUCM administration model."),
            ("What is the PSTN edge still allowed to be?", "A Local Gateway or the PSTN option the current DI design guide names."),
            ("What checklist do you leave on the shelf?", "The Calling Plan checklist. There is no customer gateway on that product, and DI is not that product."),
        ],
        ("Cisco Unified CM", CUCM),
        ["Dedicated Instance", "Peering", "CUBE"],
    ))
    add(topic(
        "wx-interview-traps", "Webex Calling interview traps", "Say the product before the port",
        "The interview fails when the port, the product, and the admin system get mixed. Start with the PSTN type, then the evidence.",
        [
            "Calling Plan, premises PSTN, and Dedicated Instance are three opening sentences.",
            "TCP 5062 and TCP 8934 belong to two trunk types. Say which.",
            "Webex Contact Center is not a tab inside the auto attendant.",
            "A 200 OK is not audio. Offer the capture you would take next.",
        ],
        "Answering 'how does Webex Calling work' with a CUCM route-pattern lecture and no location.",
        [
            "Set a timer for 60 seconds and answer: what is a Local Gateway?",
            "Set a timer for 60 seconds and answer: what is Calling Plan?",
            "Name the evidence for one-way audio in one sentence.",
            "Name the document you would open for ports, and admit you would check the date.",
        ],
        [
            ("What is the first distinction you draw?", "Calling Plan, premises Local Gateway, or Dedicated Instance."),
            ("Which ports match which trunk?", "Certificate trunk TCP 5062. Registration trunk TCP 8934."),
            ("What is Webex Contact Center relative to an auto attendant?", "A different product."),
            ("What do you capture after a 200 OK if the caller hears silence?", "RTP to the address in the SDP, on the silent direction."),
        ],
        ("Webex Calling ports", PORT),
        ["Candidate", "Diagram", "Evidence"],
    ))
    add(topic(
        "wx-capstone-quiz", "Webex Calling capstone", "Eight checks before you call the path done",
        "This quiz closes the Webex Calling path. Answer from the mechanism, then name the document you would re-read before production.",
        [
            "Locations select the PSTN connection.",
            "Certificate and registration trunks use different ports.",
            "Hub assignment and the carrier record are both required for a DID.",
            "Emergency, recording, and the canary are part of done, not follow-up work.",
        ],
        "Skipping the capstone because the earlier cards felt familiar. Familiar wording is not a trunk.",
        [
            "Answer all eight prompts before you open the card body.",
            "For each miss, write a LICC line: leg, id, counter, capture.",
            "Place one lab canary and attach its call id to the miss you care about most.",
            "Re-read the port reference and write the date.",
        ],
        [
            ("Which object selects Calling Plan versus a Local Gateway?", "The Webex Calling location."),
            ("What is TCP 5062?", "Signaling for a certificate-based Local Gateway."),
            ("What is TCP 8934?", "Signaling for a registration-based Local Gateway, and that session is reused."),
            ("Why is an on-net call a weak PSTN test?", "It can complete without the gateway or the carrier."),
            ("What joins a recording file to a call?", "A shared id you can show, not the fact that recording was enabled."),
            ("What is a dispatchable location?", "An address a responder can use, tested with the provider's test path."),
            ("Why overlap a certificate?", "So the new chain is trusted before the old certificate is removed."),
            ("What is Dedicated Instance not?", "It is not multi-tenant Webex Calling and not Webex Contact Center."),
        ],
        ("Webex Calling", WX),
        ["You", "Control Hub", "Local Gateway"],
    ))
    # Further lessons to clear 60 with the originals. Each stays specific.
    more = [
        ("wx-group-paging", "Group paging", "One-way audio on purpose",
         "Group paging is a one-way announcement to a set of phones. It is not an intercom conversation and it is not a hunt group.",
         ["Paging targets devices you listed, not everyone in the org.", "The speaker path is one-way. Do not debug it as a missing reverse RTP stream.", "Volume and do-not-disturb decide whether the page is heard.", "A page during a call has a defined behavior. Test it instead of assuming the call drops."],
         "Expecting the paged phone to talk back on the same leg.",
         ["Build a lab page group of two devices.", "Send a page and confirm the second device plays it.", "Answer a call on that device and send another page.", "Write whether the call survived."],
         [("Is paging a two-way call?", "No. It is a one-way announcement."), ("Who hears it?", "Devices in the page group that are allowed to play it."), ("Why is missing reverse audio not a fault?", "The feature has no reverse talk path."), ("What else do you test?", "A page while a call is already up.")],
         ("Webex Calling", WX), ["Pager", "Webex Calling", "Target phone"]),
        ("wx-ata-analog", "Analog through an ATA", "The ATA is the SIP device",
         "An analog phone or fax machine speaks to an ATA. The ATA is what Webex Calling registers. The analog pair is not a SIP leg.",
         ["Register the ATA in Control Hub, then test the analog port.", "Fax is delay and codec sensitive. G.711 is the usual lab choice and still not a promise.", "Hookflash features depend on the ATA, not on a SIP INFO story.", "A dead analog port can sit behind a registered ATA. Check both."],
         "Debugging SIP on the analog handset. It does not speak SIP.",
         ["Register a lab ATA.", "Place a call from the analog port.", "Confirm Hub shows the ATA, not an imaginary third device.", "If you test fax, use a lab machine and G.711, and record the result without calling it certified."],
         [("What registers to Webex?", "The ATA."), ("Does the analog phone have a Call-ID?", "No. The ATA's SIP leg does."), ("Why is fax picky?", "It wants a clean G.711 path and low delay. Packet loss ruins it."), ("What do you check when the port is dead but Hub is green?", "The analog pair, the port, and the ATA port status.")],
         ("Webex Calling", WX), ["Analog phone", "ATA", "Webex Calling"]),
        ("wx-dect", "DECT handsets", "The base is the device Hub sees",
         "A DECT deployment registers a base or the device model the current guide names. Handsets pair to that base. A missing handset is not always a SIP failure.",
         ["Pair the handset to the base before you debug calling.", "The SIP registration belongs to the DECT system, not to each handset's battery.", "Roaming between bases is a radio design. Coverage holes look like dropped calls.", "Emergency location follows the site of the base you planned, which you still test."],
         "Replacing a SIP trunk because a handset lost radio at the edge of the building.",
         ["Pair one lab handset.", "Place a call at the base, then at the edge of coverage.", "Record whether the failure was SIP or a radio drop.", "Write the site address you expect for emergency."],
         [("What does Hub register?", "The DECT device the guide tells you to claim, typically the base system."), ("What does a coverage hole look like?", "Audio dies as the handset moves, while the base stays registered."), ("Is roaming a dial-plan problem?", "No. It is radio and base placement."), ("What emergency fact do you test?", "The location associated with that site.")],
         ("Webex Calling", WX), ["Handset", "DECT base", "Webex Calling"]),
        ("wx-webex-go", "Webex Go", "The mobile number and the app identity",
         "Webex Go places the user's calling identity on a supported mobile line. It is not the same as the Webex App on Wi-Fi, and the mobile carrier is now part of the leg.",
         ["The user still exists in Control Hub.", "Outbound caller identity should be tested. Mobile CLID and Webex CLID can disagree.", "Coverage and the carrier are failure domains the LAN team does not own.", "Emergency calling follows the mobile path as the current Webex Go document describes. Test, do not invent."],
         "Debugging Webex Go as if it were an MPP phone on PoE.",
         ["Read the current Webex Go requirements and write the date.", "Place one lab call and record which network it used.", "Record the caller ID the far end saw.", "State one failure that belongs to the mobile carrier."],
         [("Is Webex Go just the app on Wi-Fi?", "No. It uses a supported mobile line."), ("What can disagree?", "The mobile caller ID and the Webex caller ID."), ("Who owns coverage?", "The mobile carrier, not the office switch."), ("What do you re-read before a design claim?", "The current Webex Go article, dated.")],
         ("Webex Calling", WX), ["Mobile", "Webex Go", "Far end"]),
        ("wx-sso", "Single sign-on", "SSO lets you in. It does not assign a number.",
         "SSO authenticates the admin or the user. Calling still needs a license, a location, and a number. An IdP outage locks the login. It does not unregister a phone that is already registered.",
         ["Admin SSO and user SSO can be different apps.", "A failed login is not a failed Local Gateway.", "Certificate expiry on the IdP is a calendar item.", "Break-glass admin access must not depend on the IdP you are testing."],
         "Restarting CUBE because an admin cannot sign in to Control Hub.",
         ["Name the IdP and the break-glass admin path.", "Sign in with SSO in a lab and confirm calling still needs a separate number assignment.", "Write what stays up if the IdP is down: already-registered devices.", "Write what stops: new admin logins."],
         [("Does SSO assign DIDs?", "No."), ("Does an IdP outage unregister phones by itself?", "No. It blocks new logins that depend on it."), ("Why keep a break-glass admin?", "So you can still work when the IdP is the fault."), ("What do you not restart first?", "The Local Gateway.")],
         ("Webex Calling", WX), ["User", "Identity provider", "Control Hub"]),
        ("wx-bulk-csv", "Bulk CSV", "A spreadsheet is a change window",
         "Control Hub CSV import creates or changes many users at once. A wrong column is a wide blast radius. Dry-run the file on a lab row before the real file.",
         ["Keep a copy of the file you imported and the result report.", "Phone numbers in the file must already be in the org inventory.", "Do not include real customer numbers in a sample you commit to a repo.", "One lab row proves the column map. Then you may run the rest."],
         "Importing the production file because the header 'looked right'.",
         ["Build a two-row lab CSV with synthetic extensions.", "Import it and read the error report.", "Fix one column and import again.", "Write the rollback for a bad row: which user you delete or edit."],
         [("Why is a CSV a change window?", "It writes many objects. A bad column touches all of them."), ("What proves the column map?", "One lab row and the result report."), ("What must already exist?", "The numbers, in the org inventory."), ("What never goes in a public sample?", "Real DIDs or real people's numbers.")],
         ("Webex Calling", WX), ["CSV", "Control Hub", "Lab user"]),
        ("wx-caller-id", "Caller ID and privacy", "What the far end is allowed to see",
         "Outbound caller ID is a policy. Privacy, the location's number, and the user's DID can each be the identity you send. The far end's display is the proof.",
         ["Write the identity you intend: user DID, location main, or restricted.", "A gateway translation can overwrite Hub. Check both.", "Privacy is not the same as sending the main number.", "Test from outside. An on-net call may show an extension instead."],
         "Trusting the Hub preview and never calling a phone you control outside the org.",
         ["Set a lab user to present a specific lab DID.", "Call a second lab endpoint on the PSTN path and record the displayed number.", "Enable restriction and record the change.", "If CUBE rewrites From or PAI, write that rule down."],
         [("What is the proof of caller ID?", "What the far end displayed, not the admin preview alone."), ("Where else can the identity change?", "On a CUBE translation of From, PAI, or RPID."), ("Is privacy the same as sending the main number?", "No. Privacy restricts the identity. The main number is a specific identity."), ("Which call is a weak test?", "An on-net extension call.")],
         ("RFC 3261", RFC3261), ["User", "Webex Calling", "Far end"]),
        ("wx-workspace-devices", "Workspace devices", "A room is not a person",
         "A workspace has a device and optional calling. Room phones and collaboration devices live here. They should not be fake users named after the room unless the design says so.",
         ["The workspace has its own calendar and device identity.", "Calling on a workspace uses a number you assign to that place.", "Hot desking and a workspace device solve different problems.", "Emergency location should be the room's site, tested."],
         "Creating a licensed user called Conference Room A and losing track of who owns the mailbox.",
         ["Create a lab workspace and assign a device identity on paper.", "Assign a lab extension to the workspace.", "Call it and confirm the call history shows the workspace, not a human.", "Write the emergency site for that room."],
         [("Is a workspace a user?", "No. It is a place with a device."), ("Who owns its number?", "The workspace, if you assigned calling there."), ("When do you use hot desking instead?", "When a person must sign into a shared phone as themselves."), ("What location do you test?", "The room's site.")],
         ("Webex Calling", WX), ["Caller", "Workspace", "Room device"]),
        ("wx-redundancy-lgw", "Two Local Gateways", "Preference is a dial plan",
         "Two Local Gateways are useful only if you know which one is preferred, how fast the second is tried, and how inbound DID lands on both.",
         ["Outbound preference is explicit. Equal cost without a rule is not a design.", "Inbound DID has to be accepted on the gateway that receives it.", "Registration or certificate state is per gateway.", "Test the failure by idling one gateway in a lab, not by hoping."],
         "Adding a second CUBE and assuming Hub will use it because it exists.",
         ["Draw primary and secondary and the preference.", "Place a canary on the primary.", "Take the primary out of service in the lab and repeat the canary.", "Restore it and confirm preference returns."],
         [("Does a second gateway get traffic automatically?", "No. Preference and inbound routing have to name it."), ("What is per gateway?", "Its registration or certificate session."), ("How do you test failover?", "Idle the primary in a lab and place the canary."), ("What do you prove on the way back?", "The primary is preferred again.")],
         ("Cisco CUBE", CUBE), ["Webex Calling", "Primary gateway", "Secondary gateway"]),
        ("wx-international", "International dialing", "Permissions, digits, and fraud",
         "International dialing needs a permission, a digit transformation to E.164, and a fraud control. A successful lab call to a test number is not permission for every user.",
         ["The location dial plan defines who may dial the international pattern.", "011 or a plus prefix must become the form the PSTN connection expects.", "Premium destinations deserve a tighter class than ordinary international.", "Alert on attempts, not only on connected minutes."],
         "Enabling international on the location default because one executive asked.",
         ["Define a lab international pattern using a documentation range, not a real toll number.", "Deny it for one user and confirm the rejection.", "Allow it for a second lab user and confirm the digits the gateway sees.", "Name the alert."],
         [("What three things does international need?", "Permission, digit form, and a fraud control."), ("Why not enable it on the default?", "Every user in the location inherits it."), ("What should you alert on?", "Attempts your policy says are forbidden, not only completed calls."), ("Which lab number is acceptable?", "A synthetic or documentation-range number, not a real toll destination.")],
         ("Webex Calling", WX), ["User", "Dial plan", "Gateway"]),
        ("wx-transfer", "Transfer and consult", "Two calls, then one",
         "A consult transfer is two calls that become one. A blind transfer is a single redirection. The call ids change. Write which flavor you tested.",
         ["Consult uses a second call before the first is transferred.", "Blind transfer moves the original caller without a consult.", "A transfer to voicemail is a destination, not a failure.", "Gateway transfers can be a SIP REFER or a hairpin. Know which one CUBE is doing."],
         "Counting a consult as a dropped call because the first Call-ID ended.",
         ["Place a lab call and blind-transfer it to a second user.", "Repeat as a consult transfer.", "Record the call ids before and after.", "If the path includes CUBE, note whether you saw REFER."],
         [("What is the difference between blind and consult?", "Consult starts a second call first. Blind redirects immediately."), ("Why did the first Call-ID end?", "The transfer completed. That can be success."), ("What is REFER?", "A SIP method that asks the other leg to call the target directly."), ("What do you record?", "Both call ids and the transfer type.")],
         ("RFC 3261", RFC3261), ["Caller", "Transferrer", "Target"]),
        ("wx-dnd", "Do not disturb", "A client state, not a trunk state",
         "Do not disturb stops the endpoint from ringing. The trunk can still be healthy. The call follows the no-answer or busy treatment you set for that state.",
         ["DND is per user or per device, depending on the client.", "A hunt group member in DND is a member who will not answer.", "The caller should hear the treatment you configured, not dead air, if you set one.", "Clearing DND is the fix. Resetting the gateway is not."],
         "Opening a carrier ticket because one user pressed DND.",
         ["Enable DND on one lab user.", "Call them and record the treatment.", "Put that user in a hunt group and call the pilot.", "Clear DND and confirm ringing returns."],
         [("Is DND a trunk failure?", "No."), ("What should the caller experience?", "The busy or no-answer treatment you configured."), ("How does DND affect a hunt group?", "That member does not answer."), ("What is the fix?", "Clear DND, then retest.")],
         ("Webex Calling", WX), ["Caller", "User", "Treatment"]),
        ("wx-monitoring", "Monitoring the gateway", "Registration is a counter",
         "Monitor the thing that fails. For a registration trunk that is the registration. For a certificate trunk that is the TLS session and call success. CPU on CUBE is not a substitute.",
         ["Alert when the registration or the TLS session drops, not only when a human complains.", "A canary call on an interval catches a trunk that is up and routing nowhere.", "Log time must be comparable to Control Hub time.", "Do not page on a single probed packet loss unless you meant to."],
         "Graphing interface bandwidth and calling the trunk monitored.",
         ["Write the counter for your trunk type.", "Write the canary and how often a lab would run it.", "Write the clock you will compare.", "Name one graph you will not use as proof."],
         [("What do you alert on for a registration trunk?", "Loss of the registration."), ("What do you alert on for a certificate trunk?", "TLS session failure and failed calls."), ("Why add a canary?", "A session can be up while digit analysis sends calls nowhere."), ("What is a weak graph?", "Raw interface bandwidth, with no call success counter.")],
         ("Webex Calling ports", PORT), ["Monitor", "Local Gateway", "Canary"]),
        ("wx-migration-parity", "Feature parity before cutover", "The list is the scope",
         "A Webex Calling migration without a parity list drops voicemail, paging, night service, and recording on the weekend. Write the list and mark each item keep, change, or drop.",
         ["Every keep item needs a destination object in Hub or on the gateway.", "Drop items need a person who agreed.", "Emergency and recording cannot be silent drop items.", "The canary user should exercise one keep item from each row that matters."],
         "Migrating the DID and calling the feature list a phase two with no owner.",
         ["Make a ten-line parity list from a fictional PBX.", "Mark keep, change, or drop.", "For two keep items, name the Webex object.", "Name the person who accepts each drop. Use role names, not personal names."],
         [("What is a parity list?", "Features you will keep, change, or explicitly drop."), ("What cannot be a silent drop?", "Emergency calling and any recording obligation you already have."), ("What does the canary exercise?", "One kept feature from each row you claim."), ("When is phase two allowed?", "When a named role owns it and the current users are not surprised.")],
         ("Cisco design zone", DESIGN), ["Old PBX", "Parity list", "Webex Calling"]),
        ("wx-lab-canary", "The Webex canary", "One DID you can call from outside",
         "A Webex Calling canary is a DID you call from a network you do not operate, plus an outbound call to a lab destination. It is the last step of every change, not a project by itself.",
         ["Inbound proves the carrier and Hub assignment.", "Outbound proves permission and the PSTN connection.", "The emergency test is separate and uses the provider's test number.", "Record the call id. A human saying it worked is not the record."],
         "Using an on-net extension as the only canary.",
         ["Choose a lab DID and a lab outbound target.", "Call inbound from outside the org.", "Call outbound from the canary user.", "File the two call ids next to the change you just made."],
         [("Why must the inbound canary come from outside?", "On-net calls skip the carrier."), ("What does outbound prove?", "Permission and the PSTN connection."), ("Where does the emergency test fit?", "It is its own call, to the provider's test number."), ("What do you file?", "The call ids, not a verbal okay.")],
         ("Webex Calling", WX), ["Outside caller", "Canary DID", "Webex Calling"]),
    ]
    for item in more:
        add(topic(*item))
    return rows


def teams():
    rows = []
    add = rows.append
    add(topic(
        "tm-phone-system", "Teams Phone starts with a license", "The user is not callable until voice is assigned",
        "Teams Phone is a license plus a phone number plus a PSTN path. A Teams user who can chat is not yet a phone.",
        [
            "Assign Teams Phone, then a number, then a PSTN route.",
            "Calling Plans, Operator Connect, and Direct Routing are the PSTN paths. A user has one primary path for a given call.",
            "The Teams admin center is the system of record for the voice user.",
            "A resource account is not a human license. It is for attendants and queues.",
        ],
        "Buying a Calling Plan and assuming every Teams user can dial. The user still needs the assignment.",
        [
            "List three lab users: one with no voice, one with Teams Phone and no number, one with a lab number.",
            "Try to place a PSTN call as each. Record which step fails.",
            "Write the PSTN path you intend to use later in the path.",
            "Do not use a real employee's number in the notes.",
        ],
        [
            ("What does a Teams chat license not include?", "PSTN calling."),
            ("What do you assign after Teams Phone?", "A number and a route that matches how you reach the PSTN."),
            ("Name three PSTN paths.", "Calling Plans, Operator Connect, and Direct Routing."),
            ("What is a resource account for?", "Auto attendants and call queues, not a person's daily phone."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Teams", "PSTN"],
    ))
    add(topic(
        "tm-calling-plans", "Microsoft Calling Plans", "Microsoft is the carrier",
        "A Microsoft Calling Plan places PSTN with Microsoft. You do not pair an SBC for that call. If you also add a voice route, Direct Routing can steal the calls that match.",
        [
            "The user needs a Calling Plan license and a number Microsoft hosts.",
            "Outbound calls that match an online voice route go to Direct Routing instead.",
            "Emergency calling for Calling Plan users follows the Calling Plan emergency path, which you still test.",
            "Porting a number into Microsoft is a port order, not a PowerShell one-liner you run on hope.",
        ],
        "Ignoring an old voice routing policy that matches the numbers you thought the Calling Plan would carry.",
        [
            "Write whether the lab user has a Calling Plan, Direct Routing, or both.",
            "If both, write one number pattern that would hit Direct Routing.",
            "Place the canary that should stay on the Calling Plan.",
            "Record which path the call took.",
        ],
        [
            ("Who is the carrier on a Calling Plan?", "Microsoft."),
            ("When does Direct Routing override it?", "When the dialed number matches an online voice route assigned to that user."),
            ("Do you need an SBC for a pure Calling Plan user?", "No."),
            ("What is a port?", "A carrier order that moves the number. The license alone does not move it."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Teams", "Calling Plan"],
    ))
    add(topic(
        "tm-operator-connect", "Operator Connect", "The carrier joins Teams for you",
        "Operator Connect lets a participating carrier attach PSTN to Teams. You administer numbers and users in Teams. You do not operate the carrier's SBC.",
        [
            "The operator is selected and the numbers are released to your tenant.",
            "You still assign the number to a user, queue, or attendant.",
            "Emergency handling follows the operator and the Teams emergency configuration. Read both.",
            "Direct Routing skills do not transfer one-for-one. There may be no SBC for you to debug.",
        ],
        "Asking the customer for SBC syslog on an Operator Connect call.",
        [
            "Draw the operator, Teams, and the user. Leave the SBC in the operator's box.",
            "Write the evidence you can see: Teams call id and the number assignment.",
            "Write the evidence the operator owns.",
            "Name one ticket you would open with the operator instead of changing a voice route.",
        ],
        [
            ("Who operates the SBC in Operator Connect?", "The operator, not you."),
            ("What do you still assign?", "The number, to a user or a resource account."),
            ("Why is an SBC debug the wrong first step?", "You may not have that SBC."),
            ("What do you test?", "Inbound and outbound on a canary the operator has released."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Teams", "Operator"],
    ))
    add(topic(
        "tm-teams-phone-mobile", "Teams Phone Mobile", "The mobile number is the Teams number",
        "Teams Phone Mobile uses a supported operator so the user's mobile number is the Teams phone number. The handset and the Teams client share that identity. Coverage is the operator's network.",
        [
            "It is not a soft client on Wi-Fi alone.",
            "Caller ID should be tested on a call to a lab phone you control.",
            "Emergency calling uses the mobile path described in the current dynamic emergency document. Do not invent a LAN ELIN for it.",
            "A dead spot is a carrier ticket, not a voice-route edit.",
        ],
        "Applying a Direct Routing media-bypass checklist to a Teams Phone Mobile user.",
        [
            "Read the current Teams Phone Mobile prerequisites and write the date.",
            "Draw the mobile operator in the path.",
            "List two failures that belong to the operator.",
            "List one Teams assignment you still perform.",
        ],
        [
            ("Is Teams Phone Mobile just the app on Wi-Fi?", "No. An operator ties the mobile number to Teams."),
            ("Who owns a coverage hole?", "The mobile operator."),
            ("What Teams-side fact remains?", "The user assignment and the number in the tenant."),
            ("Which emergency story do you refuse to copy?", "A Direct Routing ELIN design, unless the current document says it applies."),
        ],
        ("Configure dynamic emergency calling", E911),
        ["Mobile", "Operator", "Teams"],
    ))
    add(topic(
        "tm-direct-routing-architecture", "Direct Routing architecture", "Teams, a paired SBC, then your PSTN",
        "Direct Routing sends Teams PSTN calls to an SBC you pair with the tenant. The SBC then talks to your carrier or PBX. Pairing is not routing.",
        [
            "The SBC FQDN is paired and has a certificate Teams trusts.",
            "SIP OPTIONS is the health signal. A failed OPTIONS probe takes the trunk out of rotation.",
            "Voice routes decide which calls use that SBC.",
            "Media can go direct or via Microsoft, depending on bypass and the network.",
        ],
        "Stopping after a successful pairing wizard and declaring dialing done.",
        [
            "Draw Teams, the SBC, and the carrier.",
            "Label pairing, OPTIONS, and the voice route as three different checks.",
            "Write a lab FQDN. Do not use a production name in public notes.",
            "State what a green OPTIONS probe does not prove: that a specific number matches a route.",
        ],
        [
            ("What does pairing prove?", "Teams accepts the SBC's name and certificate. Not the dial plan."),
            ("What does OPTIONS prove?", "The signaling path to that SBC is healthy enough to be used."),
            ("What selects the SBC for a call?", "The online voice route, via the user's voice routing policy."),
            ("Where does media go?", "Direct to the SBC when bypass applies, otherwise via Microsoft."),
        ],
        ("Direct Routing", DR),
        ["Teams", "SBC", "Carrier"],
    ))
    add(topic(
        "tm-sbc-fqdn", "SBC FQDN and certificate", "The name on the cert is the name you pair",
        "Teams pairs an SBC by FQDN. The public certificate must contain that name, and the chain must lead to a root Teams trusts. A private CA you invented will not do.",
        [
            "The FQDN in the tenant, the DNS name, and the certificate name are the same name.",
            "Wildcard certificates have limits in the current Direct Routing plan. Read that section before you buy one.",
            "Expiry is a calendar. A Friday expiry is a Monday outage.",
            "The SIP signaling port you choose has to match the pairing and the firewall.",
        ],
        "Pairing sip.contoso.local. Teams cannot validate a name that is not publicly resolvable in the way the plan requires.",
        [
            "Write a lab FQDN and the certificate name you would request.",
            "List the chain up to a public root, from the Direct Routing plan.",
            "Put the expiry date on the same line.",
            "Write the firewall rule for the signaling port you selected.",
        ],
        [
            ("What three names must match?", "The paired FQDN, DNS, and the certificate."),
            ("Why not a private root?", "Teams has to trust the chain. A lab CA you created is not on that list."),
            ("What do you calendar?", "Certificate expiry."),
            ("What else matches the pairing?", "The signaling port on the firewall and on the SBC."),
        ],
        ("Direct Routing", DR),
        ["Teams", "Public DNS", "SBC"],
    ))
    add(topic(
        "tm-sip-options", "SIP OPTIONS", "Health is a probe, not a ping",
        "Teams sends SIP OPTIONS to a paired SBC. If the SBC does not answer the way the plan requires, Teams stops sending calls there.",
        [
            "OPTIONS is signaling. ICMP ping is not a substitute.",
            "A firewall that allows a single test INVITE and drops OPTIONS will flap.",
            "Multiple SBCs are only useful if each answers OPTIONS.",
            "TLS failures show up here before users do, if you are watching.",
        ],
        "Using ping as proof the Direct Routing trunk is healthy.",
        [
            "Identify the OPTIONS response in a lab trace or a diagram of one.",
            "Block OPTIONS in a lab policy and record how many failures Teams wants before it withdraws the trunk. Use the current plan's number, and write the date you read it.",
            "Restore OPTIONS and record recovery.",
            "Write the alert: OPTIONS failure, not interface up.",
        ],
        [
            ("What probe does Teams use toward the SBC?", "SIP OPTIONS."),
            ("Why is ping insufficient?", "It does not exercise SIP or TLS."),
            ("What happens after repeated failures?", "Teams stops selecting that SBC until it recovers."),
            ("What do you alert on?", "OPTIONS failure."),
        ],
        ("Direct Routing", DR),
        ["Teams", "SBC", "Firewall"],
    ))
    add(topic(
        "tm-voice-routing-policy", "Voice routing policies", "The user does not dial an SBC",
        "An online voice routing policy is a list of PSTN usages assigned to a user. The usages point at voice routes. The routes point at SBCs. Users are not configured with an SBC hostname.",
        [
            "No policy means no Direct Routing outbound, unless a Calling Plan is the fallback.",
            "The order of usages is the order of evaluation.",
            "A policy can be assigned to users in bulk. A mistake is wide.",
            "Resource accounts for queues need a policy too if they place outbound calls.",
        ],
        "Assigning a route and forgetting to put its usage in any policy.",
        [
            "Create two lab usages on paper: local and national.",
            "Put only local in a policy and assign it to a lab user.",
            "Show that a national pattern does not match.",
            "Add the national usage, reorder it, and say which match wins.",
        ],
        [
            ("What do you assign to a user?", "An online voice routing policy, not an SBC FQDN."),
            ("What is inside the policy?", "An ordered list of PSTN usages."),
            ("What if nothing matches and there is no Calling Plan?", "The call fails."),
            ("Who else needs a policy?", "A resource account that places outbound calls."),
        ],
        ("Configure call routing for Direct Routing", ROUTE),
        ["User", "Voice routing policy", "SBC"],
    ))
    add(topic(
        "tm-pstn-usages", "PSTN usages", "The join between a policy and a route",
        "A PSTN usage is a label. A policy includes usages. A voice route includes usages. The call matches when those sets intersect and the number pattern matches.",
        [
            "Usages are not numbered permissions by themselves. They are names you reuse.",
            "A route with no usage in any assigned policy never runs.",
            "A policy with a usage that no route lists never matches.",
            "Name usages after intent: local, national, international. Not after a project code nobody can say.",
        ],
        "Creating a new usage on the route and not adding it to the policy, then blaming the SBC.",
        [
            "Write one usage name and the route that lists it.",
            "Write the policy that includes it.",
            "Remove it from the policy on paper and state the result.",
            "Put it back and state the result.",
        ],
        [
            ("What does a PSTN usage connect?", "A voice routing policy and a voice route."),
            ("Does the usage itself contain a number pattern?", "No. The voice route does."),
            ("Why might a healthy SBC stay silent?", "No assigned policy includes a usage that route lists."),
            ("How should you name usages?", "After the class of call, so an interview and a ticket can say them."),
        ],
        ("Configure call routing for Direct Routing", ROUTE),
        ["Policy", "PSTN usage", "Voice route"],
    ))
    add(topic(
        "tm-voice-routes", "Voice routes", "Pattern, priority, and gateway",
        "An online voice route has a number pattern, a priority, a list of PSTN usages, and one or more SBCs. The first matching route in priority order wins.",
        [
            "Patterns are regular expressions on the normalized number. A typo matches nothing or everything.",
            "Priority breaks ties between routes. Know which number is tried first.",
            "An SBC on the route that fails OPTIONS is skipped.",
            "A Calling Plan user can still fall through to Microsoft when no route matches.",
        ],
        "A pattern so broad that international calls use the local SBC by accident.",
        [
            "Write a lab pattern for one country code and one area.",
            "Write a second, more specific pattern with a better priority.",
            "Say which route wins for a lab number in that area.",
            "Say which route wins for a lab number outside it.",
        ],
        [
            ("What is in a voice route?", "A number pattern, a priority, usages, and SBC targets."),
            ("What does priority do?", "It orders routes when more than one could match."),
            ("When is an SBC on the route ignored?", "When OPTIONS has marked it down."),
            ("What happens to a Calling Plan user if no route matches?", "The call can still use the Calling Plan."),
        ],
        ("Configure call routing for Direct Routing", ROUTE),
        ["Teams", "Voice route", "SBC"],
    ))
    add(topic(
        "tm-dial-plan-normalization", "Dial-plan normalization", "What the user dials becomes E.164",
        "A Teams dial plan rewrites what a person dials into the E.164 form voice routes expect. Normalization happens before the route pattern is compared.",
        [
            "Tenant dial plans and user dial plans both exist. Know which one is assigned.",
            "A normalization rule has a pattern and a translation.",
            "If normalization fails, the route sees the raw digits and usually does not match.",
            "Test from the client keypad, not only from PowerShell, when you can.",
        ],
        "Writing the voice route for 10-digit dialing and normalizing those digits to E.164 first. The route never sees 10 digits.",
        [
            "Write a lab rule that turns a 10-digit lab number into plus-form.",
            "Write the voice route pattern against the plus-form, not the 10 digits.",
            "Show one number that should not match the rule.",
            "Assign the plan to one lab user, not the whole tenant, in the exercise.",
        ],
        [
            ("When does normalization run?", "Before voice-route matching."),
            ("What does a rule contain?", "A match pattern and a translation."),
            ("Why do route patterns usually look like E.164?", "Because normalization already added the country code and the plus."),
            ("What is the blast radius of a tenant dial plan?", "Every user who inherits it. Test with one user first."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Dial plan", "Voice route"],
    ))
    add(topic(
        "tm-media-bypass", "Media bypass", "Media can skip Microsoft",
        "Media bypass lets the Teams client send media directly to the SBC when the policy and the network allow it. Signaling still goes to Microsoft. Bypass is not the default just because the SBC is certified.",
        [
            "The SBC and the user both have to be eligible.",
            "A firewall between the client and the SBC breaks bypass and looks like one-way audio.",
            "ICE and the media ports in the network guide still apply.",
            "When bypass does not apply, media hairpins through Microsoft. That is a supported path, not automatically a fault.",
        ],
        "Opening a carrier ticket for one-way audio when the client cannot reach the SBC's media address.",
        [
            "Draw signaling via Teams and media direct to the SBC.",
            "Draw the fallback where media goes through Microsoft.",
            "Write the address the client must reach in the bypass case.",
            "Name the capture that proves which path you got.",
        ],
        [
            ("Does bypass change signaling?", "No. Signaling still goes through Teams. Media may go direct."),
            ("Is bypass automatic on a certified SBC?", "No. It is configured, and the network has to allow it."),
            ("What does bypass one-way audio usually mean?", "The client cannot exchange RTP with the SBC address."),
            ("Is hairpin through Microsoft a failure?", "Not by itself. It is the non-bypass path."),
        ],
        ("Configure Local Media Optimization", LMO),
        ["Teams client", "SBC", "Microsoft media"],
    ))
    add(topic(
        "tm-local-media-optimization", "Local media optimization", "Keep the media in the branch",
        "Local media optimization keeps branch media on the local SBC instead of tromboning it. It uses the same network sites and trusted IPs as other cloud voice features. Microsoft's configuration guide is the source, not a whiteboard from memory.",
        [
            "A proxy SBC and a downstream SBC are different roles.",
            "The client's site is calculated from trusted IPs and subnets.",
            "A wrong site sends media to the wrong SBC and then re-invites.",
            "VPN split tunnels that hide the trusted IP break the site calculation.",
        ],
        "Reusing a location-based routing site without checking the trusted IP list.",
        [
            "Draw a branch SBC and a central proxy SBC.",
            "Write the trusted IP that marks a client as internal.",
            "Write what a VPN would do to that address.",
            "Read the current configuration article and date it.",
        ],
        [
            ("What is local media optimization for?", "Keeping media between a branch user and the local SBC."),
            ("What identifies an internal client?", "Trusted IPs and the network site configuration."),
            ("Why do VPNs confuse it?", "The address Teams sees may not be the branch address."),
            ("Which article do you follow?", "Configure Local Media Optimization for Direct Routing."),
        ],
        ("Configure Local Media Optimization", LMO),
        ["Branch user", "Downstream SBC", "Proxy SBC"],
    ))
    add(topic(
        "tm-codecs", "Codecs on Direct Routing", "The offer is a list, not a wish",
        "Teams and the SBC negotiate a codec. SILK, G.722, and G.711 are not interchangeable just because all three are audio. Write the codec you require for fax or recording.",
        [
            "The answer picks one codec from the offer.",
            "Transcoding on the SBC costs DSP. A design that transcodes every call should say so.",
            "Fax wants G.711. A compressed codec makes a reliable fax unlikely.",
            "The codec is in the SDP. A client badge is not the SDP.",
        ],
        "Forcing a codec in the middle of a one-way audio debug. You have two variables.",
        [
            "Capture or sketch a lab offer and a lab answer.",
            "Circle the chosen codec.",
            "Say whether the SBC transcoded.",
            "If the call is a fax lab, say why G.711 is the requirement.",
        ],
        [
            ("Where is the negotiated codec?", "In the SDP answer."),
            ("What does transcoding cost?", "DSP or equivalent resources on the SBC."),
            ("Which codec do you want for fax?", "G.711."),
            ("Why not change the codec while chasing one-way audio?", "You can no longer tell which change mattered."),
        ],
        ("RFC 4566", RFC4566),
        ["Teams", "SBC", "Carrier"],
    ))
    add(topic(
        "tm-early-media", "Early media and 183", "Ringback can be audio before the answer",
        "A 183 with SDP is early media. The caller may hear a carrier announcement or ringback before 200 OK. That audio is RTP, and a firewall can block it while the later call still connects.",
        [
            "180 Ringing with no SDP is not early media.",
            "183 with SDP means media addresses are already chosen.",
            "One-way ringback is the same class of fault as one-way audio, earlier in the call.",
            "Do not convert every 183 into a PRACK story. Reliable provisionals are negotiated.",
        ],
        "Waiting for 200 OK before you look at media, while the caller is complaining about silence during ringback.",
        [
            "Sketch a 180 without SDP and a 183 with SDP.",
            "Mark where RTP starts in each.",
            "Write the firewall symptom: ringback silent, call fine after answer, or the reverse.",
            "Name the SDP port you would capture.",
        ],
        [
            ("What is early media?", "RTP before the final answer, usually after a 183 with SDP."),
            ("Is 180 the same?", "Not when it carries no SDP."),
            ("Does 183 always require PRACK?", "No. PRACK is negotiated."),
            ("What symptom matches a blocked early-media path?", "Silence before answer, or one-way progress tones."),
        ],
        ("RFC 3261", RFC3261),
        ["Caller", "Teams", "SBC"],
    ))
    add(topic(
        "tm-refer-transfer", "REFER and transfer", "Who places the second call",
        "A SIP REFER asks the other party to call the transfer target. Teams Direct Routing supports transfer methods the considerations article describes. A hairpin transfer keeps both legs on the SBC and uses two channels.",
        [
            "REFER moves work off the transferrer.",
            "A hairpin holds two call legs for one conversation.",
            "If REFER is rejected, the SBC may hairpin. Know which one you configured.",
            "The Call-ID after a successful REFER is not the original Call-ID.",
        ],
        "Declaring transfer broken because the first Call-ID ended.",
        [
            "Place a lab transfer and record both call ids.",
            "Note whether you saw REFER or a second INVITE from the SBC.",
            "Count the channels used during the consult if you hairpin.",
            "Write the user-visible result, separate from the SIP result.",
        ],
        [
            ("What does REFER ask the far end to do?", "Place a new call to the target."),
            ("What is a hairpin?", "The SBC keeps both legs and bridges them."),
            ("Why does the original Call-ID end?", "The transfer finished. That can be success."),
            ("Where is the behavior documented?", "The Direct Routing considerations and protocol articles, for the features you enabled."),
        ],
        ("Considerations for Direct Routing", CONSIDER),
        ["Caller", "SBC", "Target"],
    ))
    add(topic(
        "tm-media-ports", "Teams media ports", "Open the range you read this quarter",
        "Teams media uses documented UDP ranges and TURN relays. Copy the range from the current network article into the firewall ticket and date it. A remembered range from a blog is not a design.",
        [
            "Signaling to Teams is not the media range.",
            "Bypass media uses the SBC's own media ports as well.",
            "QoS policies have to match the ports you actually open.",
            "A client on a guest network will fail a range the office firewall allows.",
        ],
        "Opening TCP 5060 to the internet and calling the Teams client fixed.",
        [
            "Open the current Teams network guidance and write the date.",
            "Separate client-to-Teams media from client-to-SBC media.",
            "Compare the firewall ticket to those two rows.",
            "Highlight any port that is not in the document.",
        ],
        [
            ("Why date the port list?", "Microsoft changes ranges. An undated copy drifts."),
            ("Are signaling and media the same ports?", "No."),
            ("What extra ports appear with media bypass?", "The SBC's media addresses and ports."),
            ("What is the wrong opened port story?", "TCP 5060 from a CUCM habit, aimed at the Teams client."),
        ],
        ("Direct Routing", DR),
        ["Teams client", "Firewall", "SBC"],
    ))
    add(topic(
        "tm-qos", "QoS for Teams media", "Mark the media, not the whole PC",
        "Teams QoS marks media so the network you operate can queue it. The marking has to survive the first switch, and a VPN can hide it in an outer header.",
        [
            "Use the DSCP values from the current Teams QoS article.",
            "Client source ports and DSCP are configured together in that design.",
            "Re-marking at the WAN is a second policy. Say if you do it.",
            "A speed test does not enter the voice queue.",
        ],
        "Enabling QoS on the SBC and forgetting the client, or the reverse, then comparing two different markings.",
        [
            "Write the DSCP for audio from the current article and the date.",
            "Name the device that sets it.",
            "Name the first untrusted hop.",
            "State what a full-tunnel VPN does to the mark.",
        ],
        [
            ("What document sets the DSCP numbers?", "The current Microsoft Teams QoS guidance."),
            ("Why name the device that marks?", "A mark set and then stripped is not a policy."),
            ("How does a VPN interfere?", "The outer header is what the WAN classifies."),
            ("What test is not a voice test?", "A bulk speed test."),
        ],
        ("Teams Phone", PHONE),
        ["Teams client", "Switch", "WAN"],
    ))
    add(topic(
        "tm-emergency-policy", "Emergency call routing policies", "Direct Routing emergency is a route",
        "For Direct Routing, an emergency call routing policy names the emergency numbers and the PSTN usage that routes them. Calling Plan and Operator Connect users are covered by their service. Do not apply the Direct Routing policy as if it were universal.",
        [
            "There must be a voice route for the emergency dial string.",
            "The policy can be assigned to users or to network sites.",
            "Dynamic emergency adds the client's current location. PIDF-LO has to be enabled on the SBC when that design needs it.",
            "SBA mode does not apply emergency call routing policies. The considerations in the SBA article are blunt about this.",
        ],
        "Assuming a normal voice route for 10-digit dialing also matches 911. It often does not.",
        [
            "Write the emergency dial strings for the lab country.",
            "Write a dedicated route for those strings.",
            "Assign the policy to one lab site, not the whole tenant, in the exercise.",
            "Read the SBA limitation and write one sentence in your own words.",
        ],
        [
            ("Who uses an emergency call routing policy?", "Direct Routing."),
            ("What must exist besides the policy?", "An online voice route for the emergency dial string."),
            ("Where can the policy be assigned?", "Users, network sites, or both."),
            ("What does SBA not honor?", "Emergency call routing policies. Plan a matching route in the survivable policy."),
        ],
        ("Configure dynamic emergency calling", E911),
        ["User", "Emergency policy", "SBC"],
    ))
    add(topic(
        "tm-emergency-addresses", "Emergency addresses and places", "Civic address, then a place, then a test",
        "Teams emergency addresses are civic addresses. Places refine them inside a building. A network site binds a subnet to that location for dynamic emergency calling.",
        [
            "An address Microsoft has not validated is not done.",
            "A subnet mapped to the wrong site sends the wrong location.",
            "Trusted IPs tell Teams the user is on your network.",
            "Test with the published test number, not with a real emergency call.",
        ],
        "Mapping a VPN subnet to a headquarters address so every remote user looks like they are in the HQ lobby.",
        [
            "Write one lab civic address and one place.",
            "Map one lab subnet to that site.",
            "Write the trusted IP.",
            "Name the test call. Do not place a real emergency call.",
        ],
        [
            ("What is a civic address?", "A validated street address, not a nickname."),
            ("What is a place?", "A finer location inside that address, such as a floor, when you use one."),
            ("What does a subnet mapping do?", "It associates clients on that subnet with the site's emergency location."),
            ("Why is a VPN pool dangerous?", "It can stamp every remote user with one building."),
        ],
        ("Configure dynamic emergency calling", E911),
        ["Client", "Network site", "Emergency location"],
    ))
    add(topic(
        "tm-dynamic-emergency", "Dynamic emergency calling", "Location follows the network, then you prove it",
        "Dynamic emergency calling routes and notifies based on where the Teams client is attached. Direct Routing must add location information to the outbound emergency INVITE. The SBC or an emergency routing provider uses that information.",
        [
            "Network regions, sites, subnets, and trusted IPs are shared with local media optimization and location-based routing.",
            "PIDF-LO is how location rides in the INVITE when you enable it on the gateway.",
            "Notification of a security desk is a policy, separate from the PSAP path.",
            "A client off your network uses the external behavior the current article describes. Read it for the country you are in.",
        ],
        "Turning on dynamic emergency in the admin center and never enabling PIDF-LO on the SBC.",
        [
            "Draw the client, Teams, the SBC, and the emergency provider.",
            "Mark where PIDF-LO is inserted.",
            "Mark where the security desk is notified.",
            "Write the country limitation you read, with the date.",
        ],
        [
            ("What does dynamic emergency use to find the user?", "The network site and subnet, when the client is on a trusted network."),
            ("What must the SBC add for Direct Routing?", "Location information on the emergency INVITE, when that is the design."),
            ("Is security-desk notification the same as the PSAP call?", "No. It is a separate policy."),
            ("Which article is the source?", "Configure dynamic emergency calling."),
        ],
        ("Configure dynamic emergency calling", E911),
        ["Teams client", "SBC", "PSAP path"],
    ))
    add(topic(
        "tm-location-based-routing", "Location-based routing", "Toll bypass is a policy, not a feeling",
        "Location-based routing stops a call from leaving through a gateway the user is not allowed to use, which is how some countries prevent toll bypass. It uses network sites. A user who looks external follows the external rule.",
        [
            "LBR and local media optimization share site data and can be configured together. The LMO article calls out the gateway flag for downstream SBCs.",
            "A VPN can make an in-country user look external, or the reverse.",
            "The failure mode is a blocked call, not one-way audio.",
            "Test a user inside the site and a user outside it.",
        ],
        "Enabling LBR globally because one site needed it, and blocking every traveler.",
        [
            "Name one lab site that is in scope.",
            "Write the call that should succeed inside the site.",
            "Write the call that should be blocked outside it.",
            "Note the VPN behavior in one sentence.",
        ],
        [
            ("What does location-based routing prevent?", "A call using a PSTN gateway the user's location is not allowed to use."),
            ("What data does it share with local media optimization?", "Network regions, sites, subnets, and trusted IPs."),
            ("What does a blocked LBR call look like?", "The call is rejected, rather than connected with broken audio."),
            ("Why are VPNs part of the test?", "They change the address Teams uses to place the user."),
        ],
        ("Configure Local Media Optimization", LMO),
        ["User", "Network site", "SBC"],
    ))
    add(topic(
        "tm-resource-accounts", "Resource accounts", "Attendants and queues are not people",
        "Auto attendants and call queues need resource accounts. Those accounts hold the phone number. They are not Teams Phone users with a handset, and they need a voice route if they send calls out.",
        [
            "Create the resource account, assign the license the current article requires, and assign the number.",
            "Then attach it to the attendant or the queue.",
            "Outbound from the queue uses a voice routing policy on that account if the path is Direct Routing.",
            "A disabled account silently kills the pilot number.",
        ],
        "Assigning the queue's DID to a human so you can 'just test it'.",
        [
            "Create the lab objects on paper: resource account, number, attendant.",
            "Call the pilot.",
            "Disable the account in the exercise and state the result.",
            "If the attendant transfers to PSTN, name the policy on the resource account.",
        ],
        [
            ("What holds the phone number for a queue?", "A resource account."),
            ("Is that account a user's phone?", "No."),
            ("When does it need a voice routing policy?", "When it places or transfers calls to Direct Routing PSTN."),
            ("What does disabling it do?", "The pilot stops receiving calls."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Resource account", "Queue"],
    ))
    add(topic(
        "tm-auto-attendant", "Teams auto attendants", "Hours, menus, and the after-hours path",
        "A Teams auto attendant answers a resource account, plays a menu, and sends the caller to a person, a queue, or another attendant. Business hours and holidays are part of the object.",
        [
            "The after-hours menu is a second design. Test it.",
            "Dial-by-name depends on directory data. Empty names match nothing.",
            "A transfer to an external number needs a PSTN path on the resource account.",
            "Nested attendants are easy to loop. Cap the depth.",
        ],
        "Testing only the weekday menu on a Tuesday and shipping the holiday menu untried.",
        [
            "Build a two-choice lab menu.",
            "Call each choice.",
            "Force the after-hours schedule and call again.",
            "Try one external transfer and name the policy that allowed it.",
        ],
        [
            ("What answers the number?", "The auto attendant attached to the resource account."),
            ("What must you test besides the open menu?", "After hours and holidays."),
            ("Why might dial-by-name fail?", "The directory entry has no usable name."),
            ("What does an external transfer require?", "A PSTN path, often a voice routing policy on the resource account."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Auto attendant", "Target"],
    ))
    add(topic(
        "tm-call-queues", "Teams call queues", "Agents, timeout, and overflow",
        "A Teams call queue holds callers and rings agents. Presence decides who is eligible. Overflow and timeout are different exits. The queue is not a Contact Center product.",
        [
            "Agents opt in or are assigned, depending on the configuration. Know which.",
            "A timeout sends the caller to a destination you chose.",
            "Overflow fires when the queue cannot take another call.",
            "Music on hold is a setting. Silence means you should look at it.",
        ],
        "Staffing the queue with a distribution list and expecting presence to page someone.",
        [
            "Create a lab queue with two agents.",
            "Make one agent busy and call the pilot.",
            "Let the timeout expire and record the destination.",
            "Fill the overflow condition in the exercise and record that destination too.",
        ],
        [
            ("What makes an agent eligible?", "Assignment or opt-in, plus a presence that the queue accepts."),
            ("How do timeout and overflow differ?", "Timeout is wait length. Overflow is queue capacity."),
            ("Is this Microsoft Contact Center?", "No. It is a Teams Phone queue."),
            ("What do you record?", "Pilot number, agent presence, and the call id."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Call queue", "Agent"],
    ))
    add(topic(
        "tm-caller-id", "Caller ID policies", "The identity the PSTN sees",
        "A Teams caller ID policy chooses what outbound identity a user presents. The far end is the proof. A policy that says anonymous is not the same as sending the company's main number.",
        [
            "User number, service number, and anonymous are different choices.",
            "The carrier or SBC can still rewrite the identity. Check PAI and From.",
            "Test from outside the tenant.",
            "Resource accounts have identities too.",
        ],
        "Trusting the admin-center preview and never placing the call.",
        [
            "Set a lab user to present a lab service number.",
            "Call a second lab endpoint via the PSTN path.",
            "Record the displayed identity.",
            "If the SBC rewrites it, write the header it rewrites.",
        ],
        [
            ("What is the proof of caller ID?", "The identity presented to the far end."),
            ("Is anonymous the same as the main number?", "No."),
            ("Where else can the identity change?", "On the SBC, in From or PAI."),
            ("Who else has an identity?", "Resource accounts that place outbound calls."),
        ],
        ("Configure call routing for Direct Routing", ROUTE),
        ["User", "Teams", "Far end"],
    ))
    add(topic(
        "tm-calling-policies", "Calling policies", "Forwarding, privacy, and what a user may do",
        "A Teams calling policy controls what a user is allowed to do: forwarding, simultaneous ring, call groups, and privacy features. It is not the voice routing policy.",
        [
            "Voice routing chooses the SBC. Calling policy chooses the features.",
            "A user can have a working route and still be forbidden to forward to PSTN.",
            "Policies assigned to a wide group are a wide blast radius.",
            "Test with one lab user in a custom policy.",
        ],
        "Editing the voice route because call forwarding is greyed out.",
        [
            "Name one feature the calling policy controls.",
            "Put a lab user in a restrictive policy and attempt that feature.",
            "Move the user to a policy that allows it and repeat.",
            "Write the sentence that separates this policy from a voice route.",
        ],
        [
            ("What does a calling policy control?", "User features such as forwarding and privacy, not the SBC route."),
            ("What does a voice routing policy control?", "Which PSTN usages, and therefore which routes and SBCs, are available."),
            ("Why can forwarding fail on a healthy trunk?", "The calling policy forbids it."),
            ("How do you test safely?", "One lab user in a custom policy."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Calling policy", "Target"],
    ))
    add(topic(
        "tm-delegation", "Delegation and shared lines", "Someone else rings on your number",
        "Delegation lets another person receive and place calls for a user. A shared line appearance puts that number on their client. Permissions are explicit. A delegate is not a hunt group.",
        [
            "The delegate's client must actually be signed in.",
            "Outbound calls the delegate places can present the delegator's number. Test the identity.",
            "Voicemail still belongs to someone. Say who.",
            "Remove delegation when the person changes roles. It does not expire.",
        ],
        "Using delegation as a night bell for a factory. You wanted a queue or an attendant.",
        [
            "Name a lab delegator and a lab delegate.",
            "Call the delegator and answer as the delegate.",
            "Place an outbound call as the delegate and record the caller ID.",
            "Remove the delegation and confirm the delegate no longer rings.",
        ],
        [
            ("What does delegation do?", "It lets another person handle calls for a user."),
            ("Is it a hunt group?", "No."),
            ("What identity do you test on outbound?", "Whether the delegator's number is presented."),
            ("What cleanup matters?", "Remove the delegation when the role ends."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Delegator", "Delegate"],
    ))
    add(topic(
        "tm-cloud-voicemail", "Cloud voicemail", "The timer sends the call there",
        "Cloud voicemail answers when the user's unanswered-call treatment says so. The greeting, the timeout, and the transcription setting are separate. Transcription is a privacy decision.",
        [
            "No-answer timeout is what diverts the call.",
            "A queue timeout that sends callers to a person's voicemail is a destination you chose.",
            "Message waiting in the client is not the same as an email copy.",
            "A forwarded call may land in the forward target's mailbox.",
        ],
        "Opening an SBC ticket because a user who disabled voicemail has no messages.",
        [
            "Set a short lab timeout.",
            "Call and do not answer. Confirm the mailbox takes the call.",
            "Leave a test message you are allowed to leave.",
            "Forward the user and see which mailbox answers.",
        ],
        [
            ("What sends a call to voicemail?", "The no-answer or busy treatment and its timer."),
            ("Is transcription automatic in every design?", "No. Treat it as a setting with a privacy note."),
            ("Can a queue send callers to voicemail?", "Yes, if that is the timeout or overflow destination."),
            ("Whose mailbox answers a forward?", "The target's, unless you designed otherwise. Test it."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "User", "Cloud voicemail"],
    ))
    add(topic(
        "tm-compliance-recording", "Policy-based recording", "The recorder is a participant",
        "Teams policy-based recording invites a recorder into the call. If the policy says the call must be recorded and the recorder cannot join, the call behavior follows that policy. Know whether you fail open or fail closed.",
        [
            "The policy is assigned. A tenant default you did not read still counts.",
            "The recorder bot or integration has to be allowed.",
            "The recording id must join to the Teams call id.",
            "Do not record real people as a lab. Use a test call between lab accounts.",
        ],
        "Pointing at a user's local folder and calling it compliance recording.",
        [
            "Name the recorder as a box on the diagram.",
            "Write fail open or fail closed.",
            "Place a lab call between test accounts.",
            "Write the id you would use to find the file.",
        ],
        [
            ("What invites the recorder?", "The recording policy."),
            ("What is fail closed?", "The call does not proceed if recording cannot start."),
            ("What joins the file to the call?", "A shared call id."),
            ("Who may be in the lab recording?", "Test accounts, not unsuspecting people."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Teams", "Recorder"],
    ))
    add(topic(
        "tm-survivable-branch", "Survivable Branch Appliance", "PSTN when the internet path to Teams is down",
        "A Survivable Branch Appliance keeps making and receiving PSTN calls during an internet outage. The client switches to appliance mode and shows a banner. Features that need Microsoft, including emergency location sharing, are limited. The SBA article is specific: emergency call routing policies are not supported in that mode.",
        [
            "The SBC is configured for media bypass so branch media can stay local.",
            "Users need the branch survivability policy.",
            "Hold and resume of PSTN calls are in the supported list. Arbitrary Teams features are not.",
            "Emergency dial strings still need a pattern the surviving route can match.",
        ],
        "Promising full Teams functionality, including dynamic emergency location, during an SBA event.",
        [
            "Read the SBA article and write the date.",
            "List three things that still work.",
            "List the emergency limitation in your own words.",
            "Name the banner the user should see. If the banner is absent, they are not in appliance mode.",
        ],
        [
            ("What is an SBA for?", "PSTN calling during an outage of the path to Teams."),
            ("How does the user know?", "A banner. No banner means they are not in appliance mode."),
            ("What emergency limitation does Microsoft document?", "SBA does not support emergency call routing policies, and location is not shared the same way."),
            ("What media prerequisite does the article call out?", "Media bypass, so the branch client can send media to the SBC."),
        ],
        ("Direct Routing SBA", SBA),
        ["Branch user", "SBA", "SBC"],
    ))
    add(topic(
        "tm-common-area", "Common area phones", "A phone with an account, not a person's daily driver",
        "A common area phone signs in with its own account and a Calling Plan, Operator Connect number, or Direct Routing number. It is for a place. People should not share the password of their personal account to use it.",
        [
            "The account is licensed for a device, not for a knowledge worker's mailbox habits.",
            "Hotline or restricted dialing is a policy choice.",
            "Emergency location is the place where the phone sits.",
            "Firmware and Teams app updates are a device lifecycle, not a user training issue.",
        ],
        "Signing a personal user into a lobby phone so callers see that person's caller ID.",
        [
            "Create a lab common-area account on paper.",
            "Assign a lab number and a restrictive calling policy.",
            "Call inbound to the device.",
            "Write the emergency site as the lobby, not as the installer's home.",
        ],
        [
            ("Whose account signs into the phone?", "A dedicated common-area account."),
            ("Why restrict the dialing?", "A public handset should not inherit an executive's international permission."),
            ("What emergency location do you use?", "The phone's physical site."),
            ("What is the wrong identity?", "A person's user account signed in on a shared phone."),
        ],
        ("Considerations for Direct Routing", CONSIDER),
        ["Caller", "Common area phone", "Teams"],
    ))
    add(topic(
        "tm-analog-sbc", "Analog devices behind the SBC", "The SBC or ATA speaks SIP, the fax does not",
        "Analog phones, fax, and door boxes connect through an ATA or an SBC FXS port. Teams sees a SIP endpoint. Fax needs G.711 and a clean path. A compressed codec is a choice against fax.",
        [
            "Register or route the analog endpoint as its own number.",
            "Test voice and fax separately.",
            "Hookflash and paging features are device features. Confirm the ATA supports them.",
            "Do not put a fax machine on a wireless client path.",
        ],
        "Opening a Teams client log for a fax machine that never ran a client.",
        [
            "Draw the fax machine, the ATA, the SBC, and Teams.",
            "Mark which box speaks SIP.",
            "Require G.711 in the lab notes.",
            "Place one voice call from the analog port.",
        ],
        [
            ("What does Teams register or route?", "The SIP endpoint, the ATA or SBC, not the analog electrons."),
            ("Which codec do you set aside for fax?", "G.711."),
            ("Where do you look when fax fails and voice works?", "Codec, delay, and the ATA port. Not the user's Teams client."),
            ("What is a bad path for fax?", "A wireless or heavily transcoded path."),
        ],
        ("Direct Routing", DR),
        ["Analog device", "ATA", "SBC"],
    ))
    add(topic(
        "tm-number-assignment", "Number assignment", "Inventory, then the user, then the test",
        "A phone number in Teams is inventory first. Then you assign it to a user or a resource account. An unassigned number does not ring a person just because the carrier delivered it.",
        [
            "Calling Plan, Operator Connect, and Direct Routing numbers are inventoried differently. Use the path you actually bought.",
            "Assignment is reversible. Test after you move a number.",
            "Emergency addresses are associated as the current guide describes. Do not skip them because the inbound call worked.",
            "Record the number in plus form in the lab notebook.",
        ],
        "Giving the same DID to a user and a queue and hoping Teams picks the right one.",
        [
            "Add one lab number to inventory on paper.",
            "Assign it to a user and call it.",
            "Move it to a resource account and call it again.",
            "Write the emergency association you still owe that number.",
        ],
        [
            ("What comes before assignment?", "The number has to be in the tenant inventory for that PSTN path."),
            ("Can one DID belong to a user and a queue at once?", "No. Move it, then test."),
            ("What form do you write in notes?", "Plus-form E.164."),
            ("What test follows a move?", "An inbound call, plus the emergency association."),
        ],
        ("Teams Phone", PHONE),
        ["Carrier", "Teams inventory", "User"],
    ))
    add(topic(
        "tm-porting", "Porting numbers into Teams", "FOC is the carrier's clock",
        "A port moves a number onto Calling Plans or an Operator Connect inventory. The firm order commitment is the carrier's clock. Your voice route change is not a port, and a port is not a Direct Routing translation.",
        [
            "You need an authorized letter and an accurate inventory. Wrong service addresses reject ports.",
            "Schedule the Teams assignment for after the number is in inventory.",
            "Keep the old platform able to roll back until the canary succeeds.",
            "Direct Routing often does not port into Microsoft at all. The carrier still points at your SBC.",
        ],
        "Deleting the number on the old PBX the night before a FOC you have not read.",
        [
            "Write a fictional port request with a documentation-range number.",
            "Mark the FOC as a date you do not control.",
            "Write the assignment step that happens after inventory.",
            "Write the rollback if the inbound canary fails.",
        ],
        [
            ("What is a FOC?", "The carrier's firm order commitment for the port."),
            ("Does Direct Routing always include a port into Microsoft?", "No. The carrier can keep pointing the number at your SBC."),
            ("When do you assign the number in Teams?", "After it is in the tenant inventory."),
            ("What do you keep until the canary works?", "A way back to the old platform."),
        ],
        ("Teams Phone", PHONE),
        ["Old carrier", "Port order", "Teams"],
    ))
    add(topic(
        "tm-mixed-pstn", "Mixing Calling Plan and Direct Routing", "The route wins when it matches",
        "A user can hold a Calling Plan and still send matching numbers to Direct Routing if an online voice routing policy is assigned. Unmatched numbers fall through to the Calling Plan. This is documented behavior, and it surprises people who thought the license was the whole story.",
        [
            "Draw two exits: SBC and Microsoft PSTN.",
            "The voice route pattern decides which exit.",
            "A too-broad pattern puts Calling Plan minutes on your SBC by accident, or the reverse.",
            "Test one number that matches and one that does not.",
        ],
        "Removing the Calling Plan license as a cleanup and discovering the unmatched numbers now fail.",
        [
            "Write a lab pattern that should use the SBC.",
            "Write a lab number that should stay on the Calling Plan.",
            "Assign the policy to one user.",
            "State what happens if you remove the Calling Plan license.",
        ],
        [
            ("When does a Calling Plan user use Direct Routing?", "When the dialed number matches an assigned online voice route."),
            ("When does the Calling Plan carry the call?", "When no admin route matches."),
            ("What is a dangerous pattern?", "One so broad that every destination matches the SBC."),
            ("What breaks if you remove the Calling Plan?", "Numbers that matched no voice route."),
        ],
        ("Configure call routing for Direct Routing", ROUTE),
        ["User", "Voice route", "Calling Plan"],
    ))
    add(topic(
        "tm-outbound-fraud", "Outbound fraud controls", "Block the destination before the invoice",
        "Outbound fraud on Teams is a user account placing calls it should not. Calling policies, voice routes, and carrier blocks are three layers. An alert on attempts beats an invoice.",
        [
            "International and premium patterns deserve their own usage, assigned to almost nobody.",
            "A compromised account looks like a traffic spike, often after hours.",
            "The SBC can have its own dial-peer block. Defense in depth is two blocks, not a debate about which team cares.",
            "The canary user is not in the international usage.",
        ],
        "Giving the tenant voice routing policy the international usage because it was easier than assigning exceptions.",
        [
            "Define a lab international usage that is on no default policy.",
            "Attempt the pattern as a normal lab user and record the failure.",
            "Add the usage to one lab user and record the path.",
            "Name the alert: attempts, not only minutes.",
        ],
        [
            ("What are the three layers?", "Calling policy, voice route or usage, and a block on the carrier or SBC."),
            ("Why a separate usage?", "So the default policy does not inherit it."),
            ("What do you alert on?", "Attempts to forbidden destinations."),
            ("Who is not the canary?", "The one account allowed to dial the world."),
        ],
        ("Configure call routing for Direct Routing", ROUTE),
        ["User", "Voice route", "SBC"],
    ))
    add(topic(
        "tm-sbc-failover", "SBC failover", "The second gateway has to be on the route",
        "Teams fails over between SBCs that are on the voice route and answering OPTIONS. A powered-on SBC that is not on the route does not receive the call.",
        [
            "List the SBCs on the route in order.",
            "OPTIONS removes a dead SBC from consideration.",
            "Inbound failover is a carrier or SBC problem too. Teams outbound failover does not rewrite the carrier's inbound route.",
            "Test by withdrawing OPTIONS in a lab, not by rebooting a production pair.",
        ],
        "Assuming inbound DIDs fail over because outbound failover worked.",
        [
            "Put two lab SBCs on one route.",
            "Mark one failed by OPTIONS in the exercise.",
            "Place the outbound canary and name the SBC that took it.",
            "Write the separate inbound test.",
        ],
        [
            ("When does Teams skip an SBC?", "When it is not on the route, or OPTIONS has failed."),
            ("Does outbound failover fix inbound?", "No. The carrier's inbound routing is its own design."),
            ("How do you test?", "Withdraw OPTIONS in a lab and place the canary."),
            ("What do you record?", "Which SBC took the call, and the call id."),
        ],
        ("Direct Routing", DR),
        ["Teams", "Primary SBC", "Secondary SBC"],
    ))
    add(topic(
        "tm-cqd", "Call Quality Dashboard", "Trends, not one ticket",
        "Call Quality Dashboard shows trends across many Teams calls. It is how you see a building or a subnet. It is a poor tool for the one call a user placed five minutes ago. That call belongs in Call Analytics.",
        [
            "Filter to a site or a subnet before you conclude the tenant is unhealthy.",
            "Date the report. CQD is not real-time.",
            "A quality drop after a firewall change is a hypothesis until you join a call id.",
            "Export the filter with the chart.",
        ],
        "Opening CQD for a single dropped call and declaring it empty, so the network is fine.",
        [
            "Name a lab subnet you would filter on.",
            "Write one trend question CQD can answer.",
            "Write one question it cannot answer: this user's last call.",
            "Point that second question at Call Analytics.",
        ],
        [
            ("What is CQD for?", "Quality trends across many calls."),
            ("What is it not for?", "One recent call. Use Call Analytics."),
            ("Why filter to a site?", "A tenant average hides a bad building."),
            ("Why date the report?", "CQD lags. It is not a live probe."),
        ],
        ("Teams Phone", PHONE),
        ["Many clients", "CQD", "Site"],
    ))
    add(topic(
        "tm-call-analytics", "Call Analytics", "One call, one user",
        "Call Analytics opens one user's calls and shows the legs, the client, and the network measurements Microsoft recorded. It is the tool for a ticket. CQD remains the tool for a trend.",
        [
            "Start with the user and the time.",
            "Separate the caller leg and the callee leg.",
            "A VPN or a guest network shows up here more honestly than in a WAN graph.",
            "The Teams call id is what you ask the SBC engineer to find, if that id is passed. If it is not, say so.",
        ],
        "Averaging Call Analytics across a day and calling that CQD.",
        [
            "Pick a lab user and a lab call time.",
            "Write the two legs.",
            "Write one network fact you would believe from this tool.",
            "Write the SBC evidence you still want.",
        ],
        [
            ("Who is Call Analytics about?", "One user and that user's calls."),
            ("How is that different from CQD?", "CQD is a trend across the tenant or a site."),
            ("What do you still capture on Direct Routing?", "The SBC ladder, because Analytics does not replace a SIP trace."),
            ("What network fact is useful?", "The client network Microsoft recorded, including a VPN."),
        ],
        ("Teams Phone", PHONE),
        ["User", "Call Analytics", "SBC"],
    ))
    add(topic(
        "tm-sbc-certificate", "The SBC certificate matches the paired FQDN", "TLS fails before OPTIONS if the name is wrong",
        "Direct Routing trusts the SBC by the FQDN you pair. That name has to be on the certificate the SBC presents, issued by a public CA Microsoft documents as supported.",
        [
            "The paired FQDN is the name Teams dials and the name it expects in the certificate.",
            "A name mismatch fails the TLS handshake. SIP OPTIONS never gets a chance to succeed.",
            "Renew the certificate before it expires and keep the same FQDN.",
            "A new name is a new pairing problem, not a routine renewal.",
        ],
        "Renewing onto a different common name and expecting the existing pairing to follow.",
        [
            "Write the FQDN you would pair in a lab, using a name you control.",
            "Write which certificate field must contain it.",
            "Write the symptom of a name mismatch: handshake failure, not a SIP error code.",
            "Write the renewal rule: same name, new dates.",
        ],
        [
            ("What name does Teams expect on the SBC certificate?", "The FQDN you paired."),
            ("What happens on a name mismatch?", "TLS fails before OPTIONS can succeed."),
            ("Who issues the certificate?", "A public CA that Microsoft documents as supported."),
            ("What stays the same across a renewal?", "The paired FQDN."),
        ],
        ("Direct Routing", DR),
        ["Teams", "TLS", "SBC"],
    ))
    add(topic(
        "tm-network-sites", "Trusted IPs and network sites", "Local media optimization has to know where the client is",
        "Local media optimization uses the trusted IPs and network sites you define. A client whose address does not match a site is not treated as internal, and a VPN can make a remote user look local.",
        [
            "A trusted IP tells Teams which addresses belong to your network.",
            "A site ties a subnet to a place so media can stay at the branch.",
            "VPN clients often present a datacenter address and break that calculation.",
            "When local media optimization and location-based routing are both on, a downstream SBC needs GatewaySiteLbrEnabled.",
        ],
        "Turning on media bypass and skipping the site table.",
        [
            "Sketch one branch subnet and one VPN pool.",
            "Mark which one you would list as a trusted internal site.",
            "Write what Teams will think the VPN user is.",
            "Write the downstream SBC flag you set when location-based routing is also on.",
        ],
        [
            ("What are trusted IPs for?", "They mark addresses that belong to your network."),
            ("Why do VPN users confuse the calculation?", "They present an address that is not the branch they are sitting in."),
            ("What must exist before branch media can stay local?", "A site that matches the client."),
            ("When do you set GatewaySiteLbrEnabled?", "When local media optimization and location-based routing are both on, on the downstream SBC."),
        ],
        ("Local media optimization", LMO),
        ["Client", "Site", "SBC"],
    ))
    add(topic(
        "tm-call-forwarding", "Call forwarding is a user setting", "The route still has to exist for a PSTN target",
        "Forwarding is configured for the user. It is not a voice routing policy. When the target is a PSTN number, the forwarded call still has to match a voice route.",
        [
            "Immediate, unanswered, and simultaneous treatments are user settings.",
            "A forward to another Teams user stays inside Teams.",
            "A forward to the PSTN needs a usage and a route for that destination.",
            "The forwarded leg has its own record. Keep both call ids.",
        ],
        "Adding a voice route because one user forwarded their phone.",
        [
            "On a lab user, set forward-unanswered to a second lab user.",
            "Call the first user and let it forward. Record both ids.",
            "Point a second test at a synthetic PSTN pattern and write whether a route exists.",
            "Remove the forward and confirm the user rings again.",
        ],
        [
            ("Is forwarding a voice routing policy?", "No. It is a user setting."),
            ("When does a forward need a voice route?", "When the target is a PSTN number."),
            ("What do you file?", "The original call id and the forwarded leg."),
            ("What is the rollback?", "Clear the forward and confirm the user rings."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "User", "Target"],
    ))
    add(topic(
        "tm-music-on-hold", "Music on hold follows whoever holds", "Teams file or SBC treatment",
        "When a Teams user holds a call, the organization music-on-hold file can play. When the SBC holds the caller instead, the caller hears the SBC treatment. Those are different evidence.",
        [
            "The Teams admin center stores the organization music file.",
            "A Teams-side hold is a successful hold, not a dropped call.",
            "An SBC-side hold plays whatever the SBC is configured to play.",
            "Use a file the admin center accepts. Do not invent a bitrate in the ticket.",
        ],
        "Replacing the SBC hold file because the Teams music did not play, without asking which hop held the call.",
        [
            "Place a lab call and hold it from the Teams client.",
            "Write what the caller heard.",
            "If you have an SBC, hold from the SBC and write the difference.",
            "Note the hold signaling you saw, then resume and confirm two-way audio.",
        ],
        [
            ("Who plays music when the Teams user holds?", "Teams, from the organization file."),
            ("Who plays music when the SBC holds?", "The SBC."),
            ("Is a hold a failed call?", "No. It is a treatment. Resume should restore audio."),
            ("What do you check before you replace a file?", "Which hop placed the call on hold."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Teams", "SBC"],
    ))
    add(topic(
        "tm-call-park", "Call park is an orbit", "Not a transfer and not a queue",
        "Call park places a live call on an orbit so another user can retrieve it. It does not select an agent, and it is not a blind transfer.",
        [
            "The parker puts the call on an orbit and can leave.",
            "A second user retrieves by the orbit number.",
            "If the orbit times out, the call returns. Record the timer.",
            "A return is the same call coming back, not a new inbound from the carrier.",
        ],
        "Opening a carrier ticket because a parked call came back to the parker.",
        [
            "Place a lab call and park it.",
            "Retrieve it from a second lab user.",
            "Park again and let the timer expire. Record where it rang.",
            "Write one sentence on how this differs from the call queue lesson.",
        ],
        [
            ("What is an orbit?", "The number where a parked call waits."),
            ("How does park differ from a queue?", "A queue selects an agent. Park waits for someone who knows the orbit."),
            ("What does a timeout mean?", "The call returns. It is not a new carrier call."),
            ("What do you record?", "The orbit, the timer, and who retrieved it."),
        ],
        ("Teams Phone", PHONE),
        ["Parker", "Orbit", "Retriever"],
    ))
    add(topic(
        "tm-dtmf-relay", "DTMF has to survive the SBC", "Audio can work while digits do not",
        "A caller who hears prompts but cannot enter digits is a DTMF relay problem. Teams and the SBC have to use the same method. Media bypass does not choose it for you.",
        [
            "Telephone events in RTP, RFC 4733, are the usual relay.",
            "SIP INFO is a different method. Both ends must agree.",
            "Two-way audio does not prove digits work.",
            "A bypassed media path still has to carry the relay you chose.",
        ],
        "Blaming media bypass for every failed PIN entry.",
        [
            "Place a lab call to a prompt that asks for digits.",
            "Enter a short lab code and write whether the far end received it.",
            "On the SBC, write which relay the trunk uses.",
            "Repeat on the media path you actually deploy, including bypass if that is the design.",
        ],
        [
            ("What is the usual DTMF relay?", "RFC 4733 telephone events in RTP."),
            ("What else might an SBC send?", "SIP INFO. It only works if Teams is using that method too."),
            ("Does working audio prove digits?", "No."),
            ("Does media bypass pick the relay?", "No. The relay still has to match on the path you built."),
        ],
        ("Direct Routing considerations", CONSIDER),
        ["Caller", "Teams", "SBC"],
    ))
    add(topic(
        "tm-busy-and-unanswered", "Busy and unanswered are treatments", "Name the layer that produced them",
        "A Teams client that is busy and an SBC that returns 486 Busy Here are different facts. Unanswered treatment, voicemail or a forward, is configured for the user or the queue.",
        [
            "Do not disturb and a busy client are user state.",
            "486 on the Direct Routing leg is a SIP response from the SBC or beyond it.",
            "Unanswered treatment belongs to the user, the queue, or voicemail.",
            "Write the layer before you open a carrier ticket.",
        ],
        "Reading every busy tone as a carrier failure.",
        [
            "Set a lab user to do not disturb and call them. Record the treatment.",
            "Clear it and let a call ring out. Record the unanswered treatment.",
            "If an SBC is in the path, note any SIP response on that leg.",
            "Write one sentence that names the layer.",
        ],
        [
            ("Is do not disturb a trunk failure?", "No. It is user state."),
            ("What is a 486?", "Busy Here, a SIP response. Record which hop sent it."),
            ("Who owns unanswered treatment?", "The user, the queue, or voicemail, depending on what you configured."),
            ("What do you write in the ticket?", "The layer that produced the treatment."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Teams", "SBC"],
    ))
    add(topic(
        "tm-transform-once", "Normalize once", "Teams dial plan, then the SBC",
        "Teams normalizes the number the user dialed before a voice route compares its pattern. An SBC translation that strips or adds digits again changes the request URI a second time.",
        [
            "Normalization runs in Teams, before the route match.",
            "The voice route sees the normalized number.",
            "The SBC Request-URI should be that number unless you meant to transform again.",
            "If the two differ, name the rule that changed them.",
        ],
        "Stripping the same prefix in the dial plan and again on the SBC.",
        [
            "Pick a lab pattern, such as a national number with a prefix your dial plan removes.",
            "Write the normalized form Teams should send.",
            "Write the Request-URI you expect on the SBC.",
            "If they differ in a trace, circle the second rule and decide which hop owns the transform.",
        ],
        [
            ("When does Teams normalize?", "Before the voice route pattern is compared."),
            ("What should the SBC Request-URI match?", "The normalized number, unless a later rule is intentional."),
            ("What is a double transform?", "Teams and the SBC both changing the same digits."),
            ("What do you capture?", "The normalized number in Teams and the Request-URI on the INVITE."),
        ],
        ("Voice routing", ROUTE),
        ["User", "Dial plan", "SBC"],
    ))
    add(topic(
        "tm-unassigned-number", "Unassigned numbers need a treatment", "A DID you own is not a user",
        "A number in the tenant that is not assigned to a user can be sent to a resource account. Leaving it unassigned does not make it ring someone, and it is not a voice route.",
        [
            "Assignment is what makes a DID ring a user.",
            "An unassigned-number treatment can point at an auto attendant or an announcement.",
            "That treatment is not a PSTN usage and not a carrier route.",
            "Test with a lab number you have not given to a person.",
        ],
        "Porting a block and assuming every number in the block rings a user.",
        [
            "List one lab DID you will not assign.",
            "Write the resource account that should answer it.",
            "Call it and record where it landed.",
            "Assign it to a lab user, call again, and write the difference.",
        ],
        [
            ("Does an owned DID ring a user by itself?", "No. It has to be assigned."),
            ("What can an unassigned treatment target?", "A resource account, such as an auto attendant or an announcement."),
            ("Is that treatment a voice route?", "No."),
            ("How do you prove it?", "Call the lab number before and after assignment."),
        ],
        ("Teams Phone", PHONE),
        ["Caller", "Number", "Resource account"],
    ))
    add(topic(
        "tm-lab-canary", "The Teams canary", "One DID you call from outside",
        "A Teams Phone canary is a DID you call from a network you do not operate, plus an outbound call that matches the voice route you just changed. OPTIONS staying up is necessary and not sufficient.",
        [
            "Inbound proves the carrier and the number assignment.",
            "Outbound proves the policy, the usage, and the route.",
            "OPTIONS can stay successful while the route matches nothing.",
            "File the Teams call record and the SBC Call-ID.",
        ],
        "Using an on-net Teams-to-Teams call as the only canary.",
        [
            "Choose a lab DID and a lab outbound pattern.",
            "Call inbound from outside the tenant.",
            "Call outbound from the canary user.",
            "File both records next to the change. Note that OPTIONS still succeeds.",
        ],
        [
            ("Why must the inbound canary come from outside?", "Teams-to-Teams calls skip the carrier and the SBC."),
            ("What does outbound prove?", "The voice routing policy, the usage, and the route."),
            ("Why is OPTIONS not enough?", "The SBC can answer probes and still match no number."),
            ("What do you file?", "The Teams call record and the SBC Call-ID."),
        ],
        ("Direct Routing", DR),
        ["Outside caller", "Canary DID", "SBC"],
    ))
    add(topic(
        "tm-interview-traps", "Teams Phone interview traps", "Name the PSTN path first",
        "The interview answer starts with Calling Plan, Operator Connect, or Direct Routing. Ports, policies, and emergency fall out of that choice. A CUCM route-pattern story is the wrong opening.",
        [
            "Pairing is not a voice route. OPTIONS is not a dial plan.",
            "A calling policy is not a voice routing policy.",
            "Media bypass does not move signaling off Microsoft.",
            "SBA does not keep dynamic emergency location sharing.",
        ],
        "Drawing one SBC and saying Teams is basically CUCM with a cloud skin.",
        [
            "In 60 seconds, define Direct Routing.",
            "In 60 seconds, define a PSTN usage.",
            "Name the emergency object that is only for Direct Routing.",
            "Name the document you would open before quoting a port.",
        ],
        [
            ("What are the three PSTN paths?", "Calling Plans, Operator Connect, and Direct Routing."),
            ("What does pairing not prove?", "That any particular number is routed to that SBC."),
            ("Which policy contains PSTN usages?", "The online voice routing policy."),
            ("What does media bypass leave in place?", "Signaling through Teams."),
        ],
        ("Direct Routing", DR),
        ["Candidate", "Diagram", "Evidence"],
    ))
    add(topic(
        "tm-capstone-quiz", "Teams Phone capstone", "Eight checks before you call the path done",
        "This quiz closes the Teams Phone path. Answer first, then open the card. Misses become a LICC line.",
        [
            "The PSTN path is a choice you can say out loud.",
            "Usages join policies to routes.",
            "Normalization happens before the route.",
            "Emergency and SBA have documented limits.",
        ],
        "Treating a green OPTIONS probe as a finished dial plan.",
        [
            "Answer all eight before you expand a card.",
            "Write LICC for the one you missed.",
            "Place one lab canary if you have a tenant. Otherwise write the canary you would place.",
            "Date the Direct Routing plan article.",
        ],
        [
            ("What do you assign to a user for Direct Routing outbound?", "An online voice routing policy."),
            ("What joins that policy to a route?", "A PSTN usage."),
            ("When does normalization run?", "Before the voice route pattern is compared."),
            ("What probe marks an SBC down?", "SIP OPTIONS."),
            ("Does media bypass move SIP signaling?", "No."),
            ("Who uses an emergency call routing policy?", "Direct Routing, not Calling Plan users."),
            ("What does an SBA banner mean?", "The client is in appliance mode. No banner means it is not."),
            ("What is Call Analytics for, compared with CQD?", "One user. CQD is the trend."),
        ],
        ("Direct Routing", DR),
        ["You", "Teams", "SBC"],
    ))
    return rows


def js_json(value: object) -> str:
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace("</", "<\\/")


def parse_js(text: str, marker: str):
    index = text.index(marker) + len(marker)
    value, _end = json.JSONDecoder().raw_decode(text[index:])
    return value


def body_html(item: dict) -> str:
    points = "".join(f"<li>{escape(point)}</li>" for point in item["points"])
    steps = "".join(f"<li>{escape(step)}</li>" for step in item["lab"])
    cards = []
    for number, (prompt, answer) in enumerate(item["quiz"], start=1):
        cards.append(
            f'<details class="q"><summary>Q{number}. {escape(prompt)}</summary>'
            f"<p>{escape(answer)}</p></details>"
        )
    cite_title, cite_href = item["cite"]
    return (
        f'<p class="lede">{escape(item["lead"])}</p>'
        f'<div class="card teal"><h2>How it works</h2><ul>{points}</ul></div>'
        f'<div class="card rose"><h2>Interview trap</h2><p>{escape(item["trap"])}</p></div>'
        f'<div class="card blue"><h2>Lab</h2><p>Use lab numbers only. Do not paste a production dial plan or a real caller into the notes.</p><ol>{steps}</ol></div>'
        f'<div class="card green"><h2>Check yourself</h2>{"".join(cards)}</div>'
        f'<p class="cite-line">Source: <a href="{escape(cite_href)}">{escape(cite_title)}</a>. '
        f"Re-read it for the release you run before you change production. RFC 3261 is the SIP baseline when the lesson shows a ladder.</p>"
    )


def flow(item: dict, failed: bool) -> dict:
    actors = item["actors"]
    if failed:
        steps = [
            {"f": 0, "t": 1, "label": "Attempt", "kind": "req", "cap": item["trap"]},
            {"f": 1, "t": 0, "label": "Reject", "kind": "err", "cap": item["points"][0]},
            {"f": 0, "t": 1, "label": "Retry", "kind": "note", "cap": item["points"][1]},
            {"f": 1, "t": 0, "label": "Timeout", "kind": "err", "cap": "A timeout and a SIP error are different evidence. Record which one you saw."},
        ]
        flow_id = "fail-" + item["id"]
        title = item["title"] + " — failure"
        pair = ["sec-" + item["id"]]
    else:
        steps = [
            {"f": 0, "t": 1, "label": "Setup", "kind": "req", "cap": item["points"][0]},
            {"f": 1, "t": 2, "label": "Policy", "kind": "note", "cap": item["points"][1]},
            {"f": 2, "t": 1, "label": "200 OK", "kind": "ok", "cap": item["points"][2]},
            {"f": 0, "t": 2, "label": "Media", "kind": "media", "cap": item["points"][3]},
            {"f": 0, "t": 1, "label": "BYE", "kind": "bye", "cap": item["lead"]},
        ]
        flow_id = "sec-" + item["id"]
        title = item["title"]
        pair = ["fail-" + item["id"]]
    packets = []
    links = []
    for number, step in enumerate(steps, start=1):
        packets.append({
            "n": number,
            "src": actors[step["f"]],
            "dst": actors[step["t"]],
            "msg": step["label"],
            "note": step["cap"],
        })
        links.append({"a": step["f"], "b": step["t"], "label": step["label"]})
    cite_title, _href = item["cite"]
    return {
        "id": flow_id,
        "title": title,
        "why": item["lead"],
        "cite": cite_title + " and RFC 3261",
        "layout": "ladder",
        "actors": actors,
        "chart": "queue-depth",
        "icon": "cloud",
        "keys": [[actors[1], "Join the logs on this hop"], ["LICC", "Leg, id, counter, capture"]],
        "header": "invite",
        "audio": False,
        "steps": steps,
        "walkthrough": False,
        "headerLines": [
            "INVITE sip:lab.example SIP/2.0",
            "Via: SIP/2.0/TLS lab.example;branch=z9hG4bK-lab",
            "From: Alice;tag=from-a",
            "To: Bob",
            "Call-ID: lab-" + item["id"],
            "CSeq: 1 INVITE",
        ],
        "scenarios": [flow_id, *pair],
        "art": {
            "topology": {"title": title, "nodes": actors, "links": links},
            "mockup": {"kind": "hub", "title": title, "lines": [item["sub"], item["trap"][:180], "prove: " + steps[0]["label"]]},
            "capture": {"title": title, "packets": packets},
        },
        "sectionId": item["id"],
    }


def illustration_count(flows: list[dict]) -> int:
    seen: set[str] = set()
    for item in flows:
        art = item.get("art") or {}
        for key in ("topology", "mockup", "capture"):
            if art.get(key):
                seen.add(key + ":" + json.dumps(art[key], sort_keys=True))
    return len(seen)


def main() -> int:
    manifest = parse_js(MANIFEST.read_text(encoding="utf-8"), "UC.manifest(")
    existing = {item["id"] for item in manifest["sections"]}
    fresh = {"webex": webex(), "teams": teams()}
    for journey, items in fresh.items():
        ids = [item["id"] for item in items]
        if len(ids) != len(set(ids)):
            raise SystemExit(f"duplicate ids in {journey}")
        overlap = existing.intersection(ids)
        if overlap:
            raise SystemExit(f"ids already exist: {sorted(overlap)[:5]}")
        floor = 45 if journey == "teams" else 43
        if len(items) < floor:
            raise SystemExit(f"{journey} expansion is too small: {len(items)} (need {floor})")
    group = "Webex Calling and Teams Phone"
    track = "cloud-calling"
    additions = []
    for journey, items in fresh.items():
        prefix = "WX" if journey == "webex" else "TM"
        for number, item in enumerate(items, start=1):
            body = body_html(item)
            section = {
                "id": item["id"],
                "num": f"{prefix}{number:02d}",
                "group": group,
                "title": item["title"],
                "sub": item["sub"],
                "body": body,
            }
            flows = [flow(item, False), flow(item, True)]
            payload = "UC.pack(" + js_json(section) + "," + js_json(flows) + ");\n"
            (SECTIONS / f"{item['id']}.js").write_text(payload, encoding="utf-8")
            additions.append((journey, {
                "id": item["id"],
                "num": section["num"],
                "group": group,
                "title": item["title"],
                "sub": item["sub"],
                "kind": "",
                "journey": journey,
                "track": track,
                "flow": "sec-" + item["id"],
                "walks": [],
                "blurb": item["lead"][:180],
                "cards": body.count("<details"),
            }))
    catalog = manifest["sections"]
    for journey in ("teams", "webex"):
        block = [record for name, record in additions if name == journey]
        index = next(i for i, row in enumerate(catalog) if row.get("journey") == journey)
        catalog[index:index] = block
    counts = Counter(row["journey"] for row in catalog)
    group_counts = Counter(row["group"] for row in catalog)
    for row in manifest["groups"]:
        row["count"] = group_counts[row["name"]]
    manifest["stats"]["sections"] = len(catalog)
    manifest["stats"]["journeys"] = {
        "cisco-voice": counts["cisco-voice"],
        "webex": counts["webex"],
        "teams": counts["teams"],
        "contact-center": counts["contact-center"],
    }
    all_flows = []
    details = self_checks = numbered = 0
    for row in catalog:
        section, flows = parse_pack((SECTIONS / f"{row['id']}.js").read_text(encoding="utf-8"))
        all_flows.extend(flows)
        body = section.get("body") or ""
        details += body.count("<details")
        self_checks += body.count('<details class="q"')
        numbered += len(re.findall(r"\bQ\d+\.", body))
    walks = parse_js((CURRICULUM / "walks.js").read_text(encoding="utf-8"), "UC.walks(")
    all_flows.extend(walks)
    manifest["stats"]["flows"] = len(all_flows)
    manifest["stats"]["illustrations"] = illustration_count(all_flows)
    manifest["stats"]["details"] = details
    manifest["stats"]["selfChecks"] = self_checks
    manifest["stats"]["numberedQuestions"] = numbered
    MANIFEST.write_text("UC.manifest(" + js_json(manifest) + ");\n", encoding="utf-8")
    INTEGRITY.write_text(json.dumps({
        "version": "v21",
        "sections": manifest["stats"]["sections"],
        "flows": manifest["stats"]["flows"],
        "walkthroughs": manifest["stats"]["walkthroughs"],
        "charts": manifest["stats"]["charts"],
        "illustrations": manifest["stats"]["illustrations"],
        "audioClips": manifest["stats"]["audioClips"],
        "trackHubs": manifest["stats"]["trackHubs"],
        "groups": manifest["stats"]["groups"],
        "details": details,
        "selfChecks": self_checks,
        "numberedQuestions": numbered,
        "faults": manifest["stats"]["faults"],
        "drills": manifest["stats"]["drills"],
        "journeys": manifest["stats"]["journeys"],
    }, indent=2) + "\n", encoding="utf-8")
    home_path = SECTIONS / "home.js"
    home_text = home_path.read_text(encoding="utf-8")
    home_section, home_flows = parse_pack(home_text)
    home_section["body"] = home_section["body"].replace(
        "<b>476</b><span>Sections in v21</span>",
        f"<b>{manifest['stats']['sections']}</b><span>Sections in v21</span>",
        1,
    )
    home_path.write_text("UC.pack(" + js_json(home_section) + "," + js_json(home_flows) + ");\n", encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    html = re.sub(r'("sections":)\d+', rf"\g<1>{manifest['stats']['sections']}", html, count=1)
    HTML.write_text(html, encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    replacements = {
        "sections": manifest["stats"]["sections"],
        "flows": manifest["stats"]["flows"],
        "illustrations": manifest["stats"]["illustrations"],
        "details": details,
        "selfChecks": self_checks,
        "numberedQuestions": numbered,
    }
    for key, value in replacements.items():
        checker, n = re.subn(rf'("{key}": )\d+', rf"\g<1>{value}", checker, count=1)
        if n != 1:
            raise SystemExit(f"checker key not updated: {key}")
    CHECKER.write_text(checker, encoding="utf-8")
    print(json.dumps(manifest["stats"], indent=2))
    return 0


def parse_pack(text: str):
    marker = "UC.pack("
    index = text.index(marker) + len(marker)
    section, end = json.JSONDecoder().raw_decode(text[index:])
    rest = text[index + end:].lstrip()
    if rest.startswith(","):
        rest = rest[1:]
    flows, _end = json.JSONDecoder().raw_decode(rest)
    return section, flows


if __name__ == "__main__":
    raise SystemExit(main())
