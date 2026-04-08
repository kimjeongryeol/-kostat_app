from flask import Flask, render_template, jsonify, request
import requests as req

app = Flask(__name__)

KOSTAT_BASE = "https://data.kostat.go.kr/nowcast"

ENDPOINTS = {
    "living_gender":   "/popul/living/get-gender.do",
    "living_age":      "/popul/living/get-age.do",
    "staying_resident":"/popul/staying/get-resident.do",
    "staying_gender":  "/popul/staying/get-gender.do",
    "staying_age":     "/popul/staying/get-age.do",
}

REFERERS = {
    "living_gender":    "/nowcast/popul_living_gender.do",
    "living_age":       "/nowcast/popul_living_age.do",
    "staying_resident": "/nowcast/popul_staying_resident.do",
    "staying_gender":   "/nowcast/popul_staying_gender.do",
    "staying_age":      "/nowcast/popul_staying_age.do",
}

AGENCYS = [
    "2611000000","2614000000","2617000000","2620000000","2641000000",
    "2717000000","2720000000","2730000000","2741000000","2745000000",
    "2748000000","2800000000","2900000000","3000000000","3600000000",
    "4400000000","4800000000","5000000000","5100000000","6300000000"
]

ITEMS_MAP = {
    "living_gender": [
        {"key":"004000","title":"계","col":"tot"},
        {"key":"004001","title":"남","col":"mal"},
        {"key":"004002","title":"여","col":"fem"}
    ],
    "living_age": [
        {"key":"005000","title":"계","col":"tot"},
        {"key":"005001","title":"20세미만","col":"age1"},
        {"key":"005002","title":"20대","col":"age2"},
        {"key":"005003","title":"30대","col":"age3"},
        {"key":"005004","title":"40대","col":"age4"},
        {"key":"005005","title":"50대","col":"age5"},
        {"key":"005006","title":"60세이상","col":"age6"}
    ],
    "staying_resident": [
        {"key":"006000","title":"계","col":"tot"},
        {"key":"006001","title":"내국인","col":"dom"},
        {"key":"006002","title":"외국인","col":"for_"}
    ],
    "staying_gender": [
        {"key":"004000","title":"계","col":"tot"},
        {"key":"004001","title":"남","col":"mal"},
        {"key":"004002","title":"여","col":"fem"}
    ],
    "staying_age": [
        {"key":"005000","title":"계","col":"tot"},
        {"key":"005001","title":"20세미만","col":"age1"},
        {"key":"005002","title":"20대","col":"age2"},
        {"key":"005003","title":"30대","col":"age3"},
        {"key":"005004","title":"40대","col":"age4"},
        {"key":"005005","title":"50대","col":"age5"},
        {"key":"005006","title":"60세이상","col":"age6"}
    ],
}

def get_session_cookie(referer_path):
    s = req.Session()
    s.get(
        KOSTAT_BASE + referer_path,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        timeout=10
    )
    return s

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/fetch", methods=["POST"])
def fetch_data():
    body = request.json
    dtype = body.get("type", "living_gender")
    periods = body.get("periods", ["202507","202508","202509"])

    if dtype not in ENDPOINTS:
        return jsonify({"error": "unknown type"}), 400

    referer_path = REFERERS[dtype]
    session = get_session_cookie(referer_path)

    payload = {
        "agencyCds": [], "agencys": AGENCYS, "areaTypes": [],
        "assayColData": "Y", "assayColRate": "Y",
        "assayPrevMonthYn": "N", "assayPrevYearYn": "N",
        "colAxis": [{"val":"T","text":"기준년월"},{"val":"I","text":"성별"}],
        "dataKindCd": "",
        "downExcelCellMerge": "Y", "downFileEncoding": "ANSI", "downFileType": "xlsx",
        "excelFields": [{"label":"시도명","field":"agencyNm"},{"label":"시군구명","field":"districtNm"}],
        "excelHeaders": [],
        "items": ITEMS_MAP[dtype],
        "nd": 1775438606174,
        "orderBys": ["A","P"], "page": 1,
        "pcols": [{"key":"002000","col":"pt","colnm":"생활인구:계"},{"key":"002001","col":"pn","colnm":"주민등록인구"}],
        "periods": periods,
        "rowAxis": [{"val":"A","text":"행정구역별"},{"val":"P","text":"생활인구"}],
        "rows": 9999999, "sidx": "", "sord": "asc", "sqlType": "IT", "stdYmSort": "asc",
        "_search": False
    }

    try:
        r = session.post(
            KOSTAT_BASE + ENDPOINTS[dtype],
            json=payload,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "Referer": KOSTAT_BASE + referer_path,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Origin": KOSTAT_BASE,
            },
            timeout=15
        )
        if not r.text:
            return jsonify({"error": "빈 응답 — 세션 만료 또는 파라미터 오류"}), 502
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("✅ http://127.0.0.1:5000 에서 실행 중")
    app.run(debug=True, port=5000)
