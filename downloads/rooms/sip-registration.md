# Registration

- REGISTER publishes a Contact. It does not place a call.
- The Request-URI is the registrar domain, not the user's address-of-record.
- 401 challenges the user. A second REGISTER must use a new CSeq.
- The binding expires.
- A registered phone can still be unreachable for media.

RFC 3261 section 10 is the whole idea. CUCM is the registrar for the phones that point at it. A successful 200 means CUCM stored a binding until it expires or the phone removes it. It does not mean the WAN will carry RTP.

First REGISTER, 401, second REGISTER with Authorization and CSeq plus one, then 200. If the second CSeq matches the first, the registrar treats it as a replay.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Wikipedia. [Skinny Client Control Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Skinny_Call_Control_Protocol). last checked 2026-10
- Wikipedia. [CUCM (Wikipedia disambiguation)](https://en.wikipedia.org/wiki/CUCM). last checked 2026-10
- Wikipedia. English Wikipedia article for Cisco Unified Communications Manager. confirm. That title returned HTTP 404. The CUCM disambiguation page is the Wikipedia page that opened. last checked 2026-10

Room or sheet file: ../../assets/data/sources/sip-registration.json
