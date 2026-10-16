# Offer and answer

- SDP is the offer or the answer, not a second signaling protocol you ignore.
- Early offer puts the offer in the INVITE.
- The answer lists what was accepted, not a new unrelated codec list.
- A re-INVITE can change hold, codec, or fax.
- RFC 3264 is the rule for which lines may be answered.

Early offer is common on CUCM SIP trunks. Delayed offer puts the offer in the 200 and the answer in the ACK. Mixing them on a CUBE without a plan produces a call that signals and then has no media, or a codec neither side wanted. Read m= lines and the direction attributes before you blame the WAN.

An INVITE carries G.711 and G.729. The 200 answers with G.711 only. The call is G.711. If the 200 has no audio m-line you accepted, you do not have a voice call yet.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3264, offer/answer](https://www.rfc-editor.org/rfc/rfc3264). last checked 2026-10
- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- RFC. [RFC 4566, SDP](https://www.rfc-editor.org/rfc/rfc4566). last checked 2026-10
- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Protocol and ports. [IANA RTP parameters](https://www.iana.org/assignments/rtp-parameters/rtp-parameters.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Wikipedia. [Real-time Transport Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol). last checked 2026-10
- Cisco. Collaboration 12 SRND book. confirm. The historical Collaboration 12 SRND path opened as a product listing, not the design book. Use the Preferred Architecture index, which was opened. last checked 2026-10
- Wikipedia. [Session Description Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Description_Protocol). last checked 2026-10

Room or sheet file: ../../assets/data/sources/offer-answer.json
