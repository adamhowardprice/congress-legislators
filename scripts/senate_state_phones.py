#!/usr/bin/env python

# Update current senator's phone numbers

import lxml.html, io
import re
from datetime import datetime
import utils
import json
from utils import download, load_data, save_data, parse_date

def phone_format(phone_number):
	clean_phone_number = re.sub('[^0-9]+', '', phone_number)
	formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1-", "%d" % int(clean_phone_number[:-1])) + clean_phone_number[-1]
	return formatted_phone_number

def phone_matches(dom, search_strings):
	phones = []
	for s in search_strings:
		phone_doms = dom.cssselect("*:contains({})".format(s))
		for p in phone_doms:
			phone_number_string = str(p.text_content())
			phone_matches = re.search("(\(\d{3}\) \d{3}-\d{4}|\d{3}\.\d{3}\.\d{4}|\d{3}-\d{3}-\d{4})", phone_number_string)
			if phone_matches is None:
				continue
			phone_number = phone_format(phone_matches.group(0))
			if phone_number not in phones:
				phones.append(phone_number)
			if len(phones) == 0:
				continue
	return phones

def run():
	today = datetime.now().date()

	# default to not caching
	cache = utils.flags().get('cache', False)
	force = not cache

	y = load_data("legislators-current.yaml")

	sen_to_phones = {}
	missing = []

	for idx, moc in enumerate(y):
		print(idx)
		try:
			term = moc["terms"][-1]
		except IndexError:
			print("Member has no terms", moc)
			continue

		if term["type"] != "sen": continue

		if today < parse_date(term["start"]) or today > parse_date(term["end"]):
			print("Member's last listed term is not current", moc, term["start"])
			continue

		sen_code = "SEN%s%02d" % (term["state"], term["class"])
		print(sen_code)

		if "contact_form" not in term:
			missing.append(sen_code)
			continue

		url = term["contact_form"]

		cache = "legislators/sen_contacts/%s.html" % sen_code
		try:
			# the meta tag say it's iso-8859-1, but... names are actually in utf8...
			body = download(url, cache, force)
			dom = lxml.html.parse(io.StringIO(body)).getroot()
		except:
			print("Error parsing: ", url)
			missing.append(sen_code)
			continue

		if dom is None:
			missing.append(sen_code)
			continue

		phones = phone_matches(dom, ['Office', 'Phone', 'ph', 'tel', 'T', 't', 'P', 'p'])
		if len(phones) == 0:
			missing.append(sen_code)
		else:
			sen_to_phones[sen_code] = phones
			print(phones)

	with open("../senate_state_phones.json", "w") as o:
		o.write(json.dumps(sen_to_phones, indent=4))

	# save_data(y, "legislators-current.yaml")
	print("Got this many senate codes phone #s: {}".format(str(len(sen_to_phones))))
	print("Got these results: {}".format(sen_to_phones))
	print("Missing this many: {}".format(str(len(missing))))
	print("Missing these senate codes: {}".format(missing))

if __name__ == '__main__':
  run()