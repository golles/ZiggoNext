# Ziggo Mediabox Next

## Description
A media_player component for Home Assistant that creates media_players for each Ziggo Media Box in your account.

## Installation

[^1]: Using the tool of choice open the directory (folder) for your HA configuration (where you find configuration.yaml).
[^2]:If you do not have a custom_components directory (folder) there, you need to create it.
[^3]:In the custom_components directory (folder) create a new folder called ziggo_mediabox_next.
[^4]:Download all the files from the custom_components/ziggo_mediabox_next/ directory (folder) in this repository.
[^5]:Place the files you downloaded in the new directory (folder) you created.
[^6]: Home Assistant

## Configuration
```yaml
media_player:
  - platform: ziggo_mediabox_next
    username: your@email.adr
    password: YourP@ssword
  
```
### Parameters
| Parameter | Type | Required | Description
| --- | ----------- | --- | --- |
| username | string | yes | Your Ziggo username |
| password | string | yes | Your Ziggo password |

## Credits
- The excellent start from [IIStevowII](https://github.com/IIStevowII/ziggo-mediabox-next) for a single settopbox inspired me!
- The nodejs script [NextRemoteJs from basst85](https://github.com/basst85/NextRemoteJs/) used as reference to compare results.



