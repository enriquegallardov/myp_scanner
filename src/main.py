from flask import Flask, flash, request, redirect, send_file
import os
from scanner import DocScanner
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_prefixed_env()
scanner = DocScanner(True)

os.makedirs(os.path.join(app.instance_path, "htmlfi"), exist_ok=True)

valid_formats = ["jpg", "jpeg", "jp2", "png", "bmp", "tiff", "tif"]
get_ext = lambda f: os.path.splitext(f)[1].lower()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in valid_formats


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(
                os.path.join(
                    app.instance_path, "htmlfi", secure_filename(file.filename)
                )
            )
            processed_filename = scanner.scan(
                os.path.join(app.instance_path, "htmlfi", filename)
            )
            os.remove(os.path.join(app.instance_path, "htmlfi", filename))
            return send_file(
                os.path.join(app.instance_path, "htmlfi", processed_filename),
                as_attachment=True,
            )
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8989)
