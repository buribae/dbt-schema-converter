# dbt-schema-converter

**What does this do?**

- Converts CSV file containing table and column names into yaml file for use with dbt
- Outputs resulting file as schema.yml in the directory that the source file is located

**What does this NOT do?**

- Doesn't convert back to CSV
- Doesn't convert to DDL

**Directory Structure**

```sh
.
├── Pipfile
├── README.md
├── __init__.py
├── requirements.txt
├── schema_converter.py
├── schema_input_example.csv
└── test
    ├── __init__.py
    ├── schema.yml
    ├── test_converter.py
    ├── test_input_large.csv
    ├── test_input_large.xlsx
    ├── test_input_missing_column_name.csv
    ├── test_input_missing_column_name.xlsx
    ├── test_input_missing_table_name.csv
    ├── test_input_missing_table_name.xlsx
    ├── test_input_no_column_name.csv
    ├── test_input_no_column_name.xlsx
    ├── test_input_small.csv
    ├── test_input_small.xlsx
    ├── validation_large.yml
    ├── validation_missing_column_name.yml
    ├── validation_missing_table_name.yml
    └── validation_small.yml
```

**How to run this code:**

Using [pipenv](https://github.com/pypa/pipenv)

```sh
$ pipenv shell
$ pip install -r requirements.txt
$ python schema_converter.py -s <path to source file>

EXCEL to YAML Conversion - SUCCESS
 * Converted file: schema.yml
```

**How was this tested?**

``` sh
$ pytest -v
================================== test session starts ===================================
platform darwin -- Python 3.7.6, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
rootdir: $HOME/dbt-schema-converter
collected 15 items

test/test_converter.py::test_convert_with_rel_path PASSED                          [  6%]
test/test_converter.py::test_convert_xlsx[small] PASSED                            [ 13%]
test/test_converter.py::test_convert_xlsx[large] PASSED                            [ 20%]
test/test_converter.py::test_convert_xlsx[missing_table_name] PASSED               [ 26%]
test/test_converter.py::test_convert_xlsx[missing_column_name] PASSED              [ 33%]
test/test_converter.py::test_convert_csv[small] PASSED                             [ 40%]
test/test_converter.py::test_convert_csv[large] PASSED                             [ 46%]
test/test_converter.py::test_convert_csv[missing_table_name] PASSED                [ 53%]
test/test_converter.py::test_convert_csv[missing_column_name] PASSED               [ 60%]
test/test_converter.py::test_convert_no_column_name PASSED                         [ 66%]
test/test_converter.py::test_convert_not_supported_file_type PASSED                [ 73%]
test/test_converter.py::test_write_yaml_validate_output[small] PASSED              [ 80%]
test/test_converter.py::test_write_yaml_validate_output[large] PASSED              [ 86%]
test/test_converter.py::test_write_yaml_validate_output[missing_table_name] PASSED [ 93%]
test/test_converter.py::test_write_yaml_validate_output[missing_column_name] PASSED [100%]

=================================== 15 passed in 0.72s ===================================
```