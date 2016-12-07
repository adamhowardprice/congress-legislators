#!/usr/bin/env python

# Update current congressmen's state mailing address and phone from member's house.gov subdomain

import lxml.html, io
import re
from datetime import datetime
import utils
from utils import download, load_data, save_data, parse_date

def phone_format(phone_number):
	clean_phone_number = re.sub('[^0-9]+', '', phone_number)
	formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1-", "%d" % int(clean_phone_number[:-1])) + clean_phone_number[-1]
	return formatted_phone_number

def run():
	today = datetime.now().date()

	# default to not caching
	cache = utils.flags().get('cache', False)
	force = not cache

	y = load_data("legislators-current.yaml")

	cong_to_phones = {}
	missing = []

	for idx, moc in enumerate(y):
		print(idx)
		try:
			term = moc["terms"][-1]
		except IndexError:
			print("Member has no terms", moc)
			continue

		if term["type"] != "rep": continue

		if today < parse_date(term["start"]) or today > parse_date(term["end"]):
			print("Member's last listed term is not current", moc, term["start"])
			continue

		# Specify districts e.g. WA-02 on the command line to only update those.
		# if len(sys.argv) > 1 and ("%s-%02d" % (term["state"], term["district"])) not in sys.argv: continue

		if "class" in term: del term["class"]

		cong_code = "%s%02d" % (term["state"], term["district"])
		print(cong_code)

		if "url" not in term:
			missing.append(cong_code)
			continue

		url = term["url"]
		cache = "legislators/subdomain_house_contact/%s.html" % cong_code
		try:
			# the meta tag say it's iso-8859-1, but... names are actually in utf8...
			body = download(url, cache, force)
			dom = lxml.html.parse(io.StringIO(body)).getroot()
		except:
			print("Error parsing: ", url)
			missing.append(cong_code)
			continue

		if dom is None:
			missing.append(cong_code)
			continue

		phones = []
		phone_doms = dom.cssselect("*:contains(Phone\:)")
		for p in phone_doms:
			phone_number_string = str(p.text_content())
			phone_matches = re.search("(\(\d{3}\) \d{3}-\d{4}|\d{3}\.\d{3}\.\d{4}|\d{3}-\d{3}-\d{4})", phone_number_string)
			if phone_matches is None:
				missing.append(cong_code)
				continue
			phone_number = phone_format(phone_matches.group(0))
			if phone_number not in phones:
				phones.append(phone_number)
			if len(phones) == 0:
				missing.append(cong_code)
				continue

			cong_to_phones[cong_code] = phones

		print(phones)

	# save_data(y, "legislators-current.yaml")
	print("Got this many congress codes phone #s: {}".format(str(len(cong_to_phones))))
	print("Got these results: {}".format(cong_to_phones))
	print("Missing these congress codes: {}".format(missing))

if __name__ == '__main__':
  run()