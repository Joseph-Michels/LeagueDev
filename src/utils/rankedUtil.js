const TIER_VALUES = {
    'UNRANKED': 0,
    'IRON': 1,
    'BRONZE': 2,
    'SILVER': 3,
    'GOLD': 4,
    'PLATINUM': 5,
    'DIAMOND': 6,
    'MASTER': 7,
    'GRANDMASTER': 8,
    'CHALLENGER': 9
};

const RANK_VALUES = {
    'IV': 4,
    'III': 3,
    'II': 2,
    'I': 1
};

function ranksSortValue(r1, r2) {
    let tierVal1 = TIER_VALUES[r1.tier];
    let tierVal2 = TIER_VALUES[r2.tier];
    if(tierVal2 > tierVal1) {
        return 1;
    } else if(tierVal2 < tierVal1) {
        return -1;
    } else {
        let rankVal1 = RANK_VALUES[r1.rank];
        let rankVal2 = RANK_VALUES[r2.rank];
        if(rankVal2 < rankVal1) {
            return 1;
        } else if(rankVal2 > rankVal1) {
            return -1;
        } else {
            return r2.leaguePoints - r1.leaguePoints;
        }
    }
}

async function getLeaderboardRanksSummoners(group, database) {
    let arr = [];
    for(let i = 0; i < group.ids.length; i++) {
        let summoner = await database.getSummonerById(group.ids[i]);
        let thisRanks = await database.getRanksById(summoner.id);
        arr.push({summoner: summoner, ranks: thisRanks});
    }
    arr.sort((e1, e2) => {
        return ranksSortValue(e1.ranks.solo, e2.ranks.solo);
    });

    let ranks = [];
    let summoners = [];
    for(let i = 0; i < arr.length; i++) {
        ranks.push(arr[i].ranks);
        summoners.push(arr[i].summoner);
    }

    return { ranks, summoners };
}

module.exports = {
    getLeaderboardRanksSummoners
};