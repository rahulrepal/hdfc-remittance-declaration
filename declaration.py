"""
    Generate declaration pdf for hdfc remittance using standard template
"""
# TODO : Handle for signature
# TODO : Create cli
# TODO : Handle code to get pan no. and other data
# FIXME : fix chunky fonts
# FIXME : remove temporary file or use strings directly

from jinja2 import Environment, FileSystemLoader
import pdfkit
from zipfile import ZipFile
import pandas as pd
from datetime import datetime
import os

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, "templates")

env = Environment(
    loader=FileSystemLoader(templates_dir),
    comment_start_string="{=",
    comment_end_string="=}",
)

template = env.get_template("declaration_template.html")

temp_filepath = os.path.join(root, "temp_declaration.html")


def _validate_zip(path):
    _, ext = os.path.splitext(path)
    if ext != ".zip":
        raise ValueError("Not a zip file")


def _get_filename(path):
    splitted_path = os.path.split(path)
    if len(splitted_path) < 1 or not splitted_path[1]:
        raise ValueError("Incorrect zip path provided")
    return splitted_path[1]


def _get_xls_filename(path):
    filename = _get_filename(path)
    name, _ = os.path.splitext(filename)
    return "{}.xls".format(name)


def _get_remittance_data(zip_path):
    filename = _get_filename(zip_path)
    csv_filename = _get_xls_filename(filename)

    archive = ZipFile(zip_path, "r")
    csv_file = archive.open(csv_filename)

    df = pd.read_table(csv_file)
    remittance_data = df.to_dict("index")[0]

    return remittance_data


def _prepare_template_constants(zip_path):
    remittance_data = _get_remittance_data(zip_path)
    return {
        "branch_name": remittance_data.get("Branch"),
        "curr_date": datetime.now().strftime("%d/%m/%Y"),
        "amount": remittance_data.get("Amount", "Empty"),
        "currency": "INR",
        "remittance_date": remittance_data.get("Initiation_Date", "Empty"),
        "inward_reference_number": remittance_data.get("Customer_Ref_No", "Empty"),
        "account_number": remittance_data.get("Beneficiary_Bank_Acc", "Empty"),
        "pan_number": remittance_data.get("pan_number", "Empty"),
        "customer_number": remittance_data.get("IndiaLink_Ref_No", "Empty"),
        "purpose_desciption": remittance_data.get("Payment_Details", "Empty"),
        "rendered_from": remittance_data.get("rendered_from", "Empty"),
        "rendered_to": remittance_data.get("rendered_to", "Empty"),
    }


def _write_data(template_constants):
    with open(temp_filepath, "w") as fp:
        fp.write(template.render(**template_constants))


def _convert_to_pdf(filepath, output_path="declaration.pdf"):
    return pdfkit.from_file(filepath, output_path, options={"--print-media-type": None})


def create_declaration_pdf(zip_path, signature_path):
    if not zip_path or not signature_path:
        raise ValueError(
            "Zip path and signature path are required for generating declaration"
        )
    _validate_zip(zip_path)
    template_constants = _prepare_template_constants(zip_path)
    _write_data(template_constants)
    _convert_to_pdf(temp_filepath)
