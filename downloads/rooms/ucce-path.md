# UCCE from carrier to agent

- Ingress, routing, queue treatment, and the agent are different stages.
- CVP can front the call and ask ICM for a label.
- The routing script returns a destination. It is not the audio file.
- Finesse shows agent state.
- CUIC reports what was logged, which can lag the call.

Unified Contact Center Enterprise is a system of pieces: gateway, CVP, the ICM router and logger, peripheral gateways, and the desktop. A teaching path is PSTN to the gateway, control to CVP and ICM, then delivery to an agent on CUCM. Your deployment can be a different model. Name the model before you debug.

The caller hears queue music, so CVP treatment works. No agent is offered the call. Look at skill group staffing and the script's queue node before you restart the gateway.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Cisco Unified Contact Center Enterprise product support](https://www.cisco.com/c/en/us/support/customer-collaboration/unified-contact-center-enterprise/series.html). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10
- Cisco. [Cisco Collaboration Preferred Architectures](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/uc_system/design/guides/PAdocs.html). last checked 2026-10
- Protocol and ports. [CUCM 15 TCP and UDP port usage](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_m_tcp-and-udp-port-usage-12-0.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10
- Cisco. Collaboration 12 SRND book. confirm. The historical Collaboration 12 SRND path opened as a product listing, not the design book. Use the Preferred Architecture index, which was opened. last checked 2026-10

Room or sheet file: ../../assets/data/sources/ucce-path.json
