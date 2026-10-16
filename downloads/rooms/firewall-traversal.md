# Firewall and traversal

- Open the ports your version's guide lists.
- Signaling ports and media ranges are different lines.
- Traversal media is not the same range as a phone's RTP range on the LAN.
- One ACL copied from a blog is how outages start.
- Write the source, destination, and direction.

Cisco publishes a port reference with the Expressway and MRA guides. It changes. This lab does not reprint a port matrix as if it were current. The skill is to read the matrix for your version and test one flow: registration, then a call, then hold.

Registration works and the call has no audio. Signaling ports were opened. The media range for traversal was not. The ladder shows 200 OK. RTP counters on one side stay at zero.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Protocol and ports. [Cisco Expressway IP port usage (X14.3 and X15.0)](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/expressway/config_guide/X15-0/ip-port/exwy_b_cisco-expressway-ip-port-usage-configuration-guide-x15.html). last checked 2026-10
- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- RFC. [RFC 8445, ICE](https://www.rfc-editor.org/rfc/rfc8445). last checked 2026-10
- Cisco. [Cisco Expressway Series product support](https://www.cisco.com/c/en/us/support/unified-communications/expressway-series/series.html). last checked 2026-10
- Protocol and ports. [IANA service names and port numbers](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Real-time Transport Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Real-time_Transport_Protocol). last checked 2026-10

Room or sheet file: ../../rooms/sources/firewall-traversal/sources.json
