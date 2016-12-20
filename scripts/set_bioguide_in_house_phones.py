from datetime import datetime
import utils
from utils import load_data, parse_date
import json

def get_districts_to_bioguides():
    today = datetime.now().date()
    legislators = load_data("legislators-current.yaml")
    districts_to_bioguides = {}
    for moc in legislators:
        try:
            last_term = moc["terms"][-1]
        except IndexError:
            print("Member has no terms", moc)
            continue

        if last_term["type"] != "rep":
            continue

        if today < parse_date(last_term["start"]) or today > parse_date(last_term["end"]):
            print("Member's last listed term is not current", moc, last_term["start"])
            continue

        state = last_term['state']
        full_district = "%s%02d" % (state, int(last_term['district']))
        bioguide = moc["id"]["bioguide"]
        districts_to_bioguides[full_district] = bioguide
    return districts_to_bioguides

def run():
    with open("../house_state_phones.json") as f:
        d_to_p = json.load(f)

    output = {}
    d_to_b = get_districts_to_bioguides()
    for district in sorted(d_to_p.keys()):
        phones = d_to_p.get(district)
        bioguide = d_to_b.get(district)
        output_dict = {}
        if phones is not None:
            output_dict['phones'] = phones
        if district is not None:
            output_dict['district'] = district
        output[bioguide] = output_dict

    with open("../house_info.json", "w") as o:
        o.write(json.dumps(output, indent=4))


if __name__ == '__main__':
    run()
