import unittest
import os

import jsonquery


class TestFileLoading(unittest.TestCase):
    def test_loading(self):
        data_path = os.path.join(os.path.dirname(__file__), "resources", "nwis_request.json")
        document = jsonquery.xml_from_json_file(data_path)

    def test_query(self):
        data_path = os.path.join(os.path.dirname(__file__), "resources", "nwis_request.json")
        results = jsonquery.query(data_path, "//value/timeSeries[1]/values/value/value")
        print(results)



if __name__ == '__main__':
    unittest.main()
