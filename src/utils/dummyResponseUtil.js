const DUMMY_SUMMONER = {
    "id": "acu3F1E7p-t0JpIHbq2KXgpALV6TJW-FqEKGp3A2UHBuTwQ",
    "accountId": "nmFO671RROMhZgcAmhGuIl13XuQE0uADeDGJ6dpFL1Ia9tc",
    "puuid": "UyPV3Ji6PUh-Z4iiS4247S_P4eEjtbUbQcT6F3ZO45SQGGaLKeVDwC0I578Jpo7aMyBWohImxFhGnw",
    "name": "TsimpleT",
    "profileIconId": 3463,
    "revisionDate": 1625730827000,
    "summonerLevel": 346
};

const DUMMY_RANKS = {
    solo: {
        "leagueId": "2645ae2e-24f6-4f02-8c5b-800843add1ac",
        "queueType": "RANKED_SOLO_5x5",
        "tier": "PLATINUM",
        "rank": "IV",
        "summonerId": "acu3F1E7p-t0JpIHbq2KXgpALV6TJW-FqEKGp3A2UHBuTwQ",
        "summonerName": "TsimpleT",
        "leaguePoints": 16,
        "wins": 70,
        "losses": 73,
        "veteran": false,
        "inactive": false,
        "freshBlood": false,
        "hotStreak": false
    },
    flex: {
        "leagueId": "1145d7e6-ac29-4ed8-a02a-2baaea08a2b7",
        "queueType": "RANKED_FLEX_SR",
        "tier": "GOLD",
        "rank": "III",
        "summonerId": "acu3F1E7p-t0JpIHbq2KXgpALV6TJW-FqEKGp3A2UHBuTwQ",
        "summonerName": "TsimpleT",
        "leaguePoints": 21,
        "wins": 53,
        "losses": 61,
        "veteran": false,
        "inactive": false,
        "freshBlood": false,
        "hotStreak": false
    }
};

const DUMMY_LIVE_GAME = {
    gameId: 4010571128,
    mapId: 11,
    gameMode: "CLASSIC",
    gameType: "MATCHED_GAME",
    gameQueueConfigId: 420,
    participants: [
        {
            "teamId": 100,
            "spell1Id": 12,
            "spell2Id": 4,
            "championId": 147,
            "profileIconId": 4068,
            "summonerName": "SpikyBuffalo",
            "bot": false,
            "summonerId": "g0H8zO8xkg1uENQRDJjB05t-F3cWnLcI4FtajwTRfjkHGx0",
            "gameCustomizationObjects": [],
            "perks": { // runes
                "perkIds": [
                    8229,
                    8226,
                    8210,
                    8236,
                    8304,
                    8321,
                    5007,
                    5008,
                    5003
                ],
                "perkStyle": 8200,
                "perkSubStyle": 8300
            }
        }
    ],
    platformId: "NA1",
    bannedChampions: [],
    gameStartTime: 1628918588253,
    gameLength: 1128
};

const UNRANKED = {
    "tier": "UNRANKED"
};

module.exports = {
    DUMMY_SUMMONER, DUMMY_RANKS, DUMMY_LIVE_GAME, UNRANKED
}