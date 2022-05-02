import pytest
from pathlib import Path
from dbt_schema_converter import schema_converter as sc

cur_dir = Path(__file__).parent
test_file_scenarios = [
    "small",
    "large",
    "missing_table_name",
    "missing_column_name",
]


@pytest.fixture(params=test_file_scenarios)
def xlsx_files(request):
    return (
        cur_dir / f"test_input_{request.param}.xlsx",
        cur_dir / f"validation_{request.param}.yml",
    )


@pytest.fixture(params=test_file_scenarios)
def csv_files(request):
    return (
        cur_dir / f"test_input_{request.param}.csv",
        cur_dir / f"validation_{request.param}.yml",
    )


def test_convert_with_rel_path():
    """Tests conversion with relative source path"""
    relative_input_path = Path("./test/test_input_small.xlsx")
    absolute_input_path = sc.abs_path(relative_input_path)
    validation_file = sc.abs_path(Path("./test/validation_small.yml")).read_text()
    assert sc.convert(absolute_input_path) == validation_file


def test_convert_xlsx(xlsx_files):
    """Tests conversion with excel file (absolute path)"""
    test_input_path, validation_path = xlsx_files
    validation_file = open(validation_path, "r", newline="").read()
    assert sc.convert(test_input_path) == validation_file


def test_convert_csv(csv_files):
    """Tests conversion with csv file (absolute path)"""
    test_input_path, validation_path = csv_files
    validation_file = open(validation_path, "r", newline="").read()

    # Checking contents only. Ignoring unicode characters
    assert sc.convert(test_input_path) == validation_file


def test_convert_no_column_name():
    """Tests error handling on having no required column names"""
    with pytest.raises(SystemExit):
        test_input_path = cur_dir / "test_input_no_column_name.xlsx"
        sc.convert(test_input_path)


def test_convert_not_supported_file_type():
    """Tests error handling on converting wrong file format"""
    with pytest.raises(SystemExit):
        sc.convert(Path("file_path_with_no_extension"))


def test_write_yaml_validate_output(xlsx_files):
    """Tests writing yaml out to correct output"""
    test_input_path, validation_path = xlsx_files
    parsed_yaml = sc.convert(test_input_path)
    output_path = sc.write_yaml(parsed_yaml, test_input_path)
    output_file = open(output_path, "r", newline="").read()
    validation_file = open(validation_path, "r", newline="").read()
    assert output_file == validation_file
