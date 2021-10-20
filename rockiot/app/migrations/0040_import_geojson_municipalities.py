import json
import os

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.db import migrations

from app.models import Municipality


def import_municipalities(apps, schema_editor):
    file_path = os.path.join(os.path.dirname(__file__), 'geojson/', 'serbia.json')
    with open(file_path, 'r') as fd:
        data = json.load(fd)
        print(f"Importing municipalities [size: {len(data)}]... ")
        for feature in data['features']:
            print("Loaded feature ... ")
            geom_str = json.dumps(feature['geometry'])
            geom = GEOSGeometry(geom_str)
            try:
                if isinstance(geom, Polygon):
                    geom = MultiPolygon([geom])
                if not isinstance(geom, MultiPolygon):
                    print('{} not acceptable for this model'.format(geom.geom_type))
                    continue
                name = feature['properties']['laa']
                code = feature['properties']['adm_code']
                if code is None or len(code) == 0:
                    code = feature['properties']['salb']
                municipality = Municipality(code=code, name=name, area=geom)
                municipality.save()
                print("Saved municipality  ... ")
            except TypeError as e:
                print(e)


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0039_auto_20211015_1658'),
    ]

    operations = [
        migrations.RunPython(import_municipalities, reverse_code=migrations.RunPython.noop),
    ]
