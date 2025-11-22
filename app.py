from flask import Flask, jsonify, request
from flask_cors import CORS
from clients.mongo_client import mongo_client
from clients.neo4j_client import neo4j_client
from neo4j.graph import Node, Relationship

# -------------------------------------------------
# KHỞI TẠO APP FLASK
# -------------------------------------------------
app = Flask(__name__)
CORS(app)     # Cho phép API được gọi từ chatbot bên ngoài


# -------------------------------------------------
# ROUTE KIỂM TRA
# -------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Trang kiểm tra nhanh"""
    return jsonify({"message": "API Neo4j + MongoDB đang chạy trên Render"})


# -------------------------------------------------
# /health – KIỂM TRA KẾT NỐI HAI HỆ
# -------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    status = {}

    # Check MongoDB
    try:
        collections = mongo_client.db.list_collection_names()
        status["mongo"] = {"ok": True, "collections": collections}
    except Exception as e:
        status["mongo"] = {"ok": False, "error": str(e)}

    # Check Neo4j
    try:
        result = neo4j_client.run_query("RETURN 1 AS ok")
        status["neo4j"] = {"ok": True, "result": result}
    except Exception as e:
        status["neo4j"] = {"ok": False, "error": str(e)}

    return jsonify({
        "ok": status["mongo"]["ok"] and status["neo4j"]["ok"],
        "details": status
    })


# -------------------------------------------------
# NEO4J TEST
# -------------------------------------------------
@app.route("/neo4j/test", methods=["GET"])
def neo4j_test():
    try:
        result = neo4j_client.run_query("RETURN 1 AS ok")
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/neo4j/health", methods=["GET"])
def neo4j_health():
    return neo4j_test()


# -------------------------------------------------
# API MONGO: LẤY DỮ LIỆU
# -------------------------------------------------
@app.route("/mongo/products", methods=["GET"])
def get_mongo_products():
    limit = int(request.args.get("limit", 10))
    collection_name = request.args.get("collection", "products")

    try:
        col = mongo_client.get_collection(collection_name)
        cursor = col.find({}, {"_id": 0}).limit(limit)
        data = list(cursor)
        return jsonify({"ok": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/products", methods=["GET"])
def get_products_alias():
    return get_mongo_products()


# -------------------------------------------------
# API NEO4J: LẤY NODE (CHUẨN HÓA JSON)
# -------------------------------------------------
def normalize_node(n):
    """Chuẩn hóa dữ liệu node từ Aura Free hoặc Node object"""
    if isinstance(n, Node):
        return {
            "id": n.id,
            "labels": list(n.labels),
            "properties": dict(n)
        }
    if isinstance(n, dict):   # Aura free
        labels = n.get("labels", [])
        props = {k: v for k, v in n.items() if k != "labels"}
        return {
            "id": props.get("id"),
            "labels": labels,
            "properties": props
        }
    return {"value": str(n)}


@app.route("/neo4j/nodes", methods=["GET"])
def get_nodes():
    limit = int(request.args.get("limit", 20))

    try:
        cypher = "MATCH (n) RETURN n LIMIT $limit"
        result = neo4j_client.run_query(cypher, {"limit": limit})

        data = [normalize_node(row["n"]) for row in result]

        return jsonify({"ok": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# -------------------------------------------------
# API NEO4J: CHẠY CYPHER
# -------------------------------------------------
def convert_value(v):
    """Chuẩn hóa giá trị trả về từ Neo4j"""
    if isinstance(v, Node):
        return {
            "id": v.id,
            "labels": list(v.labels),
            "properties": dict(v),
        }
    if isinstance(v, Relationship):
        return {
            "id": v.id,
            "type": v.type,
            "start_node_id": v.start_node.id,
            "end_node_id": v.end_node.id,
            "properties": dict(v),
        }
    if isinstance(v, dict):
        return v
    return v


@app.route("/neo4j/query", methods=["POST"])
def run_neo4j_query():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query")
    params = data.get("params") or {}

    if not query:
        return jsonify({"ok": False, "error": "Thiếu 'query' trong body"}), 400

    try:
        result = neo4j_client.run_query(query, params)
        rows = [{k: convert_value(v) for k, v in r.items()} for r in result]

        return jsonify({"ok": True, "count": len(rows), "data": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# -------------------------------------------------
# MAIN – CHẠY LOCAL
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
