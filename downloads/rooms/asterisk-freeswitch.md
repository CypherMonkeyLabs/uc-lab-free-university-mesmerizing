# Asterisk and FreeSWITCH as the other PBX

- Wikipedia describes Asterisk as a software PBX that connects phones, the PSTN, and VoIP endpoints.
- The Asterisk documentation opened here separates module types. Channel drivers are one type. res_pjsip is the SIP channel configuration the same docs link as Configuring res_pjsip.
- Wikipedia describes FreeSWITCH as telephony software for real-time audio, video, and text, including SIP and WebRTC.
- The FreeSWITCH users manual that opened is the operator book. A Sofia SIP chapter URL redirected to that manual, so this lab links the manual.
- Neither product copies a CUCM calling search space. You translate the idea, then you test one call.

Asterisk matches calls in a dialplan. FreeSWITCH matches calls in its own dialplan. CUCM matches a partition and a route pattern. The interop skill is to name the digit string on each side of the trunk and the codec each side offered. The Asterisk module page shows channel-driver modules as a category. It does not list your peer's host. The FreeSWITCH manual says its parameters are checked against the project source and the shipped defaults. When a guide and a blog disagree, the guide for the version you installed is the one to follow.

Asterisk answers a lab INVITE with 488 Not Acceptable Here. CUCM offered a codec the peer's endpoint did not allow. Add a codec both sides list, or remove the one they cannot use. Do not restart CUCM to test a codec the offer already showed.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Wikipedia. [Asterisk (Wikipedia)](https://en.wikipedia.org/wiki/Asterisk_(PBX)). last checked 2026-10
- Asterisk. [Types of Asterisk modules](https://docs.asterisk.org/Fundamentals/Asterisk-Architecture/Types-of-Asterisk-Modules/). last checked 2026-10
- Asterisk. [Configuring res_pjsip](https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/). last checked 2026-10
- Wikipedia. [FreeSWITCH (Wikipedia)](https://en.wikipedia.org/wiki/FreeSWITCH). last checked 2026-10
- FreeSWITCH. [FreeSWITCH users manual](https://developer.signalwire.com/freeswitch/). last checked 2026-10
- RFC. [RFC 3261, SIP](https://www.rfc-editor.org/rfc/rfc3261). last checked 2026-10

Room or sheet file: ../../rooms/sources/asterisk-freeswitch/sources.json
