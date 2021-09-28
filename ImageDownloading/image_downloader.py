import csv
import requests
try:
  from urllib.parse import urlencode
except ImportError:
  from urllib import urlencode
import shutil
from os import path, makedirs
import os.path


# dev key keep secret!! 
dev_key = 'AIzaSyBIvaJZHj8QxpYQ7YxWn-Uj44anXgfTfQU'

base_url = "https://maps.googleapis.com/maps/api/streetview"
meta_url = "https://maps.googleapis.com/maps/api/streetview/metadata"

def download_img(lng, lat, name, pitch=0, heading=0, key=dev_key, fov=120, base_url=base_url, size=(640, 640)):

	# define parameters for street view api
	params = [{
		'size': str(size[0]) + 'x' + str(size[1]), # max 640x640 pixels
		'location': str(lat) + ',' + str(lng),
		'heading': str(heading),
		'fov': str(fov),
		'pitch': str(pitch),
		'key': str(key),
		'source': 'outdoor',
		'radius': 1000,
	}]

	# creates the request url
	url = [base_url + '?' + urlencode(p) for p in params][0]

	# gets the image from the request url
	img = requests.get(url, stream=True)

	# creates a download folder if it dose not already exist
	if not path.isdir('images'):
		makedirs('images')


	# opens and writes the output image file
	with open('images/' + name + '.jpg', 'wb') as f:
		img.raw.decode_content = True
		shutil.copyfileobj(img.raw, f)



with open('image_data.csv', 'r') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		# all headings we will take a picture at
		headings = [
			int(row['heading']),
			(int(row['heading']) + 120) % 360,
			(int(row['heading']) + 240) % 360,
		]


		# final names of the images with all headings
		image_names = [
			row['img_id'] + '_' + str(headings[0]).zfill(3), 
			row['img_id'] + '_' + str(headings[1]).zfill(3), 
			row['img_id'] + '_' + str(headings[2]).zfill(3), 
		]
		
		for index in range(3):
			if not(os.path.exists('images/' + image_names[index] + '.jpg')):
				print("downloading: " + image_names[index])
				download_img(row['lng'], row['lat'], image_names[index], heading=headings[index])

