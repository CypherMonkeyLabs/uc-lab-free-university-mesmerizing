# CUBE as a B2BUA

- CUBE terminates one dialog and starts another.
- Codec, DTMF, and header policies are per leg unless you bind them.
- Media can anchor on CUBE or flow around it, depending on the design.
- A 200 on the CUCM leg does not prove the carrier leg is up.
- Read IP addresses on each SDP.

Unified Border Element is Cisco's SBC on IOS. Treat it as two calls. Mid-call services such as transfer and hold are re-INVITEs CUBE must map. If you only capture the CUCM side, you will miss a carrier rejection.

CUCM sends G.711. The carrier peer allows G.729 only. CUBE can transcode if a DSP is configured and licensed for that feature. If not, the carrier leg fails and CUCM may see a different cause than 'no DSP'.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- RFC. [RFC 3711, SRTP](https://www.rfc-editor.org/rfc/rfc3711). last checked 2026-10
- Cisco. [Cisco Unified Border Element product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html). last checked 2026-10
- Cisco. [CUBE configuration guide, dial peers (IOS XE 17.6 onwards)](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/voice/cube/ios-xe/config/ios-xe-book/m_cube-dp.html). last checked 2026-10
- Cisco. [Understand IOS and IOS XE call routing](https://www.cisco.com/c/en/us/support/docs/voice/ip-telephony-voice-over-ip-voip/211306-In-Depth-Explanation-of-Cisco-IOS-and-IO.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Protocol and ports. [IANA SIP parameters](https://www.iana.org/assignments/sip-parameters/sip-parameters.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Session Initiation Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Session_Initiation_Protocol). last checked 2026-10
- Wikipedia. English Wikipedia article for Cisco Unified Border Element. confirm. That title returned HTTP 404. last checked 2026-10
- RFC. [RFC 4733, RTP telephony events](https://www.rfc-editor.org/rfc/rfc4733). last checked 2026-10
- RFC. [RFC 4566, SDP](https://www.rfc-editor.org/rfc/rfc4566). last checked 2026-10

Room or sheet file: ../../assets/data/sources/cube-b2bua.json
