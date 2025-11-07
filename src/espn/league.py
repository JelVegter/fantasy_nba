from espn_api.basketball import League

YEAR = 2026
MY_TEAM = 3
league_id = 1684422249
espn_s2 = "AEADt%2B18NBmKGmT4tPsCR%2FrxQ7QzEG2RxBqwZIshSyXyXQKHSvOmRIQM2r78DsAvn7UhkBnm4vNdef6L6smn5uiO10oAmdU8nCHc9BA5uGLrnFabaqF5u3xtMO1X72Xmg%2FmbPg56nGUKocJ4t5Eqklt6XiCXX7xPmETPR7slw6bbosyDbpX5I%2FizXItxAisG8aIaVqPSzoYGtStEeRt87sAlcY%2FjQPx17172G0vOE79UZvC8L9l8eLwcOEFfaDFQ02cBNbP0GBhD5J4V7IxMiooh91YjuNNYLDO20WoRV2VLSw%3D%3D"
swid = "{2488CBC0-AE37-40F0-B48B-08C06765AE78}"


league = League(
    league_id=league_id,
    year=YEAR,
    espn_s2=espn_s2,
    swid=swid,
    debug=False,
)
