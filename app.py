from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import io, zipfile, json

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    cert = Image.open(request.files['template'])
    data = pd.read_excel(request.files['excel'])
    coords = json.loads(request.form.get("coords"))  # {"name":[x,y]}

    font_file = request.files['font']
    font_size = int(request.form.get("font_size", 40))

    font_bytes = io.BytesIO(font_file.read())
    font = ImageFont.truetype(font_bytes, font_size)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for i, row in data.iterrows():
            img = cert.copy()
            draw = ImageDraw.Draw(img)

            text = str(row["Name"])
            x, y = coords["name"]

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            pos = (x - text_width // 2, y - text_height // 2)

            draw.text(pos, text, font=font, fill="black")

            out = io.BytesIO()
            img.save(out, format="PNG")
            zf.writestr(f"{row['Name']}.png", out.getvalue())

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype="application/zip",
                     as_attachment=True, download_name="certificates.zip")

if __name__ == "__main__":
    app.run(debug=True)
