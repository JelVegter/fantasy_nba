from espn_api.basketball import League

YEAR = 2025
MY_TEAM = 7
league_id = 1358670312
espn_s2 = "AECo9DbdLD7I5A3LiL2a3VmS%2FRgXNtPDknck2hC4Gnl1KNvN8y9moeB4LoYGq1FN26snqnNVYhWEjiarNVc5ZCTuy1s91cD7yI1iAGwlovqwRLzTpUT3vALBf%2F7YM%2BoEufGR0Xqh9h3GnZRvQr0ySu0bhLU5F95XWf7arBQKZBSlf3Ng0%2FH%2B7Y%2Bk6eFzL9D5fTpz8fw9stQ28FnLmJ%2FoPOu6pVSl96aQbpVFwkYiW3rsFaqXHnSZzk1GIjHgu4OGFuRhgplva1C4z7J6rKgL5oM80gDZXQjvNmVRXW3MaF7N0A%3D%3D"
swid = "{2488CBC0-AE37-40F0-B48B-08C06765AE78}"

league = League(
    league_id=league_id,
    year=YEAR,
    espn_s2=espn_s2,
    swid=swid,
    debug=False,
)
