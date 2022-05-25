import unittest
import log_analyzer


class StatsFunctionTest(unittest.TestCase):
    def test_find_stats(self):
        url_time_dict = {
            "first_url": [1, 2, 8, 21, 1],
            "second_url": [10, 10, 10, 10, 10, 10],
        }
        data = log_analyzer.find_stats(url_time_dict)
        expected_result = [
            {
                "url": "first_url",
                "count": 5,
                "time_med": 2,
                "time_sum": 33,
                "time_avg": 6.6,
                "time_max": 21,
                "time_perc": 35.484,
                "count_perc": 45.455,
            },
            {
                "url": "second_url",
                "count": 6,
                "time_med": 10.0,
                "time_sum": 60,
                "time_avg": 10.0,
                "time_max": 10,
                "time_perc": 64.516,
                "count_perc": 54.545,
            },
        ]
        self.assertEqual(expected_result, data)

    def test_process_file_without_errors(self):
        file_name = "log/test_log"
        result_dict = log_analyzer.process_file(file_name)
        expected_data = {
            "/api/1/photogenic_banners/list/?server_name=WIN7RB4": [0.133],
            "/api/v2/banner/16852664": [0.199],
            "/api/v2/banner/25019354": [0.39],
        }
        self.assertEqual(expected_data, result_dict)

    def test_process_file(self):
        file_name = "log/test_log_error"
        error_limit = 0.01
        with self.assertRaises(Exception) as context:
            log_analyzer.process_file(file_name, error_limit)

    def test_create_report_data(self):
        test_data = [
            {
                "count": 1,
                "count_perc": 33.333,
                "time_avg": 0.133,
                "time_max": 0.133,
                "time_med": 0.133,
                "time_perc": 18.421,
                "time_sum": 0.133,
                "url": "/api/1/photogenic_banners/list/?server_name=WIN7RB4",
            },
            {
                "count": 1,
                "count_perc": 33.333,
                "time_avg": 0.199,
                "time_max": 0.199,
                "time_med": 0.199,
                "time_perc": 27.562,
                "time_sum": 0.199,
                "url": "/api/v2/banner/16852664",
            },
            {
                "count": 1,
                "count_perc": 33.333,
                "time_avg": 0.39,
                "time_max": 0.39,
                "time_med": 0.39,
                "time_perc": 54.017,
                "time_sum": 0.39,
                "url": "/api/v2/banner/25019354",
            },
        ]
        max_report_size = 1
        expected_data = [
            {
                "count": 1,
                "count_perc": 33.333,
                "time_avg": 0.39,
                "time_max": 0.39,
                "time_med": 0.39,
                "time_perc": 54.017,
                "time_sum": 0.39,
                "url": "/api/v2/banner/25019354",
            }
        ]
        self.assertEqual(
            expected_data, log_analyzer.create_report_data(test_data, max_report_size)
        )


if __name__ == "__main__":
    unittest.main()
