"""
This is a python script to check authenticity of Named Entities in /Readact/csv/data and in SCB.
Main idea:
- Read ReadAct CSV files, get lookups
- Get the Q-identifier with library wikibaseintegrator for each lookup
- Use SPARQL to retrieve the property we need
- Compare wikidata item properties with data in ReadAct
"""
import pandas as pd
import requests
import time
from authenticity_space import read_space_csv
from langdetect import detect

URL  = "https://query.wikidata.org/sparql"

QUERY = """
        SELECT ?person ?personLabel ?ybirth ?ydeath ?birthplaceLabel ?genderLabel
        WHERE {{ 
        {{?person wdt:P31 wd:Q5 ;
                rdfs:label "{}"@{} . }} UNION {{?person wdt:P31 wd:Q5 ;
                skos:altLabel "{}"@{} . }}
        OPTIONAL {{ ?person  wdt:P569  ?birth . BIND(year(?birth) as ?ybirth) }}
        OPTIONAL {{ ?person  wdt:P570  ?death . BIND(year(?death) as ?ydeath) }}
        OPTIONAL {{ ?person wdt:P19  ?birthplace . }}
        OPTIONAL {{ ?person  wdt:P21  ?gender . }}
        OPTIONAL {{ ?person skos:altLabel ?altLabel . }}
        
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language  "[AUTO_LANGUAGE], en"}}
        }}
        GROUP BY ?person ?personLabel ?ybirth ?ydeath ?birthplaceLabel ?genderLabel
        LIMIT 250
        """


def read_person_csv(person_url="https://raw.githubusercontent.com/readchina/ReadAct/master/csv/data/Person.csv"):
    """
    A function to read "Person.csv", preprocess data.
    :param filename: "Person.csv".
    :return: a dictionary: key: (person_id, name_lang); value: [family_name,first_name,name_lang,sex,birthyear,
    deathyear]
    "name_lang" is used to decide if white space needs to be added into name or not.
    """
    df = pd.read_csv(person_url, error_bad_lines=False)
    print(df)
    person_dict = {}
    place_dict = read_space_csv()
    for index, row in df.iterrows():
        key = (row['person_id'], row['name_lang'])
        if key not in person_dict:
            birth_years =  __clean_birth_death_year_format(row['birthyear'])
            death_years = __clean_birth_death_year_format(row['deathyear'])

            # Replace space_id with the name of space
            if row['place_of_birth'] in place_dict:
                person_dict[key] = [row['family_name'], row['first_name'], row['sex'], birth_years, death_years, row['alt_name'],
                                    place_dict[str(row['place_of_birth'])][0]]
            else:
                person_dict[key] = [row['family_name'], row['first_name'], row['sex'], birth_years, death_years, row['alt_name'], row['place_of_birth']]
                print("Please check. A space_id is not in Space.csv.")
        else:
            print("Probably something wrong")
    return person_dict


def __clean_birth_death_year_format(default_year):
    char_to_remove = ['[',']','?','~']
    cleaned_year = default_year
    for c in char_to_remove:
        cleaned_year = cleaned_year.replace(c, "")

    if cleaned_year.isalpha():  # "XXXX" contain 0 information
        years = []
    elif '.' in cleaned_year:
        cleaned_year = cleaned_year.split('..')
        years = list(range(int(cleaned_year[0]), int(cleaned_year[1])+1))
    elif '-' in cleaned_year:  # For BCE year
        cleaned_year = int(cleaned_year.replace('-', ''))
        years = [cleaned_year-1, cleaned_year, cleaned_year]
    elif any([i.isalpha() for i in cleaned_year]):
        cleaned_year = [cleaned_year.replace('X', '0').replace('x', '0'), cleaned_year.replace('X', '9').replace('x', '0')]
        # Maybe consider to tickle the weight at this step already? since range(1000,2000) covers 1000 years and it
        # does not offer really useful information
        years = list(range(int(cleaned_year[0]), int(cleaned_year[1])+1))
    elif ',' in cleaned_year:
        cleaned_year = cleaned_year.split(',')
        years = list(range(int(cleaned_year[0]), int(cleaned_year[1])+1))
    else:
        years = [int(cleaned_year)]
    return years

def compare(person_dict, sleep=2):
    no_match_list = []
    for k, v in person_dict.items():
        lang = k[1]
        print("_______", v[0])
        if isinstance(v[1], float):
            lookup = v[0]
        else:
            if lang == "en":
                # Distinguish Pinyin and English
                if (k, 'zh') in person_dict:
                    print("-------this person has a chinese name")
                lookup = v[1] + " " + v[0] # Last name + " " + Family name
            elif lang == "zh":
                lookup = v[0] + v[1]
        print("----------", lookup)
    #     person = _sparql(lookup, lang, sleep)
    #
    #     # If has alt_name
    #     if isinstance(v[5], str):
    #         # print("++++++++++alt_name: ", v[5])
    #         # print("language type: ", detect(v[5]))
    #         # print("language type: ", lang)
    #         # print("will append")
    #         # print("~~~~~~~~person before appending: ", person)
    #         # Here the "lang" might need to be modified
    #         for p in _sparql(v[5], lang, sleep):
    #             person.append(p)
    #         # print("~~~~~~person after appending: ", person)
    #
    #     if len(person) == 0:
    #         print("No match: ", k, v)
    #         no_match_list.append((k, v))
    #         continue
    #     else:
    #         for p in person:
    #             if 'birthyear' in p:
    #                 for b in p['birthyear']:
    #                     if b == v[3]:
    #                         print("---A match: ", k, v)
    #                         continue
    #             elif 'deathyear' in p:
    #                 for d in p['deathyear']:
    #                     if d == v[4]:
    #                         print("---A match: ", k, v)
    #                         continue
    #             elif 'gender' in p:
    #                 if p['gender'] == v[2]:
    #                     print("---A match: ", k, v)
    #                     continue
    #             elif 'birthplace' in p:
    #                 if p['birthplace'] == v[6]:
    #                     print("---A match: ", k, v)
    #                     continue
    #             else:
    #                 no_match_list.append((k, v))
    #                 print("No match: ", k, v)
    # return no_match_list


def _sparql(lookup, lang, sleep=2):
    if len(lookup) == 0:
        return None
    person = []
    with requests.Session() as s:
        response = s.get(URL, params={"format": "json", "query": QUERY.format(lookup, lang, lookup, lang)})
        if response.status_code == 200:  # a successful response
            results = response.json().get("results", {}).get("bindings")
            if len(results) == 0:
                print("-----Didn't find:", lookup)
            else:
                # print(results)
                for r in results:
                    person_wiki = {}
                    if "ybirth" in r:
                        person_wiki["birthyear"] = r['ybirth']['value']
                    if "ydeath" in r:
                        person_wiki["deathyear"] = r['ydeath']['value']
                    if "genderLabel" in r:
                        person_wiki["gender"] = r['genderLabel']['value']
                    if "birthplaceLabel" in r:
                        person_wiki['birthplace'] = r['birthplaceLabel']['value']
                    person.append(person_wiki)
        time.sleep(sleep)
    return person


def _detectLang(text):
    pass
    # lang = detect(text)


if __name__ == "__main__":
    person_dict = read_person_csv("https://raw.githubusercontent.com/readchina/ReadAct/master/csv/data/Person.csv")

    print(person_dict)

    sample_dict = {('AG0616', 'en'): ['Qian', 'Zhongshu', 'male', '1910', '1998', "Nan", 'SP0183'], ('AG0616', 'zh'): ['钱', '钟书', 'male', '1910', '1998', "Nan", 'SP0183'], ('AG0617', 'en'): ['Qin', 'Guan', 'male', '1049', '1100', "Nan", 'SP0370'], ('AG0617', 'zh'): ['秦', '观', 'male', '1049', '1100', "Nan", 'SP0370'], ('AG0618', 'en'): ['Qu', 'Bo', 'male', '1923', '2002', "Nan", 'SP0108'], ('AG0618', 'zh'): ['曲', '波', 'male', '1923', '2002', "Nan", 'SP0108'], ('AG0619', 'en'): ['Qu', 'Yuan', 'male', '-0340', '-0278', 'Lingjun', 'SP0340'], ('AG0619', 'zh'): ['屈', '原', 'male', '-0340', '-0278', '灵均', 'SP0340'], ('AG0620', 'en'): ['Qu', 'Qiubai', 'male', '1899', '1935', "Nan", 'SP0106'], ('AG0620', 'zh'): ['瞿', '秋白', 'male', '1899', '1935', "Nan", 'SP0106'], ('AG0621', 'en'): ['Thomas', 'Dylan', 'male', '1914', '1953', "Nan", 'SP0371'], ('AG0621', 'zh'): ['托马斯', '狄兰', 'male', '1914', '1953', "Nan", 'SP0371']}

    # no_match_list = compare(person_dict, 2)
    # print("no_match_list", no_match_list)
    # print("-------length of the no_match_list", len(no_match_list))






