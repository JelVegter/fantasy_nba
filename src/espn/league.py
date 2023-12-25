from espn_api.basketball import League

YEAR = 2024
MY_TEAM = 2
league_id = 588888786
espn_s2 = "AEBfmOxy44LMCaoFmYfagWtfAX1o%2BStwkkyCtg83ZU7FIkRUElrNOfiHjT%2FawacBBcaWSBSiCBPOwcPX0vbDlxQinBysBlugQaJUeQh%2F3PvvWeCzQw9s%2F9IP%2BNEXoac0qMAsA3m01dIDV2BpoActcvNrHjTthz%2F1imlkuDgPLDusADd7%2FeNCb8V%2F0I4MesGg3C9%2FHukKcXuYAewNh6TlvYAu9nGSvpkgn3JCsz0XPstBUQEXIt8OiVNB9dd6WiZdHiBAhOmV9aALe0Sf2Sx6sCcjeZMV%2BrickXtIhNblUoPgyw%3D%3D"  # noqa: E501
swid = "{2488CBC0-AE37-40F0-B48B-08C06765AE78}"
# league_id = 1347896761
# espn_s2 = "AEBfmOxy44LMCaoFmYfagWtfAX1o%2BStwkkyCtg83ZU7FIkRUElrNOfiHjT%2FawacBBcaWSBSiCBPOwcPX0vbDlxQinBysBlugQaJUeQh%2F3PvvWeCzQw9s%2F9IP%2BNEXoac0qMAsA3m01dIDV2BpoActcvNrHjTthz%2F1imlkuDgPLDusADd7%2FeNCb8V%2F0I4MesGg3C9%2FHukKcXuYAewNh6TlvYAu9nGSvpkgn3JCsz0XPstBUQEXIt8OiVNB9dd6WiZdHiBAhOmV9aALe0Sf2Sx6sCcjeZMV%2BrickXtIhNblUoPgyw%3D%3D"  # noqa: E501
# swid = "{2488CBC0-AE37-40F0-B48B-08C06765AE78}"

league = League(
    league_id=league_id,
    year=YEAR,
    espn_s2=espn_s2,
    swid=swid,
)
