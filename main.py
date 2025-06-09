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
def export_csv():
    table_name = request.args.get("table")
    if not table_name:
        return jsonify({"error": "Falta el parámetro 'table'"}), 400

    try:
        # Construir el ID completo de la tabla
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Ejecutar la consulta
        query = f"SELECT * FROM `{full_table_id}`"
        query_job = bq_client.query(query)
        df = query_job.to_dataframe()

        # Generar archivo CSV temporal
        file_id = f"{uuid.uuid4().hex}.csv"
        temp_path = os.path.join(TEMP_DIR, file_id)
        df.to_csv(temp_path, index=False)

        # Convertir DataFrame a lista de diccionarios para JSON
        data_json = df.to_dict(orient="records")

        # Devolver JSON con datos y enlace de descarga
        return jsonify({
            "table": table_name,
            "rows": len(df),
            "data": data_json,
            "csv_url": f"/download-csv?id={file_id}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download-csv", methods=["GET"])
def download_csv():
    file_id = request.args.get("id")
    if not file_id:
        return jsonify({"error": "Falta el parámetro 'id'"}), 400

    file_path = os.path.join(TEMP_DIR, file_id)
    if not os.path.exists(file_path):
        return jsonify({"error": "Archivo no encontrado"}), 404

    return send_file(
        file_path,
        mimetype='text/csv',
        as_attachment=True,
        download_name=file_id
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
