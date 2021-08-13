const Requester = require('./requester');
const Firestore = require('./firestore');

const { DUMMY_SUMMONER, DUMMY_RANKS, UNRANKED } = require('../utils/dummyResponseUtil');

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

    async getSummonerById(id, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return DUMMY_SUMMONER;
        }

        // check if cached in firestore
        let summoner = await this.firestore.getSummonerById(id, this.VERBOSE || verbose);
        if(summoner) {
            return summoner;
        }

        // http request and cache it
        summoner = await this.requester.getSummonerById(id, this.VERBOSE || verbose);
        this.firestore.cacheSummoner(summoner, false);
        return summoner;  
    }

    async getRanksById(summonerId, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return DUMMY_RANKS;
        }

        // check if cached in firestore
        let ranks = await this.firestore.getRanksById(summonerId, this.VERBOSE || verbose);
        if(ranks) {
            return ranks;
        }

        // http request and cache it
        let ranksRaw = await this.requester.getRanksById(summonerId, this.VERBOSE || verbose);
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
}

module.exports = Database;