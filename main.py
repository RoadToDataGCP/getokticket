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

@app.route("/export-csv", methods=["GET"])
def export_csv():
    table_name = request.args.get("table")
    if not table_name:
        return jsonify({"error": "Falta el parámetro 'table'"}), 400

    try:
        # Construir el ID completo de la tabla: proyecto.dataset.tabla
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

        # Ejecutar la consulta
        query = f"SELECT * FROM `{full_table_id}`"
        query_job = bq_client.query(query)
        df = query_job.to_dataframe()

        # Guardar CSV temporal
        temp_filename = f"/tmp/{uuid.uuid4().hex}.csv"
        df.to_csv(temp_filename, index=False)

        return send_file(
            temp_filename,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{table_name}.csv"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
