from flask import Flask, jsonify, request
from clients.mongo_client import mongo_client
from clients.neo4j_client import neo4j_client
from neo4j.graph import Node, Relationship

# -------------------------------------------------
# KHỞI TẠO APP FLASK
# -------------------------------------------------
app = Flask(__name__)


# -------------------------------------------------
# ROUTES CƠ BẢN
# -------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Trang kiểm tra nhanh xem API có chạy không."""
    return jsonify({"message": "API Neo4j + MongoDB đang chạy trên Render"})


@app.route("/health", methods=["GET"])
def health():
    """
    Kiểm tra tình trạng kết nối MongoDB & Neo4j.
    """
    status = {}

    # ----- Check MongoDB -----
    try:
        collections = mongo_client.db.list_collection_names()
        status["mongo"] = {"ok": True, "collections": collections}
    except Exception as e:
        status["mongo"] = {"ok": False, "error": str(e)}

    # ----- Check Neo4j -----
    try:
        result = neo4j_client.run_query("RETURN 1 AS ok")
        rows = [dict(r) for r in result]
        status["neo4j"] = {"ok": True, "result": rows}
    except Exception as e:
        status["neo4j"] = {"ok": False, "error": str(e)}

    overall_ok = status.get("mongo", {}).get("ok") and status.get("neo4j", {}).get("ok")
    return jsonify({"ok": overall_ok, "details": status})


# -------------------------------------------------
# NEO4J TEST ĐƠN GIẢN
# -------------------------------------------------
@app.route("/neo4j/test", methods=["GET"])
def neo4j_test():
    """
    Test đơn giản kết nối Neo4j.
    Mở trên browser: /neo4j/test
    """
    try:
        result = neo4j_client.run_query("RETURN 1 AS ok")
        rows = [dict(r) for r in result]
        return jsonify({"ok": True, "data": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# Alias riêng cho Neo4j health (nếu cần dùng /neo4j/health)
@app.route("/neo4j/health", methods=["GET"])
def neo4j_health():
    return neo4j_test()


# -------------------------------------------------
# API MONGO: LẤY DỮ LIỆU SẢN PHẨM
# -------------------------------------------------
@app.route("/mongo/products", methods=["GET"])
def get_mongo_products():
    """
    Ví dụ: GET /mongo/products?limit=10&collection=products
    Lấy dữ liệu từ collection MongoDB (mặc định: 'products').
    """
    limit = int(request.args.get("limit", 10))
    collection_name = request.args.get("collection", "products")

    try:
        col = mongo_client.get_collection(collection_name)
        cursor = col.find({}, {"_id": 0}).limit(limit)
        data = list(cursor)
        return jsonify({"ok": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# 👉 ALIAS CHO /products
@app.route("/products", methods=["GET"])
def get_products_alias():
    return get_mongo_products()


# -------------------------------------------------
# API NEO4J: LẤY NODES DEMO (ĐÃ FIX LỖI dict.id)
# -------------------------------------------------
@app.route("/neo4j/nodes", methods=["GET"])
def get_nodes():
    """
    Demo: MATCH (n) RETURN n LIMIT {limit}
    Trả về dạng JSON an toàn cho cả Node object và dict (Aura Free).
    """
    limit = int(request.args.get("limit", 20))

    try:
        cypher = "MATCH (n) RETURN n LIMIT $limit"
        result = neo4j_client.run_query(cypher, {"limit": limit})

        data = []
        for row in result:
            n = row["n"]

            # Trường hợp Aura Free trả về dict
            if isinstance(n, dict):
                data.append({
                    "labels": n.get("labels", []),
                    "properties": n
                })
            # Trường hợp chạy Neo4j Desktop / Aura trả về Node object
            elif isinstance(n, Node):
                data.append({
                    "id": n.id,
                    "labels": list(n.labels),
                    "properties": dict(n)
                })
            else:
                # fallback: trả nguyên giá trị
                data.append({"value": str(n)})

        return jsonify({"ok": True, "count": len(data), "data": data})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# -------------------------------------------------
# API NEO4J TỔNG QUÁT: CHẠY CYPHER BẤT KỲ
# -------------------------------------------------
@app.route("/neo4j/query", methods=["POST"])
def run_neo4j_query():
    """
    Body JSON:
    {
      "query": "MATCH (n:Fruit) RETURN n LIMIT 5",
      "params": { "name": "Bưởi Da Xanh" }   # không bắt buộc
    }
    """
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query")
    params = data.get("params") or {}

    if not query:
        return jsonify({"ok": False, "error": "Thiếu 'query' trong body"}), 400

    try:
        result = neo4j_client.run_query(query, params)

        def convert_value(v):
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
            # Nếu là dict (Aura Free) thì trả nguyên
            if isinstance(v, dict):
                return v
            return v

        rows = []
        for r in result:
            row = {k: convert_value(v) for k, v in r.items()}
            rows.append(row)

        return jsonify({"ok": True, "count": len(rows), "data": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# -------------------------------------------------
# MAIN (CHỈ DÙNG KHI CHẠY LOCAL)
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
