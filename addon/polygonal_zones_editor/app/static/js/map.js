const {map, editableLayers} = generate_map('./zones.json')
setup_editing(map, editableLayers);

function generate_map(zones_url) {
    const osm_url = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    const osmAttrib = '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
    const osm = L.tileLayer(osm_url, {maxZoom: 18, attribution: osmAttrib});
    const map = L.map('map', {layers: [osm], center: [52.96523540264812, 6.52002831753822], zoom: 13});

    let editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);

    fetch(zones_url)
        .then(response => {
            return response.text()
        }).then(json => {
        let data = JSON.parse(json)

        L.geoJSON(data, {
            onEachFeature: (feature, layer) => {
                layer.bindPopup(feature.properties.name);
                editableLayers.addLayer(layer);
            },
        })

        render_zone_list();
        // fit the map to the bounds of the editable layers
        // center map on the home zone
        if (editableLayers.getLayers().length > 0) {
            map.fitBounds(editableLayers.getBounds());
            map.setView(editableLayers.getBounds().getCenter(), 13);
        } else {
            create_load_btn();
        }
    });

    return {map, editableLayers};
}

function setup_editing(map, editableLayers) {
    const drawing_options = {
        position: 'topleft',
        draw: {
            polyline: false,
            polygon: {
                allowIntersection: false,
                drawError: {
                    color: '#e1e100',
                    message: '<strong>Oh snap!<strong> you can\'t draw that!'
                },
                shapeOptions: {
                    color: '#bada55'
                }
            },
            circle: false,
            rectangle: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: editableLayers,
            edit: false,
            remove: true
        }
    };

    let drawControl = new L.Control.Draw(drawing_options);
    let drawnItems = new L.FeatureGroup();

    map.addControl(drawControl);
    map.addLayer(drawnItems);

    map.on('draw:deleted', function (e) {
        let layers = e.layers;
        layers.eachLayer(layer => {
            editableLayers.removeLayer(layer);
            render_zone_list();
        });

        if (editableLayers.getLayers().length === 0) {
            create_load_btn();
        }
    });

    map.on('draw:created', function (e) {
        let type = e.layerType,
            layer = e.layer;

        if (type === 'marker') {
            layer.bindPopup('A popup!');
        }

        // generate a name according to `zone {n}`
        let name = `Zone ${editableLayers.getLayers().length + 1}`;
        layer.feature = {
            properties: {
                name: name
            }
        };

        console.log(layer)
        editableLayers.addLayer(layer);
        // log the geojson
        console.log(layer.toGeoJSON());
        render_zone_list();

        delete_load_btn();
    });
}

function edit_zone_event(e) {
    // disable editing for all zones.
    editableLayers.eachLayer(layer => layer.editing.disable());
    document.querySelectorAll('zone-entry').forEach(zone => zone.setAttribute('editing', 'false'));

    let oldName = e.detail.oldName || e.detail.name
    let layer = editableLayers.getLayers().find(layer => layer.feature.properties.name === oldName);

    // if we start editing a zone, enable editing for that zone
    if (e.detail.editing) {
        map.fitBounds(layer.getBounds());
        layer.editing.enable();
    } else {
        // once we stop we will disable editing and save the changes
        layer.feature.properties.name = e.detail.name;
        e.target.setAttribute('name', e.detail.name);
    }
}

function render_zone_list() {
    let zone_list = document.querySelector('.zone-list');
    zone_list.innerHTML = '';
    editableLayers.eachLayer(layer => {
        // render a zone-entry element and set attribute name
        let zone_entry = document.createElement('zone-entry');
        zone_entry.setAttribute('name', layer.feature.properties.name);
        zone_entry.addEventListener('edit', edit_zone_event);

        zone_list.appendChild(zone_entry);
    });
}

function save_zones() {
    let geojson = {
        type: "FeatureCollection",
        features: Object.values(editableLayers._layers).map(value => {
            points = value._latlngs[0].map(point => [point.lng, point.lat]);
            return {
                type: "Feature",
                properties: {
                    name: value.feature.properties.name
                },
                geometry: {
                    type: "Polygon",
                    coordinates: [points]
                }
            }
        })
    };

    fetch('./save_zones', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(geojson)
    }).then(response => {
        let elem = document.querySelector('.save-btn');
        if (response.ok) {
            elem.classList.remove('error')
            elem.classList.add('success')
        } else {
            elem.classList.remove('success')
            elem.classList.add('error')
        }

        setTimeout(() => {
            elem.classList.remove('error')
            elem.classList.remove('success')
        }, 2000)
    })
}


function load_bulk_json() {
    // open a file dialog
    let input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.addEventListener('change', function () {
        let file = input.files[0];
        let reader = new FileReader();
        reader.onload = function (e) {
            let data = JSON.parse(e.target.result);
            editableLayers.clearLayers();
            L.geoJSON(data, {
                onEachFeature: (feature, layer) => {
                    layer.bindPopup(feature.properties.name);
                    editableLayers.addLayer(layer);
                },
            })
            map.fitBounds(editableLayers.getBounds());
            render_zone_list();
            if (editableLayers.getLayers().length > 0) {
                map.fitBounds(editableLayers.getBounds());
                map.setView(editableLayers.getBounds().getCenter(), 13);

                delete_load_btn();
            }
        };
        reader.readAsText(file);
    });
    input.click();
}