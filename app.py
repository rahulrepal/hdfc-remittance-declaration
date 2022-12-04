from flask import Flask, render_template, request, send_file, make_response
from declaration import create_declaration_pdf, perform_cleanup

import os

root = os.path.dirname(os.path.abspath(__file__))
temp = os.path.join(root, "temp")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(root, "upload")


def save_file(file):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    return filepath


@app.route("/", methods=["GET", "POST"])
def home_page():
    if request.method == "POST":
        zip_file = save_file(request.files["zip_file"])
        signature_file = save_file(request.files["signature_image"])
        declaration_details = {
            "name": request.form.get("name"),
            "branch_name": request.form.get("branch_name"),
            "pan_number": request.form.get("pan_number"),
            "rendered_from": request.form.get("rendered_from"),
            "rendered_to": request.form.get("rendered_to"),
        }
        print(zip_file)
        filepath = create_declaration_pdf(zip_file, signature_file, declaration_details)
        response = make_response(
            send_file(
                filepath,
                mimetype="image/pdf",
                download_name="declaration.pdf",
                conditional=True,
            )
        )
        # perform_cleanup(uploaded_files=[zip_file, signature_file])
        return response
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
