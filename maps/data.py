import json
import logging, time

logger = logging.getLogger(__name__)

def observations_to_json(observations, filepath):

    logger.info('BEGIN')
    start = time.time()

    data = {'observations': []}
    for observation in observations:
        data['observations'].append({
            'title': observation.species.name_nl + ' (' + str(observation.number) + ')',
            'number': observation.number,
            'lon': observation.coordinates.lon,
            'lat': observation.coordinates.lat,
        })

    mid = time.time()
    logger.info('MID - time: ' + str(mid - start))

    json_data = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)
    with open(filepath, 'w') as fileout:
        fileout.write(json_data)

    end = time.time()
    logger.info('END - time: ' + str(end - start))
