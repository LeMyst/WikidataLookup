import argparse
import time
import pandas as pd
import requests

from authenticity_person import order_name_by_language, get_Qid_from_wikipedia_url, sparql_with_Qid, sparql_by_name

data_dictionary_github = "https://raw.githubusercontent.com/readchina/ReadAct/master/csv/data_dictionary.csv"
person_csv_github = "https://raw.githubusercontent.com/readchina/ReadAct/master/csv/data/Person.csv"

def update(df, dict):
    flag = False
    if 'gender' in dict:
        df.at[index, 'sex'] = dict['gender']
        flag = True
    if 'birthyear' in dict:
        df.at[index, 'birthyear'] = dict['birthyear']
        flag = True
    if 'deathyear' in dict:
        df.at[index, 'deathyear'] = dict['deathyear']
        flag = True
    if 'birthplace' in dict:
        df.at[index, 'birthplace'] = dict['birthplace']
        flag = True
    if flag:
        df.at[index, 'last_modified'] = time.strftime("%Y-%m-%d", time.localtime())
        df.at[index, 'last_modified_by'] = 'SemBot'
    return df

if __name__ == "__main__":
    required_columns = ['person_id', 'family_name', 'first_name', 'name_lang', 'sex',
                        'birthyear', 'deathyear', 'birthplace', 'wikipedia_link', 'wikidata_id', 'created',
                        'created_by',
                        'last_modified',
                        'last_modified_by', 'note']  # 'wikipedia_link','wikidata_id' are waiting for discussion

    # parser = argparse.ArgumentParser(description='Validate CSV columns and auto fill information for Person')
    # parser.add_argument('person_csv', type=str, help="Path of the CSV file to be autofilled")
    # parser.add_argument('--update', help='Iteration through CSV and update it')
    # parser.add_argument('--version', action='version', version='version 1.0.0')
    #
    # args = parser.parse_args()
    #
    # #################################################################
    # # 1. Check the input Person.csv
    # #################################################################
    # if not args.person_csv.endswith('Person.csv'):
    #     print('File invalid. You should use only Person.csv as the first argument\n')
    # else:
    #     print("--> Validate 1/2 \nPerson.csv is going to be checked.\n")
    #
    # df = pd.read_csv(args.person_csv, index_col=0)

    path = '../CSV/Person.csv'
    df = pd.read_csv(path, index_col=0)
    df = df.fillna('')  # Replace all the nan into empty string
    # print(df)
    if not set(required_columns).issubset(df.columns.tolist()):
        print('There must be 14 mandatory columns in CSV table. Please check your file\n')
    else:
        print("--> Validate 2/2 \nAll 14 mandatory columns are included. Well done!\n\n")

    # In the future, should also check if family_name, first_name, name_lang are empty.
    # This three are mandatory.

    #################################################################
    # 2. Update Person.csv
    #################################################################

    df_person_Github = pd.read_csv(person_csv_github)
    person_ids_GitHub = df_person_Github['person_id'].tolist()

    for index, row in df.iterrows():
        if row['person_id'] in person_ids_GitHub: # Should we just leave this line there or compare all the columns
            pass
            # This section needs to be entirely rewrite according to a better designed strategy.
            # # with ReadAct?
            # if len(row['wikipedia_link']) < 1:
            #     for index_GitHub, row_GitHub in df_person_Github.iterrows():
            #         if row_GitHub['person_id'] == row['person_id']:
            #             if isinstance(row_GitHub['source_1'], str) and ".wikipedia.org/wiki/" in row_GitHub['source_1']:
            #                 wikipdia_link = row_GitHub['source_1']
            #             elif isinstance(row_GitHub['source_2'], str) and ".wikipedia.org/wiki/" in row_GitHub['source_2']:
            #                 wikipdia_link = row_GitHub['source_2']
            #             else:
            #                 wikipdia_link = ''
            #
            #             if wikipdia_link is not None:
            #                 wikidata_id = get_Qid_from_wikipedia_url(row_GitHub)
            #             else:
            #                 wikidata_id = ''
            # if len(row['wikidata_id']) < 1:
            #     pass
            # # here we must check if wikidata is already existed after the checking of wikipedia link
            #
            # # And then check if wikipedia_link field is empty or not:
            # for index_GitHub, row_GitHub in df_person_Github.iterrows():
            #     if row_GitHub['person_id'] == row['person_id']:
            #         if isinstance(row_GitHub['source_1'], str) and ".wikipedia.org/wiki/" in row_GitHub['source_1']:
            #             wikipdia_link = row_GitHub['source_1']
            #         elif isinstance(row_GitHub['source_2'], str) and ".wikipedia.org/wiki/" in row_GitHub['source_2']:
            #             wikipdia_link = row_GitHub['source_2']
            #         else:
            #             wikipdia_link = ''
            #
            #         if wikipdia_link is not None:
            #             wikidata_id = get_Qid_from_wikipedia_url(row_GitHub)
            #         else:
            #             wikidata_id = ''
            #             df.loc[index] = [row['person_id'], row_GitHub['family_name'], row_GitHub['first_name'],row_GitHub[
            #                              'name_lang'], row_GitHub['sex'], row_GitHub['birthyear'],row_GitHub['deathyear'],
            #                              row_GitHub['place_of_birth'], wikipdia_link, wikidata_id, row_GitHub['created'],
            #                              row_GitHub['created_by'], time.strftime("%Y-%m-%d", time.localtime()),'SemBot']
        else:
            if len(row['wikidata_id']) > 0:
                pass
            #     dict = sparql_with_Qid(row['wikidata_id'])
            #     df = update(df, dict)
            #     # Here, in the future, can check if name returned by SPARQL in a list of family_name, first_name
            #     # combinations.
            # elif len(row['wikipedia_link']) > 0:
            #     link = row['wikipedia_link']
            #     if len(link) > 30:
            #         language = link[8:10]
            #         name = link[30:]
            #         # Use MediaWiki API to query
            #         link = "https://" + language + ".wikipedia.org/w/api.php?action=query&prop=pageprops&titles=" + \
            #                name + "&format=json"
            #         response = requests.get(link).json()
            #         if 'pageprops' in list(response['query']['pages'].values())[0]:
            #             pageprops = list(response['query']['pages'].values())[0]['pageprops']
            #         if 'wikibase_item' in pageprops:
            #             Qid = list(response['query']['pages'].values())[0]['pageprops']['wikibase_item']
            #     df.at[index, 'wikidata_id'] = Qid
            #     dict = sparql_with_Qid(Qid)
            #     df = update(df, dict)
            #     # Here, in the future, can check if name returned by SPARQL in a list of family_name, first_name
            #     # combinations.

            else:
                name_ordered = order_name_by_language(row)
                person = sparql_by_name(name_ordered, row['name_lang'], 2)
                if len(person) == 0:
                    print("There is no match for this person entry with row index ", index)
                    pass
                else:
                    weight = 0
                    weights = []
                    wiki = []
                    for Q_id, p in person.items():
                        # all the matched fields will add weight 1 to the total weight for this Q_id
                        if 'gender' in p:
                            if p['gender'] == row['sex']:
                                weight += 1
                        elif 'birthyear' in p:
                            if p['birthyear'] in row['birthyear']:
                                weight += 1
                        elif 'deathyear' in p:
                            if p['deathyear'] in row['deathyear']:
                                weight += 1
                        elif 'birthplace' in p:
                            if p['birthplace'] == row['birthplace']:
                                weight += 1
                        weights.append(weight)
                        wiki.append(p)
                        weight = 0
                    if len(wiki) > 0:
                        max_value = max(weights)
                        max_index = weights.index(max_value)  # return the first match
                        if max_value == 0:
                            dict = wiki[0]
                        else:
                            dict = wiki[max_index]
                        df = update(df, dict)
                        df['note'] = "uncertain match"
                    else:
                        print('There is no match for row with index ', index)
                        print('Here is the information contained in this row: \n', row)

    # For statistics:
    updated_rows_sum = df['last_modified_by'].value_counts().SemBot
    rows_sum = len(df.index)
    print(
        "==================================\n==========  Update      "
        "==========:\n==================================\nFinished "
        "Updating\n\n")
    print("==================================\n==========  Statistics  "
          "==========\n==================================\nAmong all the ", rows_sum, " rows, you have ",
          updated_rows_sum, " rows updated\n\n")

    with open('../CSV/Person_updated.csv', 'w') as f:
        f.write(df.to_csv())