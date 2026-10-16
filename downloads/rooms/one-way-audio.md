# One-way audio

- Signaling can be perfect while RTP fails in one direction.
- Compare SDP connection addresses with the addresses that really send packets.
- NAT and a firewall are the common reasons.
- Codec mismatch usually fails the call, it does not half-succeed.
- Hold and resume is a second offer. Check it too.

One-way audio means one side's packets arrive and the other's do not, or one side is playing silence because the direction attribute is inactive or sendonly. Look at RTP counters and the SDP, then the firewall, then QoS. QoS rarely drops only one direction unless the return path is a different route.

The agent hears the caller. The caller hears nothing. The caller's SDP says a private address the carrier cannot route. The fix is the media address CUBE advertises, not a new codec list.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- RFC. [RFC 3264, offer/answer](https://www.rfc-editor.org/rfc/rfc3264). last checked 2026-10
- RFC. [RFC 3711, SRTP](https://www.rfc-editor.org/rfc/rfc3711). last checked 2026-10
- RFC. [RFC 8445, ICE](https://www.rfc-editor.org/rfc/rfc8445). last checked 2026-10
- Cisco. [Cisco Unified Border Element product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Protocol and ports. [Cisco Expressway IP port usage (X14.3 and X15.0)](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/expressway/config_guide/X15-0/ip-port/exwy_b_cisco-expressway-ip-port-usage-configuration-guide-x15.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Real-time Transport Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol). last checked 2026-10

Room or sheet file: ../../assets/data/sources/one-way-audio.json
