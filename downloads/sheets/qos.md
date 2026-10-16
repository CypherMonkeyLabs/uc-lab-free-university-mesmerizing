# Voice QoS

- EF is DSCP 46.
- Cisco signaling designs often use CS3. RFC 4594 points signaling at CS5.
- G.711 at 20 ms is about 80 kbit/s at layer 3.
- LLQ schedules bandwidth. It does not create it.
- CUCM locations do not mark packets.
- G.114 is the usual 150 ms planning citation. Confirm the current text.

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
- Cisco. [Preferred Architecture for Cisco Collaboration 15, design overview (PDF)](https://www.cisco.com/c/dam/en/us/td/docs/solutions/PA/overview/15x/clbpa15x.pdf). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10

Room or sheet file: sources/qos/sources.json
