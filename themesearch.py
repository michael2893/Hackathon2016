import urllib.request
from bs4 import BeautifulSoup
import pdb

def candidate_destinations(theme, cnt):
	citylist, countrylist = [], []
	response = urllib.request.urlopen('http://www.booking.com/destinationfinder/%s.html' % (theme))
	src = str(response.read())
	soup = BeautifulSoup(src, 'html.parser')

	# Search for cities
	matches = soup.find_all(attrs="city_name")
	matches.extend(soup.find_all(attrs="min_city_name"))
	for match in matches:
		txt = match.get_text().replace("\n", "")
		if(txt.find(",") > 0):
			citylist.append(txt[:txt.find(",")])
		else:
			citylist.append(txt)

	# Search for countries
	matches = soup.find_all(attrs="country_name")
	matches.extend(soup.find_all(attrs="min_country_name"))
	for match in matches:
		txt = match.get_text().replace("\n", "")
		if(txt.find(",") > 0):
			countrylist.append(txt)
		else:
			countrylist.append(txt)

	return [(citylist[idx], countrylist[idx]) for idx in range(len(citylist))]


res = candidate_destinations("tranquility", 5)