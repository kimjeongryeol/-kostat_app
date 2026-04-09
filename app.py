from flask import Flask, render_template, jsonify, request
import requests as req

app = Flask(__name__)

KOSTAT_BASE = "https://data.kostat.go.kr/nowcast"

ENDPOINTS = {
    "living_gender":    "/popul/living/get-gender.do",
    "living_age":       "/popul/living/get-age.do",
    "staying_resident": "/popul/staying/get-resident.do",
    "staying_gender":   "/popul/staying/get-gender.do",
    "staying_age":      "/popul/staying/get-age.do",
}

REFERERS = {
    "living_gender":    "/nowcast/popul_living_gender.do",
    "living_age":       "/nowcast/popul_living_age.do",
    "staying_resident": "/nowcast/popul_staying_resident.do",
    "staying_gender":   "/nowcast/popul_staying_gender.do",
    "staying_age":      "/nowcast/popul_staying_age.do",
}

AGENCYS = [
    "1100000000",
    "2611000000","2614000000","2617000000","2620000000","2641000000",
    "2717000000","2720000000","2730000000","2741000000","2745000000",
    "2748000000","2814000000",
    "2800000000","2810000000","2820000000","2830000000","2840000000",
    "2850000000","2860000000","2870000000","2880000000",
    "2900000000","2911000000","2914000000","2917000000","2920000000","2923000000",
    "3000000000","3011000000","3014000000","3017000000","3020000000","3023000000",
    "3100000000","3111000000","3114000000","3117000000","3120000000","3171000000",
    "3600000000",
    "4100000000","4111000000","4113000000","4115000000","4117000000","4119000000",
    "4121000000","4122000000","4125000000","4127000000","4128000000","4129000000",
    "4131000000","4136000000","4137000000","4139000000","4141000000","4143000000",
    "4145000000","4146000000","4148000000","4150000000","4155000000","4157000000",
    "4159000000","4161000000","4163000000","4165000000","4167000000","4169000000",
    "4171000000","4173000000","4175000000","4177000000","4179000000","4180000000",
    "4182000000","4183000000","4184000000","4186000000","4194000000","4195000000",
    "4196000000","4197000000","4199000000",
    "4200000000","4211000000","4213000000","4215000000","4217000000","4219000000",
    "4221000000","4223000000","4225000000","4271000000","4272000000","4273000000",
    "4274000000","4275000000","4276000000","4277000000","4278000000",
    "4300000000","4311000000","4313000000","4315000000","4317000000","4372000000",
    "4373000000","4374000000","4375000000","4376000000",
    "4400000000","4411000000","4413000000","4415000000","4417000000","4419000000",
    "4421000000","4423000000","4471000000","4472000000","4473000000","4474000000",
    "4475000000","4476000000","4477000000",
    "4500000000","4511000000","4513000000","4514000000","4515000000","4517000000",
    "4519000000","4521000000","4523000000","4571000000","4572000000","4573000000",
    "4574000000","4575000000",
    "4600000000","4611000000","4613000000","4615000000","4617000000","4619000000",
    "4621000000","4623000000","4671000000","4672000000","4673000000","4674000000",
    "4675000000","4676000000","4677000000","4678000000","4679000000","4680000000",
    "4681000000","4682000000","4683000000","4684000000","4685000000",
    "4700000000","4711000000","4713000000","4715000000","4717000000","4719000000",
    "4721000000","4723000000","4725000000","4728000000","4729000000","4771000000",
    "4772000000","4773000000","4774000000","4775000000","4776000000","4777000000",
    "4778000000","4779000000","4780000000","4781000000","4782000000","4783000000",
    "4800000000","4812000000","4817000000","4822000000","4824000000","4825000000",
    "4827000000","4831000000","4833000000","4872000000","4873000000","4874000000",
    "4875000000","4876000000","4877000000","4878000000","4879000000","4880000000",
    "4881000000","4882000000","4883000000",
    "5000000000","5011000000","5013000000",
]

ITEMS_MAP = {
    "living_gender": [
        {"key": "004000", "title": "계", "col": "agett"},
        {"key": "004001", "title": "남", "col": "age19"},
        {"key": "004002", "title": "여", "col": "age20"},
    ],
    "living_age": [
        {"key": "003000", "title": "연령:계",   "col": "agett"},
        {"key": "003001", "title": "20세 미만", "col": "age19"},
        {"key": "003002", "title": "20대",      "col": "age20"},
        {"key": "003003", "title": "30대",      "col": "age30"},
        {"key": "003004", "title": "40대",      "col": "age40"},
        {"key": "003005", "title": "50대",      "col": "age50"},
        {"key": "003006", "title": "60세 이상", "col": "age60"},
    ],
    "staying_resident": [
        {"key": "006000", "title": "계",     "col": "agett"},
        {"key": "006001", "title": "내국인", "col": "dom"},
        {"key": "006002", "title": "외국인", "col": "for_"},
    ],
    "staying_gender": [
        {"key": "004000", "title": "계", "col": "agett"},
        {"key": "004001", "title": "남", "col": "age19"},
        {"key": "004002", "title": "여", "col": "age20"},
    ],
    "staying_age": [
        {"key": "003000", "title": "연령:계",   "col": "agett"},
        {"key": "003001", "title": "20세 미만", "col": "age19"},
        {"key": "003002", "title": "20대",      "col": "age20"},
        {"key": "003003", "title": "30대",      "col": "age30"},
        {"key": "003004", "title": "40대",      "col": "age40"},
        {"key": "003005", "title": "50대",      "col": "age50"},
        {"key": "003006", "title": "60세 이상", "col": "age60"},
    ],
}

COL_AXIS_MAP = {
    "living_gender":    [{"val": "T", "text": "기준년월"}, {"val": "I", "text": "성별"}],
    "living_age":       [{"val": "T", "text": "기준년월"}, {"val": "I", "text": "연령"}],
    "staying_resident": [{"val": "T", "text": "기준년월"}, {"val": "I", "text": "내외국인"}],
    "staying_gender":   [{"val": "T", "text": "기준년월"}, {"val": "I", "text": "성별"}],
    "staying_age":      [{"val": "T", "text": "기준년월"}, {"val": "I", "text": "연령"}],
}

PCOLS_COMMON = [
    {"key": "002000", "col": "pt", "colnm": "생활인구:계"},
    {"key": "002001", "col": "pn", "colnm": "주민등록인구"},
    {"key": "002002", "col": "ps", "colnm": "체류인구"},
    {"key": "002003", "col": "pf", "colnm": "외국인"},
]

ROW_AXIS_COMMON = [
    {"val": "A", "text": "행정구역별"},
    {"val": "P", "text": "생활인구"},
]


def get_session_cookie(referer_path):
    s = req.Session()
    s.get(
        KOSTAT_BASE + referer_path,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        timeout=10,
    )
    return s


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/fetch", methods=["POST"])
def fetch_data():
    body    = request.json
    dtype   = body.get("type", "living_gender")
    periods = body.get("periods", ["202507", "202508", "202509"])

    if dtype not in ENDPOINTS:
        return jsonify({"error": "unknown type"}), 400

    referer_path = REFERERS[dtype]
    session      = get_session_cookie(referer_path)

    payload = {
        "agencyCds":          [],
        "agencys":            AGENCYS,
        "areaTypes":          [],
        "assayColData":       "Y",
        "assayColRate":       "Y",
        "assayPrevMonthYn":   "N",
        "assayPrevYearYn":    "N",
        "colAxis":            COL_AXIS_MAP[dtype],
        "dataKindCd":         "",
        "downExcelCellMerge": "Y",
        "downFileEncoding":   "ANSI",
        "downFileType":       "xlsx",
        "excelFields": [
            {"label": "시도명",   "field": "agencyNm"},
            {"label": "시군구명", "field": "districtNm"},
        ],
        "excelHeaders":       [],
        "items":              ITEMS_MAP[dtype],
        "nd":                 1775695750977,
        "orderBys":           ["A", "P"],
        "page":               1,
        "pcols":              PCOLS_COMMON,
        "periods":            periods,
        "rowAxis":            ROW_AXIS_COMMON,
        "rows":               9999999,
        "sidx":               "",
        "sord":               "asc",
        "sqlType":            "IT",
        "stdYmSort":          "asc",
        "_search":            False,
    }

    try:
        r = session.post(
            KOSTAT_BASE + ENDPOINTS[dtype],
            json=payload,
            headers={
                "Content-Type":     "application/json;charset=UTF-8",
                "Referer":          KOSTAT_BASE + referer_path,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept":           "application/json, text/javascript, */*; q=0.01",
                "Origin":           KOSTAT_BASE,
            },
            timeout=30,
        )

        if not r.text:
            return jsonify({"error": "빈 응답 — 세션 만료 또는 파라미터 오류"}), 502

        data = r.json()

        # ─── 디버그: 실제 응답 구조 터미널에 출력 ───────────────────────────
        print("\n" + "="*60)
        print(f"[DEBUG] dtype={dtype}, periods={periods}")
        print(f"[DEBUG] 응답 타입: {type(data)}")

        if isinstance(data, dict):
            print(f"[DEBUG] 최상위 키: {list(data.keys())}")
            # rows 키가 있으면 그 안을 확인
            rows = data.get("rows", data.get("data", data.get("list", None)))
            if rows and isinstance(rows, list) and len(rows) > 0:
                print(f"[DEBUG] rows 개수: {len(rows)}")
                print(f"[DEBUG] 첫번째 row 키: {list(rows[0].keys())}")
                print(f"[DEBUG] 첫번째 row 샘플:\n{rows[0]}")
            else:
                print(f"[DEBUG] dict 전체 내용(앞 500자): {str(data)[:500]}")

        elif isinstance(data, list):
            print(f"[DEBUG] 리스트 길이: {len(data)}")
            if len(data) > 0:
                print(f"[DEBUG] 첫번째 row 키: {list(data[0].keys())}")
                print(f"[DEBUG] 첫번째 row 샘플:\n{data[0]}")
        print("="*60 + "\n")
        # ────────────────────────────────────────────────────────────────────

        # rows 추출 후 반환
        if isinstance(data, dict):
            rows = data.get("rows", data.get("data", data.get("list", None)))
            if rows is not None:
                return jsonify(rows)

        return jsonify(data)

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("✅ http://127.0.0.1:5000 에서 실행 중")
    app.run(debug=True, port=5000)