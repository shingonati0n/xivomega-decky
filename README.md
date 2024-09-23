![XIVOmegaHeader](https://github.com/user-attachments/assets/eea8545d-8ca2-4ad1-a552-d2e2c5db4d6d)

# XIVOmega - Decky Version

A Steam Deck Plugin (for Decky Loader) to mitigate latency on the Critically Acclaimed MMORPG Final Fantasy XIV. This plugin is the evolution of [xivomega](https://github.com/shingonati0n/xivomega) which in turn is based on XivMitmLatencyMitigator, XivMitmDocker and XivAlexander. 

![20240923184221_1](https://github.com/user-attachments/assets/4eeb8fee-b518-48a2-8181-a1d8a7a01645)

### Installation

**(The following steps are to install the prerelease version of this plugin. The end state will be to install via Decky Loader Store).** 

- Download the zip file in the releases page. Note this is a prerelease version. 
- In Decky Loader, enable Developer mode by going into Settings -> General -> Developer Mode
- In Developer select install from Zip. Navigate to the location of the zip file and install

### Notes - How it Works 

- This plugin makes use of Podman, which is included by default with SteamOS since 3.5 as part of Distrobox. It creates a rootful container which executes the mitigation script as in XivMitmLatencyMitigator, without the need of another computer to run. 
- **The plugin applies a fix in order to use Podman:** By default, any image downloaded with podman gets save to /var/lib/containers/storage. When trying to run a container using the default location, it will error out indicating there is not sufficient space. The plugin fixes this by setting the storage location to the runtime folder of itself (homebrew/data/XIVOmega) via a storage.conf file which gets created into /etc/containers.

- The podman image used is pulled from here: https://quay.io/repository/shingonati0n/xivomega. This container runs Debian with the following contents:
   - a script to set up iptables POSTFORWARDING rule (iptset.sh)
   - a script which calls the mitigator as in XivMitmLatencyMitigator. 

- The game traffic is routed thru this container, which effectively mitigates latency. This translates into less GCD clipping - **the same effect as using XivAlexander**. 
- The container and the networking set up are ephemeral - when the mitigator is toggled off, everything is removed seamlessly and can be activated again smoothly. 
- The opcodes file which gets changed each time a new game patch releases gets updated along with XivAlexander and XivMitmLatencyMitigator. 
- Container activity gets saved to the plugin log - this can be checked on homebrew/logs/XIVOmega. 
- When uninstalling, the image and the container along with all other elements gets effectively removed. The storage.conf file from /etc/containers gets restored to default values. 

### Special Thanks

- To soreepeong and bankjaaneo, for creating XivAlexander, XivMitmLatencyMitigator and XivMitmDocker
- To bnnuy for testing 
- To jurassicplayer and the folks at the Steam Deck Homebrew Discord for all their help whenever I got stuck. 

### Was this plugin useful?? 

- **Consider donating at [ko-fi](https://ko-fi.com/ugo_shingonati0n).** Any support is greatly appreciated.

### License 

This project is licensed under the terms of the BSD 3-Clause License. You can read the full license text in LICENSE.
