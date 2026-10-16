# Phone fork and network fork

- The CUCM 15 feature guide says phone-based recording takes media from the phone. The phone forks two streams to the recording server.
- The same guide says network-based recording can take media from the phone or the gateway, and the gateway connects to Unified CM over a SIP trunk.
- Using the phone as the source requires the built-in bridge. The phone's setting overrides the cluster-wide default when it is not left at default.
- The guide says recording can fail if the built-in bridge is on and Media Termination Point Required is checked.
- Cisco's basic recording note says a phone outside the managed network cannot use this fork unless it can send RTP to the recorder.

A recording is a copy of the media, sent somewhere on purpose. It is not a second conversation and it is not proof the agent heard the caller. CUCM decides the source. The feature guide tells you to prefer the phone or the gateway on the line, then shows a table for when that preference is not what CUCM selects. Multi-fork, in that guide, sends the stream to a CUBE media proxy that can relay it to up to five recording servers. Automatic and selective recording are both named. Read the call flow for the release you run before you change a line.

An agent phone has the built-in bridge off. The line is set to record from the phone. The call completes and the recorder is empty. The signaling ladder can still show a normal 200. The missing object is the fork, not the dial plan.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Cisco. [Feature Configuration Guide for CUCM, Release 15, Recording](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/cucm_b_feature-configuration-guide-for-15/cucm_mp_r53f7ff4_00_recording-12-0.html). last checked 2026-10
- Cisco. [Configure and troubleshoot basic call recording](https://www.cisco.com/c/en/us/support/docs/unified-communications/unified-communications-manager-callmanager/200788-Call-Recording-Basic-Configuration-and-T.html). last checked 2026-10
- RFC. [RFC 3550, RTP](https://www.rfc-editor.org/rfc/rfc3550). last checked 2026-10
- Cisco. [System Configuration Guide for CUCM, Release 15](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html). last checked 2026-10

Room or sheet file: ../../rooms/sources/recording-phone/sources.json
