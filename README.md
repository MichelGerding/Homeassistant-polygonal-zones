# Polygonal Zones
This homeassistant integration provides tha ability to create polygonal zones and use them in automations.
It gives you the ability to provide a location for a GeoJSON file that contains the zones you want to monitor.
The integration will create a sensor for each device you want to track and provide you the zone it is currently in.


## Installation
1. Install this integration by copying the `custom_components/polygonal_zones` folder to your `custom_components`
   folder in your homeassistant configuration folder.
2. Add the GeoJSON file to your `config/www` folder. or host it elsewhere.
3. Cnofigure the integration in the homeassistant UI.

## Configuration
The configuration is done in the homeassistant UI.
1. Go to Configuration -> Integrations
2. Click on the `+` button to add a new integration.
3. Search for `Polygonal Zones` and click on it.
4. Fill in the required fields:
    - GeoJSON URL: The URL to the GeoJSON file that contains the zones.
    - Devices: The devices you want to track. This will create a sensor for each device.
    - Click on `Submit` to save the configuration.

## Usage
The integration will create an entity for each entity you want to track. The state of this entity will be the zone the 
device is currently in. You can use this entity in automations to trigger actions based on the zone the device is in.

The entities name will be generated based on the tracked entity. For example, if you are tracking a device called 
`device_tracker.my_phone`, the entity will be called `sensor.polygonal_zones_device_tracker_my_phone`. So make sure you 
don't include entities that have the same name and domain.

## GeoJSON file
The GeoJSON file should contain a `FeatureCollection` with `Polygon` features. Each feature should have a `name` property that will be used as the zone name.
This file can be generated and hosted using the [polygonal_zones_editor](https://github.com/MichelGerding/Homeassistant-polygonal-zones-addon/) addon.
this addon will generate and host the file.

### Example file
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "name": "Home"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [ ... ]
      }
    }, ...
  ]
}
```

## Testing
The current version of the code has no tests. It however has been extensively tested manually. unit/integration tests 
might be added in the future.


## TODO
- [ ] Add tests
- [ ] Add ability to have entities with the same name
- [ ] Add addon to create GeoJSON file/ create zones in the UI

