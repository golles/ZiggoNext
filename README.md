# Ziggo Mediabox Next

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

## Breaking changes!!
Sensors are added to this component. Therefore the configuration for this component has changed. Check the configuration section below!

## Description
A media player component for Home Assistant that creates a media player and a sensor for each Ziggo Media Box Next in your account.

## Prerequisites
- You need a Ziggo account with a Ziggo Media Box Next.
- The energy mode needs to be set to high ("Hoog" in Dutch), otherwise you are not able to switch the device on in the media player.

## HACS Installation
1. Make sure you've installed [HACS](https://hacs.xyz/docs/installation/prerequisites)
2. In the integrations tab, search for ZiggoNext.
3. Install the Integration.
4. Add ziggonext entry to configuration (see below)

## Manual installation

1. Open the directory (folder) for your HA configuration (where you find configuration.yaml).
2. If you do not have a custom_components directory (folder) there, you need to create it.
3. In the custom_components directory (folder) create a new folder called ziggonext.
4. Download all the files from the custom_components/ziggonext/ directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Add ziggonext entry to configuration (see below)
7. Restart Home Assistant

## Configuration
```yaml
ziggonext:
  username: !secret ziggo_username
  password: !secret ziggo_password  
```
The id's for media_players and sensors are generated based on the name provided by Ziggo. You can adjust your box name in the settings on the ziggogo.tv website.

### Parameters
| Parameter | Type | Required | Description
| --- | ----------- | --- | --- |
| username | string | yes | Your Ziggo username |
| password | string | yes | Your Ziggo password |

## Credits
- The excellent start from [IIStevowII](https://github.com/IIStevowII/ziggo-mediabox-next) for a single settopbox inspired me!
- The nodejs script [NextRemoteJs from basst85](https://github.com/basst85/NextRemoteJs/) used as reference to compare results.
- Contributions by:
  - [shortwood](https://github.com/shortwood)

<a href="https://www.buymeacoffee.com/sholofly" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" style="height: 25px !important;width: 108px !important;" ></a>