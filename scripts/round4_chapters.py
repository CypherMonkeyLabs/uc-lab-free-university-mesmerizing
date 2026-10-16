"""Rooms and drawings for emergency calling, recording, and open-telephony bridges.

Facts in these rows come from pages opened in 2026-10. A confirm row in the
source catalog has no URL.
"""
from __future__ import annotations

FCC = (
    "FCC, Kari's Law and RAY BAUM'S Act for multi-line telephone systems",
    "https://www.fcc.gov/mlts-911-requirements",
)
CER = (
    "Cisco Emergency Responder product support",
    "https://www.cisco.com/c/en/us/support/unified-communications/emergency-responder/series.html",
)
CER_PLAN = (
    "Plan for Cisco Emergency Responder, Release 15",
    "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cer/15/english/administration/guide/cer0_b_cisco-emergency-responder-administration-guide-15/cer0_b_cisco-emergency-responder-administration-guide-1401_chapter_01.html",
)
CER_CUCM = (
    "Configure Cisco Unified Communications Manager, Emergency Responder 15",
    "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cer/15/english/administration/guide/cer0_b_cisco-emergency-responder-administration-guide-15/cer0_b_cisco-emergency-responder-administration-guide-1401_chapter_011.html",
)
CER_ADMIN = (
    "Cisco Emergency Responder Administration Guide, Release 15",
    "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cer/15/english/administration/guide/cer0_b_cisco-emergency-responder-administration-guide-15.html",
)
WIKI_E911 = ("Enhanced 911 (Wikipedia)", "https://en.wikipedia.org/wiki/Enhanced_9-1-1")
CUCM_REC = (
    "Feature Configuration Guide for CUCM, Release 15, Recording",
    "https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15/cucm_mp_r53f7ff4_00_recording-12-0.html",
)
CUCM_REC_BASIC = (
    "Configure and troubleshoot basic call recording",
    "https://www.cisco.com/c/en/us/support/docs/unified-communications/unified-communications-manager-callmanager/200788-Call-Recording-Basic-Configuration-and-T.html",
)
CUBE_SIPREC = (
    "CUBE configuration guide, SIP forking (IOS XE 17.6 onwards)",
    "https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/voice/cube/ios-xe/config/ios-xe-book/m_voi-cube-sip-rec-recorder.html",
)
RFC7245 = (
    "RFC 7245, architecture for media recording using SIP",
    "https://www.rfc-editor.org/rfc/rfc7245",
)
RFC7865 = ("RFC 7865, SIP recording metadata", "https://www.rfc-editor.org/rfc/rfc7865")
RFC7866 = ("RFC 7866, session recording protocol", "https://www.rfc-editor.org/rfc/rfc7866")
RFC3261 = ("RFC 3261, SIP", "https://www.rfc-editor.org/rfc/rfc3261")
RFC3550 = ("RFC 3550, RTP", "https://www.rfc-editor.org/rfc/rfc3550")
RFC7118 = ("RFC 7118, SIP over WebSocket", "https://www.rfc-editor.org/rfc/rfc7118")
RFC8825 = ("RFC 8825, WebRTC protocol overview", "https://www.rfc-editor.org/rfc/rfc8825")
RFC8829 = ("RFC 8829, JavaScript session establishment", "https://www.rfc-editor.org/rfc/rfc8829")
WIKI_TRUNK = ("SIP trunking (Wikipedia)", "https://en.wikipedia.org/wiki/SIP_trunking")
SIPCONNECT = ("SIPconnect technical recommendation", "https://www.sipforum.org/technology/sipconnect/")
WIKI_AST = ("Asterisk (Wikipedia)", "https://en.wikipedia.org/wiki/Asterisk_(PBX)")
AST_MOD = (
    "Types of Asterisk modules",
    "https://docs.asterisk.org/Fundamentals/Asterisk-Architecture/Types-of-Asterisk-Modules/",
)
AST_PJSIP = (
    "Configuring res_pjsip",
    "https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/",
)
WIKI_FS = ("FreeSWITCH (Wikipedia)", "https://en.wikipedia.org/wiki/FreeSWITCH")
FS_MANUAL = ("FreeSWITCH users manual", "https://developer.signalwire.com/freeswitch/")
WIKI_WEBRTC = ("WebRTC (Wikipedia)", "https://en.wikipedia.org/wiki/WebRTC")
W3C = ("W3C WebRTC recommendation", "https://www.w3.org/TR/webrtc/")
CUCM = (
    "Cisco Unified Communications Manager product support",
    "https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html",
)


def extra_flows() -> list[tuple]:
    return [
        (
            "cer-callback",
            "Emergency call and PSAP callback",
            ["Phone", "CUCM", "CER", "PSAP"],
            [(0, 1, "911"), (1, 2, "route"), (2, 3, "ELIN"), (3, 2, "callback"), (2, 0, "original phone")],
        ),
        (
            "cer-unlocated",
            "Phone on a switch CER does not know",
            ["Phone", "Switch", "CER"],
            [(0, 1, "link"), (2, 1, "SNMP"), (1, 2, "no ERL")],
        ),
        (
            "recording-fork",
            "Phone built-in bridge fork",
            ["Phone", "CUCM", "Recorder"],
            [(0, 1, "call"), (0, 2, "fork near"), (0, 2, "fork far")],
        ),
        (
            "siprec-session",
            "CUBE as a recording client",
            ["CUCM", "CUBE", "Recorder"],
            [(0, 1, "call"), (1, 2, "INVITE siprec"), (2, 1, "200"), (1, 2, "RTP copy")],
        ),
        (
            "pbx-trunk",
            "SIP trunk to another PBX",
            ["CUCM", "CUBE", "Asterisk"],
            [(0, 1, "INVITE"), (1, 2, "INVITE"), (2, 1, "200"), (1, 0, "200")],
        ),
        (
            "webrtc-gateway",
            "Browser media across a gateway",
            ["Browser", "Gateway", "CUCM"],
            [(0, 1, "WebRTC"), (1, 2, "SIP"), (2, 1, "200"), (1, 0, "answer")],
        ),
    ]


def extra_arches() -> list[tuple]:
    return [
        (
            "erl-map",
            "Switch port, ERL, and ELIN",
            ["Port", "ERL", "ELIN", "ALI"],
            [
                "CER assigns an ERL to the switch port, then an ELIN for that ERL.",
                "The Release 15 plan says a moved patch cord can point the port at the wrong ERL.",
            ],
        ),
        (
            "record-sources",
            "Where the copy of the audio starts",
            ["Phone BiB", "Gateway", "SIPREC"],
            [
                "CUCM 15 documents phone-based and network-based recording.",
                "A score or a pause is not the same object as the media file.",
            ],
        ),
        (
            "open-neighbors",
            "Neighbors on a SIP trunk",
            ["CUCM", "CUBE", "Asterisk", "FreeSWITCH"],
            [
                "Each box keeps its own dial plan.",
                "A shared codec list is not a shared feature set.",
            ],
        ),
    ]


def extra_rooms() -> list[dict]:
    return [
        dict(
            id="T9-R01",
            track="T9",
            slug="emergency-direct",
            title="Direct dial, notification, and location",
            diagram="cer-callback",
            sheet="e911",
            five=[
                "This page is study material, not legal advice and not an emergency plan.",
                "The FCC page opened for this lab says Kari's Law requires direct 911 dialing on covered multi-line systems, without a prefix such as 9.",
                "The same page says notification must not delay the 911 call, and must include that a 911 call was made, a callback number, and the location the system sends, unless that information is technically infeasible.",
                "Section 506 of RAY BAUM'S Act, as the FCC page describes it, is about dispatchable location: a validated street address plus detail such as a suite or apartment.",
                "Enhanced 911, in the Wikipedia article opened here, is the North American system that delivers a caller's location to the dispatcher. Other regions use other numbers.",
            ],
            core="The FCC's multi-line telephone system page, opened in 2026-10, says the Commission adopted rules in August 2019 for Kari's Law and Section 506 of RAY BAUM'S Act. Kari's Law and those rules are forward-looking: the page says they apply to systems manufactured, imported, first sold or leased, or installed after February 16, 2020, with a direct-dial and notification date of February 17, 2020 for those systems. Dispatchable location for on-premises fixed devices is dated January 6, 2021 on that page, and on-premises non-fixed plus off-premises devices January 6, 2022, with alternatives when automated dispatchable location is not technically feasible. A lab route pattern is not that configuration. Confirm the rule where the site operates. The congress.gov bill page did not open past a challenge, so this lab does not link it.",
            example="A hotel phone that only dials 911 after a 9 will fail the direct-dial idea the FCC page describes, even if a test call with the prefix reaches a dispatcher. The study question is whether a station can dial 911 with no extra digit, and whether a person likely to see or hear a notice is told at the same time. The location string that rides with the call is a separate question.",
            quiz=[
                (
                    "Kari's Law, as the FCC page describes it, is satisfied by requiring users to dial 9 before 911.",
                    "False. The page says direct dialing means no prefix or access code such as 9.",
                    ["True", "False"],
                    "False",
                ),
                (
                    "This lab page is legal advice for every country.",
                    "False. It is a study note about pages that were opened. Confirm the rule where you operate.",
                    ["True", "False"],
                    "False",
                ),
            ],
            sources=[FCC, WIKI_E911],
            glossary=[
                ("MLTS", "A multi-line telephone system, the term the FCC page uses for enterprise and hotel phone systems."),
                ("Dispatchable location", "The FCC page's term for a validated street address plus detail needed to find the caller."),
            ],
            config="Write the digits a real station dials for emergency, and who is supposed to see the notice. Do not invent a prefix.",
            trouble="If the only successful test used an access code, you have not tested direct dial.",
            bridge="CUCM can route 911, but routing is not the same as location. Cisco Emergency Responder is the location product in the next room.",
            confirm="Confirm the emergency number, the statute, and the carrier outside the FCC page. This lab did not open those texts.",
        ),
        dict(
            id="T9-R02",
            track="T9",
            slug="cer-erl-elin",
            title="Emergency Responder, ERL, and ELIN",
            diagram="erl-map",
            sheet="e911",
            five=[
                "Cisco Emergency Responder is a separate product. The support page opened here lists Release 15 as available, with a release date of 16 October 2023.",
                "The Release 15 planning chapter says Emergency Responder queries Unified CM for registered phones, then queries switches to learn the port.",
                "An ERL is assigned to a switch port from the location of the device on that port. The same chapter says moving the patch cord without changing the ERL can send the wrong ELIN.",
                "The CUCM configuration chapter says Emergency Responder converts the caller extension to an ELIN used to route the call and to allow PSAP callback.",
                "That chapter says Emergency Responder tracks the extension for an ELIN for up to three hours, and sends a callback with no active mapping to on-site security.",
            ],
            core="Read the three objects in order. The switch port is where the phone was discovered. The emergency response location is the zone you assigned to that port. The ELIN is the callback number the public-safety answering point sees for that zone. The planning chapter says phones on undefined switches show up as unlocated, and new or changed ports need an ERL assignment. Discovery uses SNMP read credentials and a switch-port update. None of that is a dial-plan CSS. The product support page is the index. The administration guide is the book for Release 15. Menu names and limits belong to the release you run.",
            example="A phone moves from a lobby port to a lab port and the patch is not updated. Emergency Responder still has the lobby ERL on the old port mapping. A 911 call can leave with the lobby ELIN. The planning chapter treats that as a wiring change you must reflect, not as a mystery in the carrier.",
            quiz=[
                (
                    "An ELIN is the caller's directory number.",
                    "False. The CUCM chapter describes the ELIN as the number Emergency Responder uses for routing and PSAP callback, mapped back to the extension.",
                    ["True", "False"],
                    "False",
                ),
                (
                    "A phone on a switch Emergency Responder does not know is still located.",
                    "False. The planning chapter calls those phones unlocated.",
                    ["True", "False"],
                    "False",
                ),
            ],
            sources=[CER, CER_PLAN, CER_CUCM, CER_ADMIN],
            glossary=[
                ("ERL", "Emergency response location. The zone Emergency Responder binds to a switch port."),
                ("ELIN", "Emergency location identification number. The callback number sent for that zone."),
            ],
            config="Name the switch, the port, the ERL, and the ELIN before you change a route pattern.",
            trouble="If the phone is unlocated, fix discovery and the port assignment before you open a carrier ticket.",
            bridge="CUCM still needs a pattern that hands the emergency call to Emergency Responder, and translation patterns so a PSAP callback hits the route point the guide describes.",
            confirm="Confirm switch support, SNMP version, and on-premises versus off-premises behavior in the Emergency Responder guide for your release.",
        ),
        dict(
            id="T9-R03",
            track="T9",
            slug="emergency-onsite",
            title="On-site alert, callback, and what this lab will not decide",
            diagram="cer-unlocated",
            sheet="e911",
            five=[
                "The Release 15 administration guide contents include on-site alerts, off-premises users, and a national E911 service provider. Those are different chapters.",
                "PSAP callback is a call into your network on the ELIN. The CUCM chapter says translation patterns exist so Emergency Responder can intercept that call.",
                "A successful outbound 911 test does not prove the callback path.",
                "Wikipedia's Enhanced 911 article separates the caller's number (ANI) from the location database (ALI) on the traditional landline path. An ELIN is how many enterprise designs present a callback number.",
                "Laws, carriers, and remote-worker designs outside the pages opened here stay on a confirm row.",
            ],
            core="Treat notification, location, and callback as three tests. Kari's Law notification, on the FCC page, is a message to people at the site. The ELIN callback is a call from the PSAP. On-site alert in Emergency Responder is the product feature listed in the Release 15 guide. They can all be present and still describe different audiences. Off-premises users and a national service provider are named in that guide's contents. This lab does not restate their limits. Dedicated Instance, Webex Calling, and a branch SRST phone are different places for the same human emergency. Test the path the phone will actually use.",
            example="You place a test call in a window the carrier agreed to. The PSAP, or your test desk, sees an ELIN. You then call that ELIN back. If the call rings a hunt pilot instead of the phone that placed the test, the translation pattern or the Emergency Responder mapping is the next object, not the codec.",
            quiz=[
                (
                    "An outbound 911 test proves PSAP callback.",
                    "False. Callback is a separate call toward the ELIN.",
                    ["True", "False"],
                    "False",
                )
            ],
            sources=[CER_ADMIN, CER_CUCM, FCC, WIKI_E911],
            glossary=[
                ("PSAP", "Public safety answering point. The Wikipedia article describes it as the call center that answers the emergency call."),
                ("On-site alert", "The Emergency Responder notification path named in the Release 15 administration guide."),
            ],
            config="Record the test window, the ELIN you expect, and the extension that should ring on callback.",
            trouble="If callback reaches security after the tracking window, compare the time with the three-hour association the CUCM chapter describes.",
            bridge="SRST and a Webex Calling survivability gateway are different fallback designs. An emergency test belongs on the path that will run when the WAN is down.",
            confirm="Confirm carrier test rules, ALI formatting, and any law that is not the FCC page opened for this lab.",
        ),
        dict(
            id="T10-R01",
            track="T10",
            slug="recording-phone",
            title="Phone fork and network fork",
            diagram="recording-fork",
            sheet="recording",
            five=[
                "The CUCM 15 feature guide says phone-based recording takes media from the phone. The phone forks two streams to the recording server.",
                "The same guide says network-based recording can take media from the phone or the gateway, and the gateway connects to Unified CM over a SIP trunk.",
                "Using the phone as the source requires the built-in bridge. The phone's setting overrides the cluster-wide default when it is not left at default.",
                "The guide says recording can fail if the built-in bridge is on and Media Termination Point Required is checked.",
                "Cisco's basic recording note says a phone outside the managed network cannot use this fork unless it can send RTP to the recorder.",
            ],
            core="A recording is a copy of the media, sent somewhere on purpose. It is not a second conversation and it is not proof the agent heard the caller. CUCM decides the source. The feature guide tells you to prefer the phone or the gateway on the line, then shows a table for when that preference is not what CUCM selects. Multi-fork, in that guide, sends the stream to a CUBE media proxy that can relay it to up to five recording servers. Automatic and selective recording are both named. Read the call flow for the release you run before you change a line.",
            example="An agent phone has the built-in bridge off. The line is set to record from the phone. The call completes and the recorder is empty. The signaling ladder can still show a normal 200. The missing object is the fork, not the dial plan.",
            quiz=[
                (
                    "A 200 OK proves the recorder received both audio directions.",
                    "False. The fork is a separate media path.",
                    ["True", "False"],
                    "False",
                ),
                (
                    "The built-in bridge on one phone always follows the cluster-wide parameter.",
                    "False. The feature guide says the phone setting overrides the cluster default when default is not selected.",
                    ["True", "False"],
                    "False",
                ),
            ],
            sources=[CUCM_REC, CUCM_REC_BASIC, RFC3550],
            glossary=[
                ("Built-in bridge", "The phone feature CUCM uses when the phone itself forks recording media."),
                ("Fork", "A copy of the media stream sent to a recorder."),
            ],
            config="Write phone or gateway as the intended source, and whether the built-in bridge is on.",
            trouble="If the call is fine and the file is silent, compare the recorder address with the SDP of the fork.",
            bridge="A contact-center agent is still a CUCM line for this feature. The quality score lives in another product.",
            confirm="Confirm codec support and secure-recording settings in the feature guide for your CUCM version.",
        ),
        dict(
            id="T10-R02",
            track="T10",
            slug="recording-siprec",
            title="SIPREC and CUBE as the recording client",
            diagram="siprec-session",
            sheet="recording",
            five=[
                "RFC 7245 describes architectures for recording in a SIP environment by sending a copy of a media stream to a recording device.",
                "RFC 7865 describes the metadata the session recording server sees. RFC 7866 is the session recording protocol.",
                "RFC 7866 introduces the siprec option tag. An SRC puts it in Require so a peer that does not support the extension can reject the INVITE.",
                "The CUBE IOS XE 17.6 guide says CUBE acts as the session recording client and any third-party recorder acts as the recording server.",
                "That guide cites RFC 7245 section 3.1.1, and it cites the SIPREC metadata and protocol drafts. Confirm the guide for the release you run.",
            ],
            core="Keep the call and the recording session apart. The human call is one dialog. The recording session is another SIP relationship whose job is to carry a copy and the metadata. RFC 7866 says a recording-aware participant can use the record-aware option and the SDP a=record attribute, and that a participant who is not recording-aware still needs an indication by some other means, such as a tone. The CUBE guide says that if SIPREC is not configured, CUBE falls back to its network-based recording implementation. It also says CUBE supports the siprec option tag and the src feature tag, and does not support the SDP extensions in the protocol draft it cites. Do not tell an operator the draft and the RFC are the same text.",
            example="A recorder answers the recording INVITE and the agent hears the caller. The file has audio and no party names. Metadata is the missing piece RFC 7865 is about. A tone, or the absence of one, is a different requirement from RFC 7866, not a codec problem.",
            quiz=[
                (
                    "The recording INVITE is the same dialog as the call being recorded.",
                    "False. SIPREC is a separate recording session.",
                    ["True", "False"],
                    "False",
                )
            ],
            sources=[RFC7245, RFC7865, RFC7866, CUBE_SIPREC, RFC3261],
            glossary=[
                ("SRC", "Session recording client. The CUBE guide says CUBE takes this role when SIPREC is configured."),
                ("SRS", "Session recording server. RFC 7865 describes metadata from the server's point of view."),
            ],
            config="Name the dial peer toward the recorder and whether the profile says siprec.",
            trouble="If the recorder returns 420 Bad Extension, it rejected the siprec option. That is the RFC 7866 failure, not a WAN drop.",
            bridge="CUCM network-based recording and CUBE SIPREC can both be present. Say which box starts the recording session.",
            confirm="Confirm the metadata draft or RFC your recorder and IOS release actually implement.",
        ),
        dict(
            id="T10-R03",
            track="T10",
            slug="recording-compliance",
            title="Compliance is a reason, not a setting",
            diagram="record-sources",
            sheet="recording",
            five=[
                "RFC 7245 says some environments record every call for regulatory, compliance, and consumer-protection reasons.",
                "That sentence does not name your statute, your retention period, or your consent rule.",
                "A recording file, a quality score, and a pause during a card number are different objects. This lab did not open a payment-card standard.",
                "Notification of recording is part of SIPREC for recording-aware users, and the RFC also allows other indications. Your spoken notice is a local rule.",
                "No privacy statute was opened for this chapter. The confirm row has no link.",
            ],
            core="Use the recording architecture to see whether a copy was made. Use counsel and the rule that applies to the site to decide whether you may make it, how long you keep it, and what you tell the caller. This page will not invent that rule. In a contact center the agent desktop, the CUCM line, and the recorder can disagree: the desktop shows a recording icon while the fork never left the phone, or the file exists while the score was never submitted. Debug the object that failed. UCCE and Webex Contact Center do not become the same recorder because both can sit next to a CUCM.",
            example="A supervisor says the call was not recorded. The phone's built-in bridge forked RTP, and the recorder has a file for that time. The missing object is the quality form, not the RTP. Changing the dial plan will not create the form.",
            quiz=[
                (
                    "RFC 7245 chooses the retention period for your contact center.",
                    "False. It explains recording architectures. It does not set your policy.",
                    ["True", "False"],
                    "False",
                )
            ],
            sources=[RFC7245, RFC7866, CUCM_REC],
            glossary=[
                ("Recording file", "The stored copy of the media."),
                ("Quality score", "A review of a call. It is not the media file."),
            ],
            config="Store the call id, the recorder, and the time next to any claim that a call was recorded.",
            trouble="If legal asks for a call, produce the file you have. Do not describe a score as the audio.",
            bridge="Workforce management forecasts how many people you need. It does not store the audio.",
            confirm="Confirm consent, retention, and any duty to pause a recording with the rule that applies where you operate.",
        ),
        dict(
            id="T11-R01",
            track="T11",
            slug="open-sip-trunk",
            title="A SIP trunk is a peer, not a brand",
            diagram="pbx-trunk",
            sheet="bridges",
            five=[
                "Wikipedia's SIP trunking article describes a SIP service between a provider and a customer's SIP PBX.",
                "The same article says the provider side and the enterprise side are different domains, joined by a SIP trunk.",
                "SIPconnect, on the SIP Forum page opened here, is a technical recommendation for direct IP peering between a SIP PBX and a VoIP provider.",
                "CUCM's trunk, CUBE's dial peers, and the far PBX's own routes are three plans.",
                "RFC 3261 is still the request and the response. A trunk does not replace it.",
            ],
            core="When CUCM sends a call to Asterisk or FreeSWITCH, count dialogs the same way you count them toward a carrier. CUBE in the middle is a B2BUA, so the Call-ID usually changes. Early offer, PRACK, and session timers are negotiation, not a feature of the logo on the box. SIPconnect is a profile the SIP Forum publishes for provider peering. It is not a promise that every open-source PBX implements it. Read the recommendation if you are matching a provider. Read the far PBX's own dial plan if you are matching a lab peer.",
            example="CUCM matches a route pattern and sends INVITE to CUBE. CUBE matches an outbound dial peer and sends a new INVITE to Asterisk. Asterisk's dialplan does not match the digits. The failure is on the third plan. A CUCM DNA trace that stops at the trunk has not seen it.",
            quiz=[
                (
                    "One SIP trunk means both PBXs share one dial plan.",
                    "False. Each side matches the digits with its own rules.",
                    ["True", "False"],
                    "False",
                )
            ],
            sources=[WIKI_TRUNK, SIPCONNECT, RFC3261, CUCM],
            glossary=[
                ("SIP trunk", "The signaling peer between two call agents or between a PBX and a provider."),
                ("SIPconnect", "The SIP Forum's technical recommendation for IP peering with a VoIP provider."),
            ],
            config="Write the CUCM destination, the CUBE dial peer, and the far-side match.",
            trouble="If only one direction fails, compare called-number format on that direction before you change codecs.",
            bridge="A Webex Calling local gateway is this same shape with a different peer. The Webex guide still wins for that peer.",
            confirm="Confirm header, cipher, and fax requirements in the SIPconnect version your provider names.",
        ),
        dict(
            id="T11-R02",
            track="T11",
            slug="asterisk-freeswitch",
            title="Asterisk and FreeSWITCH as the other PBX",
            diagram="open-neighbors",
            sheet="bridges",
            five=[
                "Wikipedia describes Asterisk as a software PBX that connects phones, the PSTN, and VoIP endpoints.",
                "The Asterisk documentation opened here separates module types. Channel drivers are one type. res_pjsip is the SIP channel configuration the same docs link as Configuring res_pjsip.",
                "Wikipedia describes FreeSWITCH as telephony software for real-time audio, video, and text, including SIP and WebRTC.",
                "The FreeSWITCH users manual that opened is the operator book. A Sofia SIP chapter URL redirected to that manual, so this lab links the manual.",
                "Neither product copies a CUCM calling search space. You translate the idea, then you test one call.",
            ],
            core="Asterisk matches calls in a dialplan. FreeSWITCH matches calls in its own dialplan. CUCM matches a partition and a route pattern. The interop skill is to name the digit string on each side of the trunk and the codec each side offered. The Asterisk module page shows channel-driver modules as a category. It does not list your peer's host. The FreeSWITCH manual says its parameters are checked against the project source and the shipped defaults. When a guide and a blog disagree, the guide for the version you installed is the one to follow.",
            example="Asterisk answers a lab INVITE with 488 Not Acceptable Here. CUCM offered a codec the peer's endpoint did not allow. Add a codec both sides list, or remove the one they cannot use. Do not restart CUCM to test a codec the offer already showed.",
            quiz=[
                (
                    "An Asterisk dialplan is a CUCM calling search space.",
                    "False. It is a different object on a different product.",
                    ["True", "False"],
                    "False",
                )
            ],
            sources=[WIKI_AST, AST_MOD, AST_PJSIP, WIKI_FS, FS_MANUAL],
            glossary=[
                ("Dialplan", "The Asterisk or FreeSWITCH rules that match a call. Not a CUCM CSS."),
                ("res_pjsip", "The Asterisk SIP channel stack named in the documentation opened for this lab."),
            ],
            config="Record the version string of the PBX and the one match that should take the test call.",
            trouble="A 401 from the far PBX is authentication. A 404 is a miss in that dialplan. Read the status before you change CUCM.",
            bridge="CUBE can sit between them and still be only a B2BUA. Two ladders remain two ladders.",
            confirm="Confirm the module list and the SIP port in the version you installed. This lab does not copy a sample peer.",
        ),
        dict(
            id="T11-R03",
            track="T11",
            slug="webrtc-bridge",
            title="WebRTC, SIP over WebSocket, and a hosted bridge",
            diagram="webrtc-gateway",
            sheet="bridges",
            five=[
                "Wikipedia describes WebRTC as browser and mobile APIs for real-time audio and video without a plugin.",
                "The W3C WebRTC recommendation is the browser API. RFC 8825 is the IETF overview of the protocol suite those browsers use.",
                "RFC 8829, JSEP, lets a JavaScript application control the signaling plane through RTCPeerConnection. It discusses how that relates to existing signaling protocols.",
                "RFC 7118 carries SIP over a WebSocket so a web application can use SIP as the signaling.",
                "The FreeSWITCH manual opened here says SignalWire runs that engine as a hosted platform with REST APIs. That is one bridge from open telephony to a cloud API. It is not a catalog of every CPaaS.",
            ],
            core="A browser does not register to CUCM just because both can carry voice. WebRTC media and SIP dialogs meet at a gateway, a PBX that speaks both, or a service that translates them. ICE, which the Wikipedia article names, is how the browser finds a path. It is not a CUCM partition. JSEP is how the page drives offer and answer. SIP over WebSocket is one way to keep SIP as the signaling instead of inventing a new call model. A communications API that places a call for you is a further hop. This lab opened one statement of that idea, in the FreeSWITCH manual's note on SignalWire. It did not open a vendor matrix, so the matrix stays on a confirm row with no link.",
            example="A web page establishes a PeerConnection to a gateway. The gateway sends a SIP INVITE to CUCM. CUCM rings a desk phone. If you capture only on CUCM you will see SIP and miss the browser's ICE candidates. If you capture only in the browser you will not see the CUCM route pattern. Save both sides.",
            quiz=[
                (
                    "A WebRTC page is a CUCM SIP phone.",
                    "False. Something has to translate, unless the far end also speaks WebRTC.",
                    ["True", "False"],
                    "False",
                ),
                (
                    "RFC 8829 replaces SIP.",
                    "False. It describes JavaScript control of the signaling plane and how that relates to existing signaling.",
                    ["True", "False"],
                    "False",
                ),
            ],
            sources=[WIKI_WEBRTC, W3C, RFC8825, RFC8829, RFC7118, FS_MANUAL],
            glossary=[
                ("WebRTC", "Browser real-time communication. The W3C recommendation is the API. RFC 8825 points at the protocol suite."),
                ("JSEP", "JavaScript Session Establishment Protocol, RFC 8829."),
            ],
            config="Name the gateway that translates, and which side speaks SIP.",
            trouble="One-way audio here is still SDP and ICE. A 200 on the SIP leg does not prove the browser received RTP.",
            bridge="Expressway is a Cisco edge. A WebRTC gateway is a different edge. Do not mix the port lists.",
            confirm="A full CPaaS product matrix was not opened. Confirm any vendor claim on that vendor's own page.",
        ),
    ]
