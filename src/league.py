import logging
from espn_api.basketball import League

YEAR = 2023
MY_TEAM = 2
league_id = 1347896761
espn_s2 = "AEBfmOxy44LMCaoFmYfagWtfAX1o%2BStwkkyCtg83ZU7FIkRUElrNOfiHjT%2FawacBBcaWSBSiCBPOwcPX0vbDlxQinBysBlugQaJUeQh%2F3PvvWeCzQw9s%2F9IP%2BNEXoac0qMAsA3m01dIDV2BpoActcvNrHjTthz%2F1imlkuDgPLDusADd7%2FeNCb8V%2F0I4MesGg3C9%2FHukKcXuYAewNh6TlvYAu9nGSvpkgn3JCsz0XPstBUQEXIt8OiVNB9dd6WiZdHiBAhOmV9aALe0Sf2Sx6sCcjeZMV%2BrickXtIhNblUoPgyw%3D%3D"
swid = "{2488CBC0-AE37-40F0-B48B-08C06765AE78}"

league = League(
    league_id=league_id,
    year=YEAR,
    espn_s2=espn_s2,
    swid=swid,
)


def refresh_league():
    return League(
        league_id=league_id,
        year=YEAR,
        espn_s2=espn_s2,
        swid=swid,
    )


FANTASY_TEAMS = sorted([t.team_name for t in league.teams])


def fetch_fantasy_team_current_fantasy_points() -> dict[str, int]:
    fantasy_team_points = {}
    for team in league.teams:
        fantasy_team_points[team] = stats_points_conversion(team.stats)
    return fantasy_team_points


def stats_points_conversion(stats: dict[str, float]) -> int:
    fantasy_points = 0
    points_per_stat = {
        "PTS": 1,
        "FTA": -1,
        "BLK": 4,
        "3PTM": 1,
        "STL": 4,
        "AST": 2,
        "REB": 1,
        "TO": -2,
        "FGM": 2,
        "FGA": -1,
        "FTM": 1,
    }

    for stat in stats.keys():
        fantasy_points += points_per_stat[stat] * stats[stat]
    return int(fantasy_points)


FANTASY_TEAMS_CURRENT_POINTS: dict = fetch_fantasy_team_current_fantasy_points()
