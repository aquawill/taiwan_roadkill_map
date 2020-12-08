import csv
import json

import requests

app_id = 'JDuZcEECeUBXGkFT6zp9'  # HERE APP ID
app_code = 'pTa6-IjR6ElKf0kjAolO2A'  # HERE APP CODE
mode = 'fastest;car;traffic:disabled'  # Routing Mode of HERE Routing API.


# Read starting and end points of roadkill hotspots, pass to HERE Routing API to get the shape of road segments
# Output the list of geo-coordinates of road segments for mapping.
def get_route(ori_lat, ori_lon, dest_lat, dest_lon, route_mode):
    route_url = 'https://route.api.here.com/routing/7.2/calculateroute.json?'
    wp0 = '{},{}'.format(ori_lat, ori_lon).replace(' ', '')  # Starting Point of road segment
    wp1 = '{},{}'.format(dest_lat, dest_lon).replace(' ', '')  # End point of road segment
    route_options = '&mode={}&legAttributes=shape'.format(route_mode)
    url = route_url + 'app_id=' + app_id + '&app_code=' + app_code + '&waypoint0=geo!' + wp0 + '&waypoint1=geo!' + wp1 + route_options
    print(url)
    json_result = json.loads(requests.get(url).text)
    print(json_result)
    routes = json_result['response']['route']
    route_shape = []
    for route in routes:
        legs = route['leg']
        for leg in legs:
            shape = leg['shape']
            point_index = 0
            while point_index < len(shape):
                point = shape[point_index]
                lat = float(point.split(',')[0])
                lon = float(point.split(',')[1])
                route_shape.append([lat, lon])
                point_index += 1
    print(route_shape)
    return route_shape


full_list = []

# Open input csv file, column names of raw input are:
# id,species,type,recommended_type,season,day_night,lat_1,lng_1,lat_2,lng_2,route_type,route_number,route_desc,recommended_voice
# Add one more column "wkt" to store the geometries of roadkill road segments in WKT format.
with open('roadkill_locations.csv', encoding='utf-8') as csv_file:
    dict_reader = csv.DictReader(csv_file, delimiter='\t')
    fieldnames = dict_reader.fieldnames
    fieldnames.append('wkt')

    for row in dict_reader:
        print(row)
        lat_1 = row.get('lat_1')
        lng_1 = row.get('lng_1')
        lat_2 = row.get('lat_2')
        lng_2 = row.get('lng_2')
        shape_point_list = []
        route_shape_point_list = get_route(lat_1, lng_1, lat_2, lng_2, mode)
        shape_point_index = 0
        while shape_point_index < len(route_shape_point_list):
            shape_point = route_shape_point_list[shape_point_index]
            shape_point_list.append(shape_point)
            shape_point_index += 1
        wkt_start = "LINESTRING ("
        wkt_shape_point_list = []
        wkt_end = ")"
        for shape_point in shape_point_list:
            shape_point_lat = shape_point[0]
            shape_point_lng = shape_point[1]
            wkt_shape_point_list.append('{} {}'.format(shape_point_lng, shape_point_lat))
        wkt_body = '{}{}{}'.format(wkt_start, ', '.join(wkt_shape_point_list), wkt_end)
        print(wkt_body)
        row['wkt'] = wkt_body
        full_list.append(row)

# Write the result to new csv file.
with open('roadkill_locations_output.csv', mode='w', newline='', encoding='utf-8') as csv_output_file:
    writer = csv.DictWriter(csv_output_file, delimiter='\t', fieldnames=dict_reader.fieldnames)
    writer.writeheader()
    writer.writerows(full_list)
