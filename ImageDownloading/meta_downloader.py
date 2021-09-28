import csv
import requests
try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode
import shutil
from os import path, makedirs
import random

raise Exception("are you sure!!")

# dev key keep secret!! 
dev_key = 'AIzaSyBIvaJZHj8QxpYQ7YxWn-Uj44anXgfTfQU'

base_url = "https://maps.googleapis.com/maps/api/streetview"
meta_url = "https://maps.googleapis.com/maps/api/streetview/metadata"

#number of images for each city
downloads_per_city = 400

# stores all the info for each city
# all lower case with underscores between words
city_info = {
	'tokyo': {'id': 0, 'country': 'japan', 'lng': 139.6922, 'lat': 35.6897, 'radius': 0.1, 'continent': 'asia'}, 
	'delhi': {'id': 1, 'country': 'india', 'lng': 77.2300, 'lat': 28.6600, 'radius': 0.1, 'continent': 'asia'}, 
	'shanghai': {'id': 2, 'country': 'china', 'lng': 121.4667, 'lat': 31.1667, 'radius': 0.1, 'continent': 'asia'}, 
	'mexico_city': {'id': 3, 'country': 'mexico', 'lng': -99.1333, 'lat': 19.4333, 'radius': 0.1, 'continent': 'north_america'}, 
	'sao_paulo': {'id': 4, 'country': 'brazil', 'lng': -46.6339, 'lat': -23.5504, 'radius': 0.1, 'continent': 'south_america'}, 
	'mumbai': {'id': 5, 'country': 'india', 'lng': 72.8333, 'lat': 18.9667, 'radius': 0.1, 'continent': 'africa'}, 
	'kinki': {'id': 6, 'country': 'japan', 'lng': 135.5019, 'lat': 34.6936, 'radius': 0.1, 'continent': 'asia'}, 
	'cairo': {'id': 7, 'country': 'egypt', 'lng': 31.2394, 'lat': 30.0561, 'radius': 0.05, 'continent': 'asia'}, 
	'new_york': {'id': 8, 'country': 'america', 'lng': -73.9249, 'lat': 40.6943, 'radius': 0.1, 'continent': 'north_america'}, 
	'beijing': {'id': 9, 'country': 'china', 'lng': 116.3914, 'lat': 39.9050, 'radius': 0.1, 'continent': 'asia'}, 
}


def get_meta(lng, lat, pitch=0, heading=0, key=dev_key, fov=120, base_url=base_url, size=(640, 640), radius = 1000):

	# define parameters for street view api
	params = [{
		'size': str(size[0]) + 'x' + str(size[1]), # max 640x640 pixels
		'location': str(lat) + ',' + str(lng),
		'heading': str(heading),
		'fov': str(fov),
		'pitch': str(pitch),
		'key': str(key),
		'source': 'outdoor',
		'radius': radius,
	}]

	# creates the request url
	url = [meta_url + '?' + urlencode(p) for p in params][0]

	# gets the image from the request url
	result = requests.get(url, stream=True)

	return result.json()


def get_city_coords(city):
	data = city_info.get(city, "Invalid city")
	if(data == "Invalid city"):
		raise Exception("Invalid city!!")

	trial_lng = random.randint(int((data['lng'] - data['radius']) * 10000), int((data['lng'] + data['radius']) * 10000)) / 10000.0
	trial_lat = random.randint(int((data['lat'] - data['radius']) * 10000), int((data['lat'] + data['radius']) * 10000)) / 10000.0

	data = get_meta(trial_lng, trial_lat)

	if data.get('status') == 'OK':
		return data
	else:
		return get_city_coords(city)



def get_random_heading():
	return random.randint(0, 365)

# data = get_meta(37.699034,-75.542322, 'test_img')
# print(data)
# print(data.get('location').get('lat'))


# data  = get_city_coords('tokyo')
# print(data)


with open('image_data.csv', 'w') as csvfile:
	fieldnames = ['img_id', 'lng', 'lat', 'city_id', 'city_name', 'country', 'continent', 'heading', 'pano_id', 'date', 'img_name_0', 'img_name_1', 'img_name_2']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()

	for city in city_info.keys():
	# for city in ['tokyo']:  # only for testing 
		print("checking city: " + city)

		#download the images for the city
		for img in range(downloads_per_city):
		# for img in range(20): # only for testing
			heading = get_random_heading()
			
			# image ids
			image_id = str(city_info[city]['id']) + str(img).zfill(4)

			# final names of the images with all headings
			image_names = [
				image_id + '_' + str(heading).zfill(3) + '.jpg', 
				image_id + '_' + str((heading + 120) % 360).zfill(3) + '.jpg', 
				image_id + '_' + str((heading + 240) % 360).zfill(3) + '.jpg', 
			]

			data = get_city_coords(city)

			# throw error if the data does not hold a valid location
			if data['status'] != 'OK': raise Exception('ERROR downloading image')

			writer.writerow({
				'img_id': image_id,
				'lng': data['location']['lng'],
				'lat': data['location']['lat'],
				'city_id': city_info[city]['id'],
				'city_name': city,
				'country': city_info[city]['country'],
				'continent': city_info[city]['continent'],
				'heading': heading,
				'pano_id': data['pano_id'],
				'date': data['date'],
				'img_name_0': image_names[0],
				'img_name_1': image_names[1],
				'img_name_2': image_names[2],
			})
