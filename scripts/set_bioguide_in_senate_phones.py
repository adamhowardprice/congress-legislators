from datetime import datetime
import utils
from utils import load_data, parse_date
import json

def get_sen_codes_to_bioguides():
    today = datetime.now().date()
    legislators = load_data("legislators-current.yaml")
    sen_codes_to_bioguides = {}
    for moc in legislators:
        try:
            last_term = moc["terms"][-1]
        except IndexError:
            print("Member has no terms", moc)
            continue

        if last_term["type"] != "sen":
            continue

        if today < parse_date(last_term["start"]) or today > parse_date(last_term["end"]):
            print("Member's last listed term is not current", moc, last_term["start"])
            continue

        state = last_term['state']
        sen_code = "SEN%s%02d" % (state, int(last_term['class']))
        bioguide = moc["id"]["bioguide"]
        sen_codes_to_bioguides[sen_code] = bioguide
    return sen_codes_to_bioguides

def run():
    with open("../senate_state_phones.json") as f:
        s_to_p = json.load(f)

    output = {}
    s_to_b = get_sen_codes_to_bioguides()
    for sen_code in sorted(s_to_p.keys()):
        phones = s_to_p.get(sen_code)
        bioguide = s_to_b.get(sen_code)
        output_dict = {}
        if phones is not None:
            output_dict['phones'] = phones
        if sen_code is not None:
            output_dict['sen_code'] = sen_code
        output[bioguide] = output_dict

    with open("../senate_info.json", "w") as o:
        o.write(json.dumps(output, indent=4))


if __name__ == '__main__':
    run()
