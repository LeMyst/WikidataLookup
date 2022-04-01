import unittest
import pandas as pd
from datetime import date
from src.scripts.command_line_tool import check_each_row, get_last_id


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.column_names = ['person_id', 'family_name', 'first_name', 'name_lang', 'sex', 'birthyear', 'deathyear',
                             'place_of_birth', 'wikidata_id', 'created', 'created_by',
                             'last_modified', 'last_modified_by', 'note']
        self.l = ['', '', '', '', '', '', '', '', '', '', '', '', '', '']
        self.df = pd.DataFrame([self.l])
        self.df.columns = self.column_names
        self.df_person_gh = pd.read_csv('../src/CSV/df_person_Github_fake.csv')  # unofficial version
        self.last_person_id, self.person_ids_gh, self.wikidata_ids_GH = get_last_id(self.df_person_gh)
        self.today = date.today().strftime("%Y-%m-%d")

    def test_should_skip_expect_no_change(self):
        self.l = ['AG0001', '鲁', '迅', 'zh', 'male', '0000', '0000', 'Shaoxing', 'Q23114', '2021-12-22', 'QG', '', '',
                  'skip']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist(), ['AG0001', '鲁', '迅', 'zh', 'male', '0000',
                                                                            '0000', 'Shaoxing', 'Q23114', '2021-12-22',
                                                                            'QG', '', '', 'skip'])

    def test_should_NOT_skip(self):
        self.l = ['AG0001', '鲁', '迅', 'zh', 'male', '0000', '1111', 'Shaoxing', 'Q23114', '2021-12-22', 'QG', '', '',
                  '']
        self.df.loc[0] = self.l
        self.assertNotEqual(
            check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                           self.wikidata_ids_GH)[0].tolist()[0:-1],
            ['AG0001', '鲁', '迅', 'zh', 'male', '1881', '1936', 'Shaoxing', 'Q23114', '2021-12-22', 'QG', self.today,
             'SemBot'])

    def test_should_match_all_expect_no_change(self):
        self.l = ['AG0001', '鲁', '迅', 'zh', 'male', '1881', '1936', 'SP0048', 'Q23114', '2017-07-03', 'LH',
                  '2020-04-02',
                  'DP', '']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist()[0:-1],
                         ['AG0001', '鲁', '迅', 'zh', 'male', '1881',
                          '1936', 'SP0048', 'Q23114', '2017-07-03', 'LH', '2020-04-02', 'DP'])

    def test_should_two_ids_match_but_other_person_infos_NOT_match_expect_overwrite_with_ReadAct(self):
        self.l = ['AG0001', '鲁', '迅', 'zh', 'male', '1881', '1936', 'Shaoxing', 'Q23114', '2021-12-22', 'QG', '', '',
                  '']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist()[0:-1],
                         ['AG0001', '鲁', '迅', 'zh', 'male', '1881',
                          '1936', 'SP0048', 'Q23114', '2017-07-03', 'LH', '2020-04-02', 'DP'])

    def test_should_same_personID_has_different_wikiIds_expect_error(self):
        self.l = ['AG0001', '鲁', '迅', 'zh', 'male', '1881', '1936', 'Shaoxing', 'Q00000000', '2021-12-22', 'QG', '', '',
                  '']
        self.df.loc[0] = self.l
        with self.assertRaises(SystemExit) as cm:
            check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                           self.wikidata_ids_GH)
        self.assertEqual(cm.exception.code, None)

    def test_should_new_person_but_given_wikiId_already_in_ReadAct_expect_error(
            self):
        self.l = ['AG1200', 'Monet', 'Claude', 'en', 'male', '1840', '1926', 'Paris', 'Q23114', '2021-12-22', 'QG', '',
                  '', '']
        self.df.loc[0] = self.l
        with self.assertRaises(SystemExit) as cm:
            check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                           self.wikidata_ids_GH)
        self.assertEqual(cm.exception.code, None)

    def test_should_two_new_ids_and_person_infos_match_WikiData_infos_expect_no_change(
            self):
        self.l = ['AG1200', 'Monet', 'Claude', 'en', 'male', '1840', '1926', 'Paris', 'Q296', '2021-12-22', 'QG', '',
                  '', '']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist()[0:-1], ['AG1200', 'Monet', 'Claude', 'en',
                                                                                  'male', '1840', '1926', 'Paris',
                                                                                  'Q296',
                                                                                  '2021-12-22', 'QG', '', ''])

    def test_should_two_new_ids_and_person_infos_NOT_match_WikiData_expect_updating_unmached_cells(
            self):
        self.l = ['AG1200', 'Monet', 'Claude', 'en', '', '', '', '', 'Q296', '2021-12-22', 'QG', '',
                  '', '']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist()[0:-1], ['AG1200', 'Monet', 'Claude', 'en',
                                                                                  'male', '1840', '1926', 'Paris',
                                                                                  'Q296', '2021-12-22', 'QG',
                                                                                  self.today, 'SemBot'])

    def test_should_new_person_but_queried_wikiId_already_in_ReadAct_expect_error(
            self):
        self.l = ['AG1200', '鲁', '迅', 'zh', '', '', '', '', '', '2021-12-22', 'QG', '', '', '']
        self.df.loc[0] = self.l
        with self.assertRaises(SystemExit) as cm:
            check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                           self.wikidata_ids_GH)
        self.assertEqual(cm.exception.code, None)

    def test_should_new_person_has_infos_match_WikiData_infos_expect_only_update_WikiId(
            self):
        self.l = ['AG1200', 'Monet', 'Claude', 'en', 'male', '1840', '1926', 'Paris', '', '2021-12-22', 'QG', '',
                  '', '']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist()[0:-1], ['AG1200', 'Monet', 'Claude', 'en',
                                                                                  'male', '1840', '1926', 'Paris',
                                                                                  'Q296', '2021-12-22', 'QG',
                                                                                  self.today, 'SemBot'])

    def test_should_new_person_has_infos_NOT_match_WikiData_expect_update_with_WikiData(
            self):
        self.l = ['AG1200', 'Monet', 'Claude', 'en', 'male', '1840', '1926', 'Tokyo', '', '2021-12-22', 'QG', '',
                  '', '']
        self.df.loc[0] = self.l
        self.assertEqual(check_each_row(0, self.df.iloc[0], self.df_person_gh, self.person_ids_gh, self.last_person_id,
                                        self.wikidata_ids_GH)[0].tolist()[0:-1], ['AG1200', 'Monet', 'Claude', 'en',
                                                                                  'male', '1840', '1926', 'Paris',
                                                                                  'Q296',
                                                                                  '2021-12-22', 'QG', self.today,
                                                                                  'SemBot'])  #
        # should
        # test the warning
        # clean up after testing updated files


if __name__ == '__main__':
    unittest.main()
