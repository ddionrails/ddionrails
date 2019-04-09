from ddionrails.imports.helpers import read_csv


class TestHelpers:
    def test_read_csv(self):
        filename = "sample.csv"
        path = "tests/imports/test_data"
        csv = read_csv(filename, path)
        print(csv)
        assert "study_name" in csv[0].keys()

    def test_read_csv_without_path(self, mocker):
        mocked_open = mocker.patch("builtins.open")
        mocked_csv_dict_reader = mocker.patch("csv.DictReader")
        return_value = [dict(study_name="soep-core", dataset_name="abroad")]
        mocked_csv_dict_reader.return_value = return_value
        filename = "sample.csv"
        content = read_csv(filename)
        mocked_open.assert_called_once_with(filename, "r")
        mocked_csv_dict_reader.assert_called_once()
        assert "study_name" in content[0].keys()
