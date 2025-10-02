import json
from urllib.parse import parse_qs

# --- Sample data (can be swapped for DynamoDB later) ---
SAMPLE = {
  "city_to_zips": {
    "raleigh, nc": ["27603", "27610", "27612"],
    "durham, nc": ["27703", "27713", "27707"],
    "elizabeth city, nc": ["27909", "27921", "27917"],
    "goldsboro, nc": ["27534", "27530", "27531"],
    "portland, or": ["97202", "97206", "97229"]
  },
  "zip_neighbors": {
    "27612": ["27613", "27609"],
    "27610": ["27603", "27604"],
    "27603": ["27610", "27529"],
    "27703": ["27713", "27560"],
    "97202": ["97206", "97214"],
    "27534": ["27530", "27531"],
    "27909": ["27921", "27917"]
  },
  "market": {
    "27612": {"city":"Raleigh", "state":"NC", "county":"Wake County", "score":71, "class":"WARM", "dom":41, "mos":2.4, "slr":98.7, "reductions":23,
              "trends":["Inventory loosening slightly","Buyers negotiating harder","Higher price points slowing"],
              "insights":["Target expireds & high-equity owners","Flip smaller homes/townhomes for faster turns"],
              "evidence":["DOM > 40","Reductions up","Supply trending up"]},
    "27603": {"city":"Raleigh", "state":"NC", "county":"Wake County", "score":82, "class":"HOT", "dom":27, "mos":1.7, "slr":100.3, "reductions":14,
              "trends":["Core buyer demand strong","Under-30 DOM common","Tight sub-400k supply"],
              "insights":["Fast flips w/ cosmetic rehabs","Wholesale entry-level SFRs"],
              "evidence":["DOM < 30","Sale/List > 100%","Low MoS"]},
    "27610": {"city":"Raleigh", "state":"NC", "county":"Wake County", "score":74, "class":"WARM", "dom":33, "mos":2.0, "slr":99.1, "reductions":19,
              "trends":["Mixed comps by micro-hood","Slight uptick in inventory","Investors active but selective"],
              "insights":["Novations & wholetails near retail-ready","Assign lower ARV pockets"],
              "evidence":["DOM ~ 30","Moderate reductions","MoS ~ 2.0"]},
    "27703": {"city":"Durham", "state":"NC", "county":"Durham County", "score":76, "class":"WARM", "dom":32, "mos":1.9, "slr":100.1, "reductions":18,
              "trends":["Near RTP demand steady","Townhomes move quickly","Affordability pockets remain"],
              "insights":["Focus 3/2 ranches near 70/540","Wholesale townhomes to FHA buyers"],
              "evidence":["Sale/List ≈ 100%","MoS < 2.0","DOM low 30s"]},
    "97202": {"city":"Portland", "state":"OR", "county":"Multnomah County", "score":69, "class":"WARM", "dom":43, "mos":2.6, "slr":98.1, "reductions":25,
              "trends":["High rates cooling move-up buyers","More price improvements","Segmented by school clusters"],
              "insights":["Focus cosmetic rehabs under 500k","Wholesale craftsman fixers"],
              "evidence":["DOM > 40","Reductions 25%","MoS > 2.5"]},
    "27909": {"city":"Elizabeth City", "state":"NC", "county":"Pasquotank County", "score":64, "class":"COOL", "dom":52, "mos":3.1, "slr":97.4, "reductions":28,
              "trends":["Longer marketing times","Investor demand patchy","More concessions"],
              "insights":["Creative finance / sub-to","Deeper discounts for flips"],
              "evidence":["DOM > 50","MoS > 3","Reductions near 30%"]},
    "27534": {"city":"Goldsboro", "state":"NC", "county":"Wayne County", "score":66, "class":"COOL", "dom":48, "mos":2.8, "slr":97.9, "reductions":26,
              "trends":["Military turnover influences DOM","Affordability remains key","Builders cautious"],
              "insights":["Assignments near bases","Entry-level wholetails"],
              "evidence":["DOM ~ 50","MoS ~ 2.8","SLR < 98%"]}
  }
}

def _response(body: dict, status=200):
  # IMPORTANT: include CORS header for GitHub Pages
  return {
    "statusCode": status,
    "headers": {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "https://jb24000.github.io",
      "Access-Control-Allow-Methods": "GET,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type,Authorization",
    },
    "body": json.dumps(body)
  }

def route_city_zips(event):
  params = event.get("rawQueryString") or ""
  qs = parse_qs(params)
  city_state = (qs.get("city_state", [""])[0] or "").strip().lower()
  if not city_state:
    return _response({"error":"city_state required"}, 400)
  zips = SAMPLE["city_to_zips"].get(city_state)
  if not zips:
    return _response({"zips": []}, 200)
  return _response({"zips": zips})

def route_zip_neighbors(event):
  params = event.get("rawQueryString") or ""
  qs = parse_qs(params)
  zipc = (qs.get("zip", [""])[0] or "").strip()
  if not zipc:
    return _response({"error":"zip required"}, 400)
  n = SAMPLE["zip_neighbors"].get(zipc, [])
  return _response({"neighbors": n})

def route_market(event):
  params = event.get("rawQueryString") or ""
  qs = parse_qs(params)
  zipc = (qs.get("zip", [""])[0] or "").strip()
  if not zipc:
    return _response({"error":"zip required"}, 400)
  m = SAMPLE["market"].get(zipc)
  if not m:
    return _response({"error":"zip not found"}, 404)
  return _response(m)

def lambda_handler(event, context):
  # HTTP API v2 event
  path = (event.get("rawPath") or "").lower()
  method = (event.get("requestContext", {}).get("http", {}).get("method") or "GET").upper()

  if method == "OPTIONS":
    # Preflight
    return _response({"ok":True})

  if path.endswith("/city-zips"):
    return route_city_zips(event)
  if path.endswith("/zip-neighbors"):
    return route_zip_neighbors(event)
  if path.endswith("/market"):
    return route_market(event)

  return _response({"error":"not found","path":path}, 404)
