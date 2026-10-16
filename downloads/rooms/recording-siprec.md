# SIPREC and CUBE as the recording client

- RFC 7245 describes architectures for recording in a SIP environment by sending a copy of a media stream to a recording device.
- RFC 7865 describes the metadata the session recording server sees. RFC 7866 is the session recording protocol.
- RFC 7866 introduces the siprec option tag. An SRC puts it in Require so a peer that does not support the extension can reject the INVITE.
- The CUBE IOS XE 17.6 guide says CUBE acts as the session recording client and any third-party recorder acts as the recording server.
- That guide cites RFC 7245 section 3.1.1, and it cites the SIPREC metadata and protocol drafts. Confirm the guide for the release you run.

Keep the call and the recording session apart. The human call is one dialog. The recording session is another SIP relationship whose job is to carry a copy and the metadata. RFC 7866 says a recording-aware participant can use the record-aware option and the SDP a=record attribute, and that a participant who is not recording-aware still needs an indication by some other means, such as a tone. The CUBE guide says that if SIPREC is not configured, CUBE falls back to its network-based recording implementation. It also says CUBE supports the siprec option tag and the src feature tag, and does not support the SDP extensions in the protocol draft it cites. Do not tell an operator the draft and the RFC are the same text.

A recorder answers the recording INVITE and the agent hears the caller. The file has audio and no party names. Metadata is the missing piece RFC 7865 is about. A tone, or the absence of one, is a different requirement from RFC 7866, not a codec problem.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- RFC. [RFC 7245, architecture for media recording using SIP](https://www.rfc-editor.org/rfc/rfc7245). last checked 2026-10
- RFC. [RFC 7865, SIP recording metadata](https://www.rfc-editor.org/rfc/rfc7865). last checked 2026-10
- RFC. [RFC 7866, session recording protocol](https://www.rfc-editor.org/rfc/rfc7866). last checked 2026-10
- Cisco. [CUBE configuration guide, SIP forking (IOS XE 17.6 onwards)](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/voice/cube/ios-xe/config/ios-xe-book/m_voi-cube-sip-rec-recorder.html). last checked 2026-10
- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10
- Cisco. [Cisco Unified Border Element product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-border-element/series.html). last checked 2026-10

Room or sheet file: ../../rooms/sources/recording-siprec/sources.json
