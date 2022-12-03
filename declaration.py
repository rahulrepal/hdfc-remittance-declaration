"""
    Generate declaration pdf for hdfc remittance using standard template
"""
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
temp = os.path.join(root, "temp")

temp_html_filepath = os.path.join(temp, "declaration.html")
temp_pdf_filepath = os.path.join(temp, "declaration.pdf")


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


def _prepare_template_constants(zip_path, **data):
    remittance_data = _get_remittance_data(zip_path)
    return {
        "branch_name": data.get("branch_name", "").upper(),
        "curr_date": datetime.now().strftime("%d/%m/%Y"),
        "amount": remittance_data.get("Amount", "Empty"),
        "currency": "INR",
        "remittance_date": remittance_data.get("Initiation_Date", "Empty"),
        "inward_reference_number": remittance_data.get("Customer_Ref_No", "Empty"),
        "account_number": remittance_data.get("Beneficiary_Bank_Acc", "Empty"),
        "pan_number": data.get("pan_number", "Empty"),
        "customer_number": remittance_data.get("IndiaLink_Ref_No", "Empty"),
        "purpose_description": remittance_data.get("Payment_Details", "Empty"),
        "rendered_from": data.get("rendered_from", "Empty"),
        "rendered_to": data.get("rendered_to", "Empty"),
    }


def _write_data(template_constants):
    with open(temp_html_filepath, "w") as fp:
        fp.write(template.render(**template_constants))
        fp.flush()


def _convert_to_pdf(filepath):
    return pdfkit.from_file(
        filepath, temp_pdf_filepath, options={"--print-media-type": None}
    )


def create_declaration_pdf(zip_path, signature_path, declaration_details=None):
    if not zip_path or not signature_path:
        raise ValueError(
            "Zip path and signature path are required for generating declaration"
        )
    if not declaration_details:
        declaration_details = {}
    _validate_zip(zip_path)
    _write_data(_prepare_template_constants(
        zip_path, **declaration_details
        )
    )
    _convert_to_pdf(temp_html_filepath)
    return temp_pdf_filepath

def perform_cleanup(uploaded_files=[]):
    files_to_delete = [
        temp_html_filepath, temp_pdf_filepath
    ]

    if uploaded_files:
        files_to_delete.extend(uploaded_files)
    
    for file in files_to_delete:
        if os.path.exists(file) and os.path.isfile(file):
            os.remove(file)
    

