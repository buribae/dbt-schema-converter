import pandas as pd
import numpy as np
import argparse
from pathlib import Path

# Constants for parsing input excel file columns
TABLE_NAME = "Table Name"
TABLE_DESC = "Table Description"
COL_NAME = "Column Name"
COL_DESC = "Column Description"
TESTS = "Tests"


def main():
    """Convert excel file to schema.yml for dbt

    Converts .xlsx or .csv file into a schema.yml.
    [ file -> {Table} -> yaml ]

    Example usage:
      $ python schema_converter.py -s <path to source file>

    Help:
      $ python schema_converter.py -h

    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--source_file_path",
        dest="source_file_path",
        type=Path,
        help="Path to source file (can be either full path or relative path)",
        required=True,
    )
    p = parser.parse_args()

    source = abs_path(p.source_file_path)
    parsed_yaml = convert(source)
    output_path = write_yaml(parsed_yaml, source)

    print("\nEXCEL to YAML Conversion - SUCCESS", end="\n * ")
    print("Converted file: %s" % output_path)


class Column:
    """A class used to represent a Column.

    Attributes:
        name: A string indicating the name of the column.
        description: A string that describes the column.
        tests: A list of tests ino the column.

    """

    def __init__(self, name, description, tests=[]):
        """Inits Column with name, description, and tests."""
        self.name = name
        self.description = description
        self.tests = tests

    def __str__(self):
        """Returns name, description, tests in yaml form."""

        nl = "\n"  # new line character

        # Column name
        name = f"{nl}      - name: {self.name}"

        # Column description if exists
        description = (
            f'{nl}        description: "{self.description}"' if self.description else ""
        )

        # Tests
        tests_header, tests = "", ""
        if self.tests:
            tests_header = f"{nl}        tests:"
            tests = "".join([f"{nl}          - {test}" for test in self.tests])

        return "".join([name, description, tests_header, tests, nl])

    def add_test(self, test):
        """Appends test to the tests list."""
        self.tests.append(test)


class Table:
    """A class used to represent a  Table.

    One Table can have multiple columns.

    Attributes:
        name: A string indicating the name of the table.
        description: A string that describes the table.
        columns: A list of columns in the table.

    """

    def __init__(self, name, description="", columns=[]):
        """Inits Column with name, description, and columns."""
        self.name = name
        self.description = description
        self.columns = columns

    def __str__(self):
        """Returns name, description, in yaml form."""

        nl = "\n"  # new line character

        # Table name
        name = f"{nl}  - name: {self.name}"

        # Table description if exists
        description = (
            f'{nl}    description: "{self.description}"' if self.description else ""
        )

        # Columns
        columns_header, columns = "", ""
        if self.columns:
            columns_header = f"{nl}    columns:"
            columns = "".join([str(col) for col in self.columns])

        return "".join([name, description, columns_header, columns])

    def add_column(self, column):
        """Appends column to the columns list."""
        self.columns.append(column)


def abs_path(file_path):
    """Converts relative path into an absolute path.

    Args:
        file_path: A Path object for the input.

    Returns:
        A processed Path.

    """
    # Handle relative path & absolute path
    # - Path is relative when Path.anchor is empty
    file_path = (
        (Path(__file__).parent / file_path) if file_path.anchor == "" else file_path
    )

    return file_path


def get_file(file_path):
    """Reads data from an excel file.

    Reads data dynamically from .csv or .xlsx using pandas library.

    Args:
        file_path: A Path object for the input (absoulte file path).

    Returns:
        A processed data read from input excel file.

    Raises:
        SystemExit: Exit out when file is in wrong format.

    """
    extension = file_path.suffix

    # Exit out when file is not in csv or xlsx format
    if extension != ".csv" and extension != ".xlsx":
        print("\nEXCEL to YAML Conversion - FAILED", end="\n * ")
        print("schema_converter only supports csv or xlsx files")
        raise SystemExit

    # Read in data using pandas library
    data = (
        pd.read_excel(file_path)
        if extension == ".xlsx"
        else pd.read_csv(file_path, encoding="latin-1")
    )

    # Check required columns
    required_cols = [TABLE_NAME, TABLE_DESC, COL_NAME, COL_DESC, TESTS]
    for col in required_cols:
        if col not in data.columns.values:
            print(
                f"\nEXCEL to YAML Conversion - FAILED\n",
                f"---------------------\n",
                f"* Required Columns: \n",
                f"{', '.join(required_cols)}\n\n",
                f"---------------------\n",
                f"* Actual Columns Found:\n{', '.join(data.columns.values)}",
            )
            raise SystemExit

    # Drop rows with no values
    data = data.dropna(how="all")

    # Handle empty cells using numpy library
    data = data.replace(np.nan, "", regex=True)

    return data


def get_table_dict(data):
    """Converts data into a dictionary of Table objects.

    Args:
        data: A data ready to be processed for making a dict of Table objects.

    Returns:
        A dictionary of Table objects generated from input.

    """
    table_dict = {}
    for _, row in data.iterrows():
        name = row[TABLE_NAME]

        # Create table if not exists already
        if name not in table_dict.keys():
            table_dict[name] = Table(name, "", [])

        # Add table description if exists
        table_dict[name].description = row[TABLE_DESC] if row[TABLE_DESC] else ""

        # Create column
        col = Column(row[COL_NAME], row[COL_DESC], [])

        for test in row[TESTS].split("|"):
            if test:
                col.add_test(test)  # Add tests to column

        table_dict[name].add_column(col)  # Add column to table

    return table_dict


def get_yaml(table_dict):
    """Converts Table dictionary into a yaml string.

    Args:
        table_dict: A dictionary of Table objects.

    Returns:
        A yaml form of all Table objects.

    """
    yaml = "version: 2 \n\n"
    yaml += "models:"
    for table in table_dict.values():
        yaml += str(table)
    return yaml


def convert(input_path):
    """Converts excel file to yaml for dbt

    A wrapper function for running all conversion process.
    Conversion ignores any unicode strings.

    Args:
        table_dict: A dictionary of Table objects.

    Returns:
        A yaml form of all Table objects.

    """
    file = get_file(input_path)
    parsed_yaml = get_yaml(get_table_dict(file))

    return parsed_yaml.encode("ascii", "ignore").decode("ascii")


def write_yaml(yaml_txt, path):
    """Writes yaml file to the given path using pathlib.

    Args:
        yaml_txt: A string in yaml format.

    Returns:
        A full output path where yaml was saved.

    """
    output_path = path.parent / "schema.yml"
    output_path.write_text(yaml_txt)

    return output_path


if __name__ == "__main__":
    main()
