#!/usr/bin/env python3
# -*- coding: utf-8 -*-

OUTPUT_FILENAME = 'visa_edgedata.json'

from bs4 import BeautifulSoup
import json
import urllib.request
from pprint import pprint
from tqdm import tqdm
import requests

countries_list = ['Afghanistan', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'British Virgin Islands', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'Colombia', 'Comoros', 'Cook Islands', 'Costa Rica', "Cote d'Ivoire", 'Croatia', 'Cuba', 'Curaçao', 'Cyprus', 'Czech Republic', 'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'East Timor', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French West Indies', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Grenada', 'Guam', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kosovo', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macau', 'Macedonia', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 'North Korea', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', "People's Republic of China", 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Republic of China (Taiwan)', 'Republic of the Congo', 'Reunion', 'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Swaziland', 'Sweden', 'Switzerland', 'Syria', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'United States Virgin Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe']

def country2url( country ):
	'''converts the country name to the country URL'''

	country = country.replace(' ', r'%20' )

	return 'http://www.doyouneedvisa.com/passport/%s' % country

def get_htmldoc_from_doyouneedvisa( url ):

	#response = urllib.request.urlopen(url)
	response = requests.get(url)
	z = response.text
	#data = response.read()      # a `bytes` object
	#z = data.decode('utf-8') # a `str`; this step can't be used if data is binary

	return z

def rowranking2countryname( rowranking ):
	'''returns the name of the country that the row is about'''
	global countries_list

	justtherow = BeautifulSoup( str(div_rowranking), 'html5lib')
	countrydata = justtherow.find_all(attrs={"class": "col-xs-6"} )

	#print("Found instances of col-xs-6...")
	assert len(countrydata) == 2, "Didn't find two arguments.  They were %d instead." % len(countrydata)
	# the country is always the second entry
	#print("Found row for ")
	z = countrydata[1].text.strip()

	assert z in countries_list, "did not find country '%s' in the list of countries.  Something wrong?" % z

	return z

def rowranking2edgetype( rowranking ):
	'''returns the edge type for this particular rowranking'''

	#div class="col-xs-4 detail-elem info-required	
	justtherow = BeautifulSoup( str(div_rowranking), 'html5lib')
	#edgedata = justtherow.find_all(attrs={"class": "detail-elem"} )

#	edgedata = edgedata.get('class')

	# [<div class="col-xs-4 detail-elem info-onarrival"> <h6> </h6></div>,
 	# <div class="col-xs-8 detail-elem info-onarrival"><h6>  </h6> </div>]

	# soup = BeautifulSoup('<META NAME="City" content="Austin">')
	edgedata = justtherow.find("div", attrs={"class":"detail-elem"})['class']

	edgetype = [ x[len('info-'):].lower() for x in edgedata if x.startswith('info-') ]

	# assert that all of the matched edgetypes are the same.
	for x in edgetype:
		assert edgetype[0] == x, "Found multiple edgetypes.  They were: %s" % edgetype

	# since they are all the same, just get the first one.
	edgetype = edgetype[0]

	assert edgetype in ('onarrival','free','required','refused'), "Did not find the right edgetype.  Found=%s" % edgetype


	return edgetype




if __name__ == '__main__':

	z, zz = [], {}


	#for c in tqdm(countries_list):
	for from_country in countries_list:

#		if from_country[0] < 'D':
#			continue

		print("Downloading data for country", from_country)
		the_url = country2url( from_country )
		print("- url: '%s'" % the_url )

		html_doc = get_htmldoc_from_doyouneedvisa( the_url )

		soup = BeautifulSoup(html_doc, 'html5lib')

		div_rowrankings = soup.find_all(attrs={"class": "rowranking"} )

		# for each row in the list...
		for div_rowranking in div_rowrankings:
			to_country = rowranking2countryname( div_rowranking )

#			print("getting edgedata...")
			edgetype = rowranking2edgetype( div_rowranking )

			print('Found data for edge %(from_country)s -> %(to_country)s \t : %(edgetype)s' % locals() )
			triplet = (from_country, to_country, edgetype)

			z.append( triplet )
			zz.setdefault(from_country, {})
			zz[from_country][to_country] = edgetype


	# now we write this whole thing to a big JSON file

	with open(OUTPUT_FILENAME,'w') as f:
		json.dump(zz,f,indent=True)

#			input('...')

		# show me all div tags
		#div_tags = soup.find_all('div')
		#print( type(div_rowrankings) )
		#pprint( div_tags )

		'''
<div class="row rowranking ">

        <div class="col-xs-5 ">
            <div class="row ">
                                                <a href="/visa/Afghanistan/South%20Africa">
                    <div class="col-xs-6">
                        <img alt="South Africa" class="img-circle" src="/bundles/techyvisa/resizeflags/ZA/za.mini.png " style="max-width: 80px;"/>
                    </div>
                    <div class="col-xs-6">  
                        South Africa
                    </div> 
                </a>
            </div>
        </div>
        <div class="col-xs-7">
            <div class="row">
                                <div class="col-xs-4 detail-elem info-required"> <h6> </h6></div>
                <div class="col-xs-8 detail-elem info-required"><h6>  </h6> </div>
                            </div>

        </div>

    </div>
'''



			#pprint( to_country[1].contents )
			#pprint( to_country[1].string )



		#<div class="row.rowranking">
		# div.row.rowranking





