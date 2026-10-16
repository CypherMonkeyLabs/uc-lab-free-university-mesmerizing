# Expressway-C and Expressway-E

- Expressway-C lives on the inside, next to CUCM.
- Expressway-E lives at the edge.
- A traversal zone connects them.
- They are not a SIP proxy you insert in every PSTN call.
- Clustering and certificates are part of the design, not an afterthought.

The pair exists so devices on the internet can reach CUCM services without exposing CUCM. Traversal keeps the connection initiated from the inside. If you treat C and E as two unrelated servers, MRA will not come up.

Phones on the LAN register straight to CUCM. Phones off the LAN use the Expressway pair. A PSTN call from a LAN phone does not need to hairpin through Expressway unless you designed it that way.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Cisco Expressway Series product support](https://www.cisco.com/c/en/us/support/unified-communications/expressway-series/series.html). last checked 2026-10
- Cisco. [Mobile and Remote Access through Cisco Expressway, X15.2](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/expressway/config_guide/X15-2/mra/exwy_b_mra-deployment-guide-x152.html). last checked 2026-10
- Protocol and ports. [Cisco Expressway IP port usage (X14.3 and X15.0)](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/expressway/config_guide/X15-0/ip-port/exwy_b_cisco-expressway-ip-port-usage-configuration-guide-x15.html). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Cisco. [Cisco Collaboration Preferred Architectures](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/uc_system/design/guides/PAdocs.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10
- Cisco. Collaboration 12 SRND book. confirm. The historical Collaboration 12 SRND path opened as a product listing, not the design book. Use the Preferred Architecture index, which was opened. last checked 2026-10

Room or sheet file: ../../rooms/sources/expressway-pair/sources.json
