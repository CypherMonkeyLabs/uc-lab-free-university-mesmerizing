# A SIP trunk is a peer, not a brand

- Wikipedia's SIP trunking article describes a SIP service between a provider and a customer's SIP PBX.
- The same article says the provider side and the enterprise side are different domains, joined by a SIP trunk.
- SIPconnect, on the SIP Forum page opened here, is a technical recommendation for direct IP peering between a SIP PBX and a VoIP provider.
- CUCM's trunk, CUBE's dial peers, and the far PBX's own routes are three plans.
- RFC 3261 is still the request and the response. A trunk does not replace it.

When CUCM sends a call to Asterisk or FreeSWITCH, count dialogs the same way you count them toward a carrier. CUBE in the middle is a B2BUA, so the Call-ID usually changes. Early offer, PRACK, and session timers are negotiation, not a feature of the logo on the box. SIPconnect is a profile the SIP Forum publishes for provider peering. It is not a promise that every open-source PBX implements it. Read the recommendation if you are matching a provider. Read the far PBX's own dial plan if you are matching a lab peer.

CUCM matches a route pattern and sends INVITE to CUBE. CUBE matches an outbound dial peer and sends a new INVITE to Asterisk. Asterisk's dialplan does not match the digits. The failure is on the third plan. A CUCM DNA trace that stops at the trunk has not seen it.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Wikipedia. [SIP trunking (Wikipedia)](https://en.wikipedia.org/wiki/SIP_trunking). last checked 2026-10
- SIP Forum. [SIPconnect technical recommendation](https://www.sipforum.org/technology/sipconnect/). last checked 2026-10
- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10

Room or sheet file: ../../rooms/sources/open-sip-trunk/sources.json
