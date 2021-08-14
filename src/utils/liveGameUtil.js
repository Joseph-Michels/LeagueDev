const QUEUE_CONSTANTS = require('../../constants/queueConstants');

function GET_TIME(num) {
    if(num === 0) {
        return "00:00";
    } else {
        let secDiff = 0.001*(new Date() - new Date(num));
        let leftoverSeconds = Math.floor(secDiff%60);
        if(leftoverSeconds < 10) {
            leftoverSeconds = '0'+leftoverSeconds;
        }
        return `${Math.floor(secDiff/60)}:${leftoverSeconds}`;
    }
}

function ABBREVIATE_MAP(map) {
    switch(map) {
        case "Summoner's Rift":
            return 'S. Rift';
        default:
            return map;
    }
}

function ABBREVIATE_MODE(mode) {
    switch(mode) {
        case "5v5 Ranked Solo games":
            return "S/D";
        case "One for All games":
            return 'OneFAll';
        default:
            return mode;
    }
}

async function getLiveGames(database, group) {
    // gather summoners and raw live games
    let summoners = [];
    let rawLiveGames = [];
    for(let i = 0; i < group.ids.length; i++) {
        let summoner = await database.getSummonerByPuuid(group.ids[i]);
        summoners.push(summoner);
        let thisRawLiveGame = await database.getLiveGameBySummonerId(summoner.id);
        if(thisRawLiveGame) {
            let alreadyAdded = false;
            rawLiveGames.forEach(rawLiveGame => {
                if(rawLiveGame.gameId === thisRawLiveGame.gameId) {
                    alreadyAdded = true;
                }
            });
            if(!alreadyAdded) {
                rawLiveGames.push(thisRawLiveGame);
            }
        }
    }

    // simply format live games
    let liveGames = [];
    rawLiveGames.forEach(rawLiveGame => {
        let queue = QUEUE_CONSTANTS[rawLiveGame.gameQueueConfigId];
        let names = [];
        rawLiveGame.participants.forEach(participant => {
            summoners.forEach(summoner => {
                if(summoner.id === participant.summonerId) {
                    names.push(participant.summonerName);
                }
            });
        });
        liveGames.push({
            start: GET_TIME(rawLiveGame.gameStartTime),
            map:   ABBREVIATE_MAP(queue.map),
            mode:  ABBREVIATE_MODE(queue.description),
            names: names
        });
    });

    return liveGames;
}

module.exports = {
    getLiveGames
};