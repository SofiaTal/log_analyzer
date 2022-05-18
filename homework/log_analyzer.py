#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

import argparse
import logging
import gzip
import json
import sys
import os
import re
from datetime import datetime
from typing import List
from string import Template

config = {
    "REPORT_SIZE": 10,
    "REPORT_DIR": "./reports",
    "REPORT_TEMPLATE": "./reports/template/report.html",
    "LOG_DIR": "./log",
}

LOG_RECORD_RE = (
    "^"
    "\S+ "  # remote_addr
    "\S+\s+"  # remote_user (note: ends with double space)
    "\S+ "  # http_x_real_ip
    "\[\S+ \S+\] "  # time_local [datetime tz] i.e. [29/Jun/2017:10:46:03 +0300]
    '"\S+ (?P<href>\S+) \S+" '  # request "method href proto" i.e. "GET /api/v2/banner/23815685 HTTP/1.1"
    "\d+ "  # status
    "\d+ "  # body_bytes_sent
    '"\S+" '  # http_referer
    '".*" '  # http_user_agent
    '"\S+" '  # http_x_forwarded_for
    '"\S+" '  # http_X_REQUEST_ID
    '"\S+" '  # http_X_RB_USER
    "(?P<time>\d+\.\d+)"  # request_time
)

DEFAULT_CONFIG_PATH = "config.json"


def logger(log_path):
    if log_path:
        log_dir = os.path.split(log_path)[0]
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
    logging.basicConfig(
        filename=log_path,
        filemode="w",
        level=logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )


def merge_config(default_config, custom_config):
    if custom_config is None:
        return default_config
    if not os.path.isfile(custom_config):
        raise FileNotFoundError("Config file doesn't exist")
    with open(custom_config, "rb") as cf:
        config_file = json.load(cf)
        for key, value in default_config.items():
            if key in config_file:
                continue
            else:
                config_file[key] = default_config[key]
    return config_file


def find_last_log_file(log_path=config["LOG_DIR"]):
    if not os.path.isdir(log_path):
        return None, None

    files = os.listdir(log_path)
    regex = r"^nginx-access-ui\.log-\d{8}(\.gz)?$"
    if files:
        dates = (filename[20:28] for filename in files if re.match(regex, filename))
        datetime_list = [datetime.strptime(date, "%Y%m%d") for date in dates]
        if datetime_list:
            last_date = max(datetime_list)
            for file in files:
                if last_date.strftime("%Y%m%d") in file:
                    return file, last_date.strftime("%Y.%m.%d")
    return None, None


def process_file(file, errors_limit=None):
    if file.endswith(".gz"):
        func = gzip.open
    else:
        func = open
    result_dict = {}
    errors = 0
    lines = 0
    with func(file, "rb") as log:
        for line in log:
            line = line.decode("utf-8")
            data = re.search(LOG_RECORD_RE, line)
            lines += 1
            if data:
                datadict = data.groupdict()
                url = datadict["href"]
                time = float(datadict["time"])
                if url in result_dict:
                    result_dict[url].append(time)
                else:
                    result_dict[url] = [time]
            else:
                errors += 1
    if errors_limit and lines > 0 and errors / lines > errors_limit:
        raise RuntimeError("Max limit of errors achieved")
    return result_dict


def find_median(time_list):
    n = len(time_list)
    index = n // 2
    sort = sorted(time_list)
    if n % 2:
        return sort[index]
    return (sort[index - 1] + sort[index]) / 2


def find_stats(result_dict) -> List[dict]:
    total_count = 0
    total_time = 0
    data = []
    for url, time_list in result_dict.items():
        count = len(time_list)
        median = round(find_median(time_list), 3)
        time_sum = round(sum(time_list), 3)
        time_avg = round(time_sum / count, 3)
        max_time = max(time_list)
        total_time += time_sum
        total_count += count
        data.append(
            {
                "url": url,
                "count": count,
                "time_med": median,
                "time_sum": time_sum,
                "time_avg": time_avg,
                "time_max": max_time,
            }
        )
    for dic in data:
        dic["time_perc"] = round(dic["time_sum"] / total_time * 100, 3)
        dic["count_perc"] = round(dic["count"] / total_count * 100, 3)
    return data


def create_report_data(log_data, max_report_size=None):
    if not log_data:
        log_data = []
    sort = sorted(log_data, key=lambda log: log["time_sum"], reverse=True)
    if max_report_size:
        return sort[0:max_report_size]
    return sort


def render_report(data, filename, template_dir):
    with open(template_dir, encoding="utf-8") as temp:
        template = Template(temp.read())
    with open(filename, "w", encoding="utf-8") as fh:
        report = template.safe_substitute(table_json=data)
        fh.write(report)


def main(config_file=None):
    file, date = find_last_log_file(config_file["LOG_DIR"])
    if not file:
        logging.info("There is no matching files in log directory")
        return

    report_path = os.path.normpath(
        os.path.join(config_file["REPORT_DIR"], f"report-{date}.html")
    )
    if os.path.isfile(report_path):
        logging.info("Report with the latest date already exist")
        return

    file_path = os.path.join(config_file["LOG_DIR"], file)
    url_time_dict = process_file(file_path, config_file.get("ERROR_LIMIT"))
    log_data = find_stats(url_time_dict)
    data_for_report = create_report_data(log_data, config_file["REPORT_SIZE"])

    render_report(data_for_report, report_path, config_file["REPORT_TEMPLATE"])
    logging.info(f"Report saved to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping script")

    parser.add_argument(
        "--config", dest="config", required=False, default=DEFAULT_CONFIG_PATH
    )

    args = parser.parse_args()
    conf = merge_config(config, args.config)
    logger(conf.get("LOG_FILE"))
    try:
        main(conf)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
