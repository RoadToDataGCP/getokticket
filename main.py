from flask import Flask, request, jsonify, send_file
from google.cloud import bigquery, storage
from dotenv import load_dotenv
from datetime import timedelta
import pandas as pd
import os
import uuid

load_dotenv()

app = Flask(__name__)

bq_client = bigquery.Client()
storage_client = storage.Client()

PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")
BUCKET_NAME = os.getenv("BUCKET_NAME")
TEMP_DIR = "/tmp"

@app.route("/export-csv", methods=["GET"])
def export_csv():
    user = request.args.get("user")
    password = request.args.get("pass")
    if user != API_USER or password != API_PASS:
        return jsonify({"error": "Acceso no autorizado"}), 401

    table_name = request.args.get("table")
    if not table_name:
        return jsonify({"error": "Falta el parámetro 'table'"}), 400

    try:
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        query = f"SELECT * FROM `{full_table_id}`"
        query_job = bq_client.query(query)
        df = query_job.to_dataframe()

        file_id = f"{table_name}.csv"
        local_path = os.path.join(TEMP_DIR, file_id)
        df.to_csv(local_path, index=False, date_format="%Y-%m-%d %H:%M:%S", na_rep="")

        # Subir CSV a Cloud Storage
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"temp_exports/{file_id}")
        blob.upload_from_filename(local_path)

        # Generar URL firmada que apunta a nuestro propio endpoint de descarga
        signed_url = f"/download-csv?id={file_id}&user={user}&pass={password}"

        data_json = df.to_dict(orient="records")

        return jsonify({
            "table": table_name,
            "rows": len(df),
            "data": data_json,
            "csv_url": signed_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download-csv", methods=["GET"])
def download_csv():
    file_id = request.args.get("id")
    user = request.args.get("user")
    password = request.args.get("pass")

    if user != API_USER or password != API_PASS:
        return jsonify({"error": "Acceso no autorizado"}), 401

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"temp_exports/{file_id}")
        local_path = os.path.join(TEMP_DIR, file_id)
        blob.download_to_filename(local_path)

        # Eliminar el archivo del bucket tras la descarga
        blob.delete()

        return send_file(
            local_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name=file_id
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
