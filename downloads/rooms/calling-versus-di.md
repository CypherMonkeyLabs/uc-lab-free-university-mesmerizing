# Webex Calling and Dedicated Instance

- Multi-tenant Webex Calling and Dedicated Instance are different offers.
- Calling locations, numbers, and features are managed in Control Hub.
- Dedicated Instance is CUCM hosted for you, with its own dial plan.
- A local gateway is a PSTN choice for Calling, not the definition of Calling.
- Confirm the offer on the subscription before you design.

People say 'we moved to Webex' and mean four different architectures. Ask whether the phone registers to Calling, to a Dedicated Instance CUCM, or still to the old CUCM through a trunk. The ladder answers it.

A site keeps CUCM and sends only a pilot range to Webex Calling through a local gateway. That is coexistence, not a finished migration. Draw the numbers that still live on CUCM.

## Sources and go deeper

Independent, free, learning-only student project.

Opened 2026-10. A row marked confirm has no link, because that page was not verified.

- Webex. [Get started with Webex Calling](https://help.webex.com/en-us/article/8jda92/Webex-Calling). last checked 2026-10
- Webex. [Webex Help Center](https://help.webex.com/). last checked 2026-10
- Cisco. [Cisco Unified Communications Manager product support](https://www.cisco.com/c/en/us/support/unified-communications/unified-communications-manager-callmanager/series.html). last checked 2026-10
- Cisco. [Cisco Collaboration Preferred Architectures](https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/uc_system/design/guides/PAdocs.html). last checked 2026-10
- Community. [Cisco Community, Collaboration knowledge base](https://community.cisco.com/t5/collaboration-knowledge-base/tkb-p/4691-docs-collaboration-voice-video). last checked 2026-10
- Wikipedia. [Voice over IP (Wikipedia)](https://en.wikipedia.org/wiki/Voice_over_IP). last checked 2026-10

Room or sheet file: ../../rooms/sources/calling-versus-di/sources.json
