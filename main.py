from flask import Flask, request, send_file, jsonify
from google.cloud import bigquery
from dotenv import load_dotenv
import pandas as pd
import os
import uuid

# Cargar variables de entorno si estás en desarrollo
load_dotenv()

app = Flask(__name__)
bq_client = bigquery.Client()

# Proyecto y dataset fijos definidos por entorno
PROJECT_ID = os.getenv("PROJECT_ID")
DATASET_ID = os.getenv("DATASET_ID")
TEMP_DIR = "/tmp"

@app.route("/export-csv", methods=["GET"])
@app.route("/export-csv", methods=["GET"])
def export_csv():
    # Validar usuario y contraseña desde query params
    user = request.args.get("user")
    password = request.args.get("pass")

    if user != os.getenv("r2d") or password != os.getenv("12345"):
        return jsonify({"error": "Acceso no autorizado"}), 401

    table_name = request.args.get("table")
    if not table_name:
        return jsonify({"error": "Falta el parámetro 'table'"}), 400

    try:
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        query = f"SELECT * FROM `{full_table_id}`"
        query_job = bq_client.query(query)
        df = query_job.to_dataframe()

        file_id = f"{uuid.uuid4().hex}.csv"
        temp_path = os.path.join(TEMP_DIR, file_id)
        df.to_csv(temp_path, index=False, date_format="%Y-%m-%d %H:%M:%S", na_rep="")

        data_json = df.to_dict(orient="records")

        return jsonify({
            "table": table_name,
            "rows": len(df),
            "data": data_json,
            "csv_url": f"/download-csv?id={file_id}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
