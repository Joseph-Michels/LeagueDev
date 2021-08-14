const Requester = require('./requester');
const Firestore = require('./firestore');

const { DUMMY_SUMMONER, DUMMY_RANKS, DUMMY_LIVE_GAME, UNRANKED } = require('../utils/dummyResponseUtil');

class Database {
    constructor(useDummyResponses=false, verbose=false) {
        this.USE_DUMMY_RESPONSES = useDummyResponses;
        this.VERBOSE = verbose;

        this.requester = new Requester();
        this.firestore = new Firestore();
    }

    async getSummonerByName(name, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return DUMMY_SUMMONER;
        }

        // check if cached in firestore
        let summoner = await this.firestore.getSummonerByName(name, this.VERBOSE || verbose);
        if(summoner) {
            return summoner;
        }

        // http request and cache it
        summoner = await this.requester.getSummonerByName(name, this.VERBOSE || verbose);
        this.firestore.cacheSummoner(summoner, true);
        return summoner;  
    }

    async getSummonerByPuuid(id, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return DUMMY_SUMMONER;
        }

        // check if cached in firestore
        let summoner = await this.firestore.getSummonerByPuuid(id, this.VERBOSE || verbose);
        if(summoner) {
            return summoner;
        }

        // otherwise http request and cache it
        summoner = await this.requester.getSummonerByPuuid(id, this.VERBOSE || verbose);
        this.firestore.cacheSummoner(summoner, false);
        return summoner;  
    }

    async getRanksBySummonerId(summonerId, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return DUMMY_RANKS;
        }

        // check if cached in firestore
        let ranks = await this.firestore.getRanksBySummonerId(summonerId, this.VERBOSE || verbose);
        if(ranks) {
            return ranks;
        }

        // otherwise http request and cache it
        let ranksRaw = await this.requester.getRanksBySummonerId(summonerId, this.VERBOSE || verbose);
        ranks = { 'solo': UNRANKED, 'flex': UNRANKED };
        ranksRaw.forEach(rank => {
            if(rank.queueType === "RANKED_SOLO_5x5") {
                ranks.solo = rank;
            } else if(rank.queueType === "RANKED_FLEX_SR") {
                ranks.flex = rank;
            } else {
                console.log(`UNKNOWN QUEUE TYPE: ${rank.queueType}`);
            }
        });
        this.firestore.cacheRanks(summonerId, ranks);
        return ranks;  
    }
    
    // returns undefined if not in game and gets 404
    async getLiveGameBySummonerId(summonerId, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return DUMMY_LIVE_GAME;
        }

        // check if cached in firestore
        let liveGame = await this.firestore.getLiveGameBySummonerId(summonerId, this.VERBOSE || verbose);
        if(liveGame) {
            return liveGame;
        }

        // otherwise http request and cache it
        liveGame = await this.requester.getLiveGameBySummonerId(summonerId, this.VERBOSE || verbose);
        if(liveGame.status === undefined) {
            this.firestore.cacheLiveGame(liveGame);
            return liveGame;
        }
    }
}

module.exports = Database;