from flask import Flask, request, jsonify
from pdf2image import convert_from_bytes
from io import BytesIO
import os
from supabase import create_client, Client
from PIL import Image
import datetime

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = "documents"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/convert", methods=["POST"])
def convert_pdf():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files['file']
    pdf_bytes = file.read()

    try:
        images = convert_from_bytes(pdf_bytes, dpi=200)
    except Exception as e:
        return jsonify({"success": False, "error": f"Conversion failed: {str(e)}"}), 500

    urls = []
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    for idx, img in enumerate(images):
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f"converted/{timestamp}_page_{idx+1}.png"
        upload_response = supabase.storage.from_(SUPABASE_BUCKET).upload(filename, buffer, {
            "content-type": "image/png"
        })

        if upload_response.get("error"):
            return jsonify({"success": False, "error": upload_response["error"]["message"]}), 500

        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        urls.append(public_url["publicUrl"])

    return jsonify({"success": True, "pages": urls})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
