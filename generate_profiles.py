#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
# "Jinja2",
# "pdfkit",
# ]
# ///
import argparse
import csv
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import pdfkit
from jinja2 import Environment, FileSystemLoader

PDFKIT_OPTIONS = {
    "enable-local-file-access": "",
    "debug-javascript": "",
    "encoding": "UTF-8",
    "orientation": "Landscape",
    "page-size": "A4",
}

NUM_PER_FILE = 3

EDUCATION_DICT = {
    "1": "No formal education",
    "2": "Basic education",
    "3": "Some higher education",
    "4": "Degree or higher",
}

ATTITUDE_MONEY_DICT = {
    "1": "The government should completely fund services through taxes.",
    "2": "The government should subsidise the cost but individuals need to pay something for their usage.",
    "3": "Corporations should pay for services they benefit from.",
    "4": "Individuals should pay for their own use.",
}

ATTITUDE_ENVIRONMENT_DICT = {
    "1": "We need drastic change now to protect the future.",
    "2": "Significant change is needed, but comfort matters too.",
    "3": "Small changes in our habits can make a difference.",
    "4": "Technology should solve the problem, not lifestyle changes.",
}

ATTITUDE_BELONGING_DICT = {
    "1": "Local communities should decide their own spaces.",
    "2": "Government should lead, with input from everyone.",
    "3": "Developers should guide growth, as they bring investment.",
    "4": "Decisions should be made through direct democracy.",
}

ATTITUDE_EDUCATION_DICT = {
    "1": "Teach life skills and critical thinking.",
    "2": "Strong foundation in academics is essential.",
    "3": "Practical skills should be the focus.",
    "4": "Teach values and emotional intelligence first.",
}


class PDFOption(Enum):
    NONE = 0
    ONE = 1
    MANY = 2


@dataclass
class PersonaData:
    """Dataclass to hold row data from CSV file.

    This is a placeholder dataclass - you should modify the fields
    to match your actual CSV columns.
    """
    index: str
    name: str
    age: str
    gender: str
    town: str
    province: str
    economic: str
    education: str
    attitude_money_value: str
    attitude_environment_value: str
    attitude_belonging_value: str
    attitude_education_value: str

    @classmethod
    def from_dict(cls, data_dict: dict[str, Any]) -> 'PersonaData':
        """Create a PersonaData instance from a dictionary.

        This method helps with handling missing fields or extra fields
        in the CSV data.
        """

        # Person (Order),Name,Age range,Economic Stability,Gender,Age (years),Ethnicity,Province,Town,
        # Education,Money & Fairness,Environment & Daily Life,Belonging & Shared Space,Education & Next Generation,
        return cls(
            index=data_dict["Person (Order)"],
            name=data_dict["Name"],
            age=data_dict["Age (years)"],
            gender=data_dict["Gender"],
            town=data_dict["Town"],
            province=data_dict["Province"],
            economic=data_dict["Economic Stability"],
            education=data_dict["Education"],
            attitude_money_value=data_dict["Money & Fairness"],
            attitude_environment_value=data_dict["Environment & Daily Life"],
            attitude_belonging_value=data_dict["Belonging & Shared Space"],
            attitude_education_value=data_dict["Education & Next Generation"],
        )

    @property
    def education_text(self) -> str:
        return EDUCATION_DICT[self.education]

    @property
    def attitude_money_text(self) -> str:
        return ATTITUDE_MONEY_DICT[self.attitude_money_value]

    @property
    def attitude_environment_text(self) -> str:
        return ATTITUDE_ENVIRONMENT_DICT[self.attitude_environment_value]

    @property
    def attitude_belonging_text(self) -> str:
        return ATTITUDE_BELONGING_DICT[self.attitude_belonging_value]

    @property
    def attitude_education_text(self) -> str:
        return ATTITUDE_EDUCATION_DICT[self.attitude_education_value]

    @property
    def headshot_file(self) -> str:
        num_index = int(self.index)
        for file_path in Path("headshots").glob(f"{num_index:02d}*.png"):
            return file_path.name
        return "01-amina-flat-eco-nat.png"


def read_csv_to_dataclasses(csv_path: Path) -> list[PersonaData]:
    """Read CSV file and convert each row to a dataclass instance."""
    data_objects = []

    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        # Assuming the first row contains headers
        reader = csv.DictReader(csvfile)

        for row in reader:
            # Convert the row dictionary to a dataclass instance
            data_object = PersonaData.from_dict(row)
            data_objects.append(data_object)

    return data_objects


def render_html_from_template(template_path: Path, data: dict[str, Any], output_path: Path) -> None:
    """Render an HTML file using a Jinja2 template and a dataclass instance."""
    # Get the directory containing the template
    template_dir = template_path.parent
    template_file = template_path.name

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    # Render the template with the data
    rendered_html = template.render(**data)

    # Write the rendered HTML to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rendered_html)


def render_pdf_from_html(html_path: Path) -> Path:
    """ Convert HTML to PDF, return the path to the PDF """
    pdf_path = html_path.with_suffix(".pdf")
    pdfkit.from_file(str(html_path), str(pdf_path), options=PDFKIT_OPTIONS)
    return pdf_path


def render_pdf_from_many_html(html_paths: list[str], pdf_path: Path) -> None:
    " "" Convert HTML to PDF, return the path to the PDF " ""
    pdfkit.from_file(html_paths, str(pdf_path), options=PDFKIT_OPTIONS)


def page_name(start: int, people: list[PersonaData]) -> str:
    person_names = ", ".join(p.name for p in people)
    return f"Personas {start + 1} to {start + 3} ({person_names})"


def generate_html_files(
    csv_path: Path, 
    template_path: Path, 
    index_template_path: Path, 
    output_dir: Path, 
    pdf_option: PDFOption
) -> None:
    """Generate HTML files for each row in the CSV file."""
    # Read data from CSV
    data_objects = read_csv_to_dataclasses(csv_path)
    files_written = []

    for start in range(0, len(data_objects), NUM_PER_FILE):
        data_subset = data_objects[start:start + NUM_PER_FILE]

        output_name = f"persona_{start+1:02d}_{start+3:02d}.html"
        output_path = output_dir / output_name

        # Render the HTML file
        render_html_from_template(template_path, {"people": data_subset}, output_path)
        if pdf_option == PDFOption.MANY:
            render_pdf_from_html(output_path)
        files_written.append({"name": page_name(start, data_subset), "url": output_name, "path": output_path})
        print(f"Generated: {output_path}")

    # now generate the HTML file for the index
    render_html_from_template(index_template_path, {"pages": files_written}, output_dir / "index.html")
    if pdf_option == PDFOption.ONE:
        render_pdf_from_many_html([str(f["path"]) for f in files_written], output_dir / "all.pdf")



def parse_args(argv: list[str]) -> PDFOption:
    parser = argparse.ArgumentParser()
    parser.add_argument("--one-pdf", action="store_true", help="Produce one combined PDF of all the HTML files.")
    parser.add_argument("--many-pdf", action="store_true", help="Produce a PDF file for each HTML file.")
    args = parser.parse_args(argv)
    if args.one_pdf:
        if args.many_pdf:
            raise Exception("Cannot use --one-pdf and --many-pdf")
        return PDFOption.ONE
    if args.many_pdf:
        return PDFOption.MANY
    return PDFOption.NONE


def main(argv):
    pdf_option = parse_args(argv)
    # Configuration
    current_dir = Path(__file__).parent
    csv_file = current_dir / "input.csv"
    template_file = current_dir / "persona.html.jinja2"
    index_template_file = current_dir / "index.html.jinja2"
    output_directory = current_dir / "html"

    # Create output directory if it doesn't exist
    output_directory.mkdir(exist_ok=True)
    # Generate HTML files
    generate_html_files(csv_file, template_file, index_template_file, output_directory, pdf_option)

    print(f"HTML generation complete. Files saved to: {output_directory}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
