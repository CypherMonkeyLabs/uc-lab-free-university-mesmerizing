# LLQ and the delay budget

- Priority queue bandwidth is a limiter for the EF class.
- Serialization, queuing, propagation, packetization, and jitter buffer all add delay.
- ITU-T G.114 is the usual citation for a 150 ms one-way planning target.
- A queue cannot create bandwidth the circuit does not have.
- Confirm the current ITU text before you treat 150 ms as a contract.

G.711 at 20 ms is about 80 kbit/s at layer 3 and about 87.2 kbit/s with an 18-byte Ethernet header. The formula is (payload + 40 + layer-2) times 8 times packets per second, then divide by 1000 for kbit/s. Size the priority class from calls you allow, not from a feeling.

Twenty G.711 calls want about 1.6 Mbit/s at layer 3 before overhead. A priority statement of 512 kbit/s will drop or delay the rest. Users hear it as clipping, not as a SIP error.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 3246, Expedited Forwarding](https://www.rfc-editor.org/rfc/rfc3246). last checked 2026-10
- RFC. [RFC 4594, DiffServ service classes](https://www.rfc-editor.org/rfc/rfc4594). last checked 2026-10
- ITU. [ITU-T G.114, one-way transmission time](https://www.itu.int/rec/T-REC-G.114). last checked 2026-10
- ITU. [ITU-T G.711, pulse code modulation of voice](https://www.itu.int/rec/T-REC-G.711). last checked 2026-10
- Cisco. [Cisco Collaboration Preferred Architectures](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/uc_system/design/guides/PAdocs.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Differentiated services (Wikipedia)](https://en.wikipedia.org/wiki/Differentiated_services). last checked 2026-10
- Wikipedia. [Quality of service (Wikipedia)](https://en.wikipedia.org/wiki/Quality_of_service). last checked 2026-10
- Cisco. Enterprise QoS SRND book. confirm. The Enterprise QoS SRND path returned HTTP 404. last checked 2026-10

Room or sheet file: ../../rooms/sources/llq-delay/sources.json
