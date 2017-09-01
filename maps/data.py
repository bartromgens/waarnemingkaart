import json


def observations_to_json(observations, filepath):
    data = {'observations': []}
    for observation in observations:
        data['observations'].append({
            'title': observation.species.name_nl,
            'number': observation.number,
            'lon': observation.coordinates.lon,
            'lat': observation.coordinates.lat,
        })
    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    with open(filepath, 'w') as fileout:
        fileout.write(json_data)
