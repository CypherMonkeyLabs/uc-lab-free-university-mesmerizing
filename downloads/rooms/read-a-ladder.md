# Reading a ladder

- One leg at a time.
- Method, status, CSeq, Call-ID, tags.
- SDP addresses are where media was supposed to go.
- A cause code is a clue, not a root cause by itself.
- Compare a good call of the same type.

Start at the first request that belongs to the failure. Note who sent it and who answered. If there are two Call-IDs, you have a B2BUA. Follow the leg that actually failed, then step back one box.

CUCM sends INVITE to CUBE. CUBE answers 503. The carrier leg has no INVITE. The failure is on CUBE before the carrier, often dial-peer or a down interface. Do not open a carrier ticket yet.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- RFC. [RFC 3515, SIP REFER](https://www.rfc-editor.org/rfc/rfc3515). last checked 2026-10
- RFC. [RFC 3264, offer/answer](https://www.rfc-editor.org/rfc/rfc3264). last checked 2026-10
- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- Cisco. [Cisco Unified Border Element product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html). last checked 2026-10
- Cisco. [Understand IOS and IOS XE call routing](https://www.cisco.com/c/en/us/support/docs/voice/ip-telephony-voice-over-ip-voip/211306-In-Depth-Explanation-of-Cisco-IOS-and-IO.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10

Room or sheet file: ../../assets/data/sources/read-a-ladder.json
