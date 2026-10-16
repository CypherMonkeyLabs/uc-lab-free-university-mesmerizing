# Early media and PRACK

- 183 Session Progress can carry SDP before answer.
- A reliable provisional response wants PRACK.
- PRACK is its own transaction.
- Early media is not the same as answer.
- RFC 3262 is the specification.

Carriers often send ringback or an announcement as early media. If the caller hears silence until the 200, the 183 may have been unreliable and ignored, or the early RTP never arrived. Do not mark the call answered because you heard a tone.

INVITE, 183 with Require 100rel and SDP, PRACK, 200 OK of the PRACK, later 200 OK of the INVITE, ACK. The tone is the 183. The answer is the later 200.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3262, reliable provisional responses (PRACK)](https://www.rfc-editor.org/rfc/rfc3262). last checked 2026-10
- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- RFC. [RFC 4566, SDP](https://www.rfc-editor.org/rfc/rfc4566). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Wikipedia. [Session Description Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Description_Protocol). last checked 2026-10

Room or sheet file: ../../rooms/sources/prack-early-media/sources.json
