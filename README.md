# Polygonal Zones

This homeassistant integration provides tha ability to create polygonal zones and use them in automations.
It gives you the ability to provide a location for a GeoJSON file that contains the zones you want to monitor.
The integration will create a sensor for each device you want to track and provide you the zone it is currently in.


## Installation
Installing the integration can be done using hacs but also manually. Installation using hacs is recommended.


### Install using hacs
To install the integration using hacs you can either add the url to your custom repositories or use the button below

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=MichelGerding&repository=Homeassistant-polygonal-zones&category=integration)


### Manual installation
Installing the integration manually can be done by copying the `custom_components/polygonal_zones` folder to your
`custom_components`
folder in your homeassistant configuration folder.

## Configuration
The configuration is done in the homeassistant UI.

1. Go to Configuration -> Integrations
2. Click on the `+` button to add a new integration.
3. Search for `Polygonal Zones` and click on it.
4. Fill in the required fields:
    - GeoJSON URIs: The URLs to the GeoJSON files that contains the zones you want to track.
    - Devices: The devices you want to track.

If you want to create an empty GeoJSON file you can omit the GeoJSON URIs field but the download option is required. in
the section below the options are further explained


### Configuration options
The configuration exposes you to a couple of different options.
These options are as follows:

- GeoJSON uris: This is a list of the GeoJSON files that contain the zones you want to track. This can either be a local
  file or a URL to a website.
- Prioritize zone files: If you want to prioritize the order of the zone files, enable this option. this means that if a
  tracker is in multiple zones it will only consider those with the lowest priority.
- Download zones: Use a local GeoJSON file to store the zones in. This will load the above defined files into a single
  file. The provided urls will be replaced with the location of this file. If you want to edit the zone files using
  actions, you will need to enable this option.
- Registered entities: Select the entities that you want to track in the zones.


## Usage
The integration will create an entity for each entity you want to track. The state of this entity will be the zone the
device is currently in. You can use this entity in automations to trigger actions based on the zone the device is in.

The entities name will be generated based on the tracked entity. For example, if you are tracking a device called
`device_tracker.my_phone`, the entity will be called `device_tracker.polygonal_zones_device_tracker_my_phone`. If that
entity is already defined, the integration will append `_n` to the name where `n` is the number of the entity.


## GeoJSON file
The zones are stored in geojson files. GeoJSON is a well-defined standard for storing geospatial data. It is a
JSON-based format that is easy for humans to read and write and easy for machines to parse and generate.
Currently only polygons are supported. an example of this file is shown below

for the ease of creating and managing this file in the ui an optional add-on is available that will generate and host
the file. This addon can be found in the [polygonal zones editor repo](https://github.com/MichelGerding/Homeassistant-polygonal-zones-addon/). This addon can be added by using the button 
below

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FMichelGerding%2FHomeassistant-polygonal-zones-addon.git)


### Example file
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Home",
        "priority": 0  // optional. lower number means higher priority
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          ...
        ]
      }
    },
    ...
  ]
}
```


## Actions
The integration provides a couple of different actions that can be used to modify the zones. It also provides an action
to reload the zones cache.

these integrations are as follows:
- `polygonal_zones.add_new_zone`: This action will add a new zone to the GeoJSON file. This expects a GeoJSON feature as input.
- `polygonal_zones.delete_zone`: This action will delete a zone from the GeoJSON file. This expects the name of the zone to delete as input.
- `polygonal_zones.edit_zone`: This action will edit a zone in the GeoJSON file. This expects a GeoJSON feature as input and the name of the zone to edit as input.
- `polygonal_zones.replace_all_zones`: This action will replace all zones in the GeoJSON file with the provided zones. This expects a GeoJSON feature collection as input.
- `polygonal_zones.reload_zones`: This action will reload the zones from the GeoJSON files.

all but the reload_zones action expect the device to be used as target. This is because the zone files are for the entire 
device and not a single entity.  You will also still need to call the reload zones integration action to update the entities.
The reload_zones action expects the entities to be reloaded as target and returns the newly loaded zones to the user.


## TODO
- [ ] **Testing**: The current version of the code has no tests. It however has been extensively tested manually. 
                   unit/integration tests might be added at a later date.
- [ ] **Improve documentation**: The documentation is not yet complete. This might be added at a later date.



## Contributing
This project is just a simple hobby project so not much additional functionality will be added. If you want to contribute
to this project please feel free to open an issue or a pull request. I will try to get back to you as soon as possible.


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
