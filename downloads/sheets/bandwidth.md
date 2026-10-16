# Bandwidth sketch

- G.711 20 ms payload is 160 bytes.
- IP, UDP, and RTP add 40 bytes.
- Layer 3 is about 80 kbit/s.
- An 18-byte Ethernet header makes about 87.2 kbit/s.
- Size the priority queue from admitted calls.
- Formula: (payload + 40 + L2) x 8 x (1000 / ptime) / 1000.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- ITU. [ITU-T G.711, pulse code modulation of voice](https://www.itu.int/rec/T-REC-G.711). last checked 2026-10
- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- RFC. [RFC 4594, DiffServ service classes](https://www.rfc-editor.org/rfc/rfc4594). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Quality of service (Wikipedia)](https://en.wikipedia.org/wiki/Quality_of_service). last checked 2026-10
- Cisco. Enterprise QoS SRND book. confirm. The Enterprise QoS SRND path returned HTTP 404. last checked 2026-10

Room or sheet file: sources/bandwidth/sources.json
