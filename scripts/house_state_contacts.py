#!/usr/bin/env python

# Update current congressmen's state mailing address and phone from member's house.gov subdomain

import lxml.html, io
import re
from datetime import datetime
import utils
from utils import download, load_data, save_data, parse_date

def run():
	today = datetime.now().date()

	# default to not caching
	cache = utils.flags().get('cache', False)
	force = not cache

	y = load_data("legislators-current.yaml")

	for moc in y:
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

		url = term["url"]
		cong_code = "%s%02d" % (term["state"], term["district"])
		cache = "legislators/subdomain_house/%s.html" % cong_code
		try:
			# the meta tag say it's iso-8859-1, but... names are actually in utf8...
			body = download(url, cache, force)
			dom = lxml.html.parse(io.StringIO(body)).getroot()
		except lxml.etree.XMLSyntaxError:
			print("Error parsing: ", url)
			continue

		print(cong_code)
		# print(body)

		thoroughfare_dom = dom.cssselect(".office-info .thoroughfare")
		locality_dom = dom.cssselect(".office-info .locality")
		state_dom = dom.cssselect(".office-info .state")
		postal_dom = dom.cssselect(".office-info .postal-code")
		phone_fax_dom = dom.cssselect(".office-info p")

		dc_thoroughfare = str(thoroughfare_dom[0].text_content()) if len(thoroughfare_dom) > 0 else ""
		dc_locality = str(locality_dom[0].text_content()) if len(locality_dom) > 0 else ""
		dc_state = str(state_dom[0].text_content()) if len(state_dom) > 0 else ""
		dc_postal = str(postal_dom[0].text_content()) if len(postal_dom) > 0 else ""
		dc_phone_fax = str(phone_fax_dom[0].text_content()) if len(phone_fax_dom) > 0 else ""

		state_thoroughfare = str(thoroughfare_dom[1].text_content()) if len(thoroughfare_dom) > 1 else ""
		state_locality = str(locality_dom[1].text_content()) if len(locality_dom) > 1 else ""
		state_state = str(state_dom[1].text_content()) if len(state_dom) > 1 else ""
		state_postal = str(postal_dom[1].text_content()) if len(postal_dom) > 1 else ""
		state_phone_fax = str(phone_fax_dom[1].text_content()) if len(phone_fax_dom) > 1 else ""

		dc_phone_m = re.search(r"(\(\d\d\d\) \d\d\d-\d\d\d\d)", dc_phone_fax)
		state_phone_m = re.search(r"(\(\d\d\d\) \d\d\d-\d\d\d\d)", state_phone_fax)
		dc_phone = dc_phone_m.group(0) if dc_phone_m is not None else ""
		state_phone = state_phone_m.group(0) if state_phone_m is not None else ""

		dc_address = "%s %s %s %s" % (dc_thoroughfare, dc_locality, dc_state, dc_postal)
		state_address = "%s %s %s %s" % (state_thoroughfare, state_locality, state_state, state_postal)

		print("name:")
		print(moc["name"]["official_full"])
		print("dc address:")
		print(dc_address)
		print("dc_phone:")
		print(dc_phone)
		print("state_address:")
		print(state_address)
		print("state_phone:")
		print(state_phone)
		print("\n")

		term["dc_address"] = dc_address
		term["state_address"] = state_address
		term["dc_phone"] = dc_phone
		term["state_phone"] = state_phone

	save_data(y, "legislators-current.yaml")

if __name__ == '__main__':
  run()