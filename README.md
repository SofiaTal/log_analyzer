# Log Analyzer

-----
### First Otus Homework

This repository contains python script for first Otus homework
and all necessary repos for test it. Requirements for it you can see [here](homework.pdf).

Example of report rendering with script including 10 most loaded URL's you can see [here](reports/report-2018.06.30.html).
It matches with example report.

### Directories and files

- **log**

   Directory where script by default will search files with nginx log.
   Template for log-file name is `nginx-access-ui.log-{date}.*` (plain or .gzip)
- **reports**

   Directory where script by default will write a report.
   Reports name will include access log date in format `report-{date}.html`
- **reports/template**

   Directory contains render template for creating report
- **config.json**

   Example of config json, which includes all essential parametrs.
   * **REPORT_SIZE** - number of urls with maximum time_sum to include in report (integer)
   * **REPORT_DIR** - path to dir to create reports
   * **REPORT_TEMPLATE** - path to custom rendering template (variable `$table_json` is necessary)
   * **LOG_DIR** - path to dir with logs to analyze
   * **LOG_FILE** - path to file with script log (include all unexpected exceptions and some info). If None - log will be in stdout
   * **ERROR_LIMIT** - fractional number of acceptable errors (float)

   You may pass own parametrs by creating new config.json

### To run

```
$ python log_analyzer.py                                        # for running with default parametrs
$ python log_analyzer.py --config {path_to_your_config.json}    # for running with custom config
$ python log_tests.py                                           # for running tests
```

### To develop

#### Pre-commit hook
I am using black, pylint and pre-commit to care about code formatting and linting.

So you have to install pre-commit hook before you do something with code.

```
$ pip install pre-commit # Or do it with your preffered way to install pip packages
$ pre-commit install
```

After this you will see invocation of black and pylint on every commit.
