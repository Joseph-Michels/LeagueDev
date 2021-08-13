const Requester = require('./requester');
const Firestore = require('./firestore');

const DUMMY_SUMMONER = {
    "id": "acu3F1E7p-t0JpIHbq2KXgpALV6TJW-FqEKGp3A2UHBuTwQ",
    "accountId": "nmFO671RROMhZgcAmhGuIl13XuQE0uADeDGJ6dpFL1Ia9tc",
    "puuid": "UyPV3Ji6PUh-Z4iiS4247S_P4eEjtbUbQcT6F3ZO45SQGGaLKeVDwC0I578Jpo7aMyBWohImxFhGnw",
    "name": "TsimpleT",
    "profileIconId": 3463,
    "revisionDate": 1625730827000,
    "summonerLevel": 346
};

const UNRANKED = {
    "tier": "UNRANKED"
}

class Database {
    constructor(useDummyResponses=false, verbose=false) {
        this.USE_DUMMY_RESPONSES = useDummyResponses;
        this.VERBOSE = verbose;

        this.requester = new Requester();
        this.firestore = new Firestore();
    }

    async getSummonerByName(name, verbose=false) {
        if(this.USE_DUMMY_RESPONSES) {
            return {
                "id": "acu3F1E7p-t0JpIHbq2KXgpALV6TJW-FqEKGp3A2UHBuTwQ",
                "accountId": "nmFO671RROMhZgcAmhGuIl13XuQE0uADeDGJ6dpFL1Ia9tc",
                "puuid": "UyPV3Ji6PUh-Z4iiS4247S_P4eEjtbUbQcT6F3ZO45SQGGaLKeVDwC0I578Jpo7aMyBWohImxFhGnw",
                "name": "TsimpleT",
                "profileIconId": 3463,
                "revisionDate": 1625730827000,
                "summonerLevel": 346
            };
        }

        // TODO check database
        // 

        // http request and cache it
        let summoner = await this.requester.getSummonerByName(name, this.VERBOSE || verbose);
        this.firestore.cacheSummoner(summoner);
        return summoner;  
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
            // TODO return
        }

        // check if cached in firestore
        let ranks = await this.firestore.getRanksById(summonerId, this.VERBOSE || verbose);
        if(ranks) {
            return ranks;
        }

        // http request and cache it
        let ranksRaw = await this.requester.getRanksById(summonerId, this.VERBOSE || verbose);
        console.log(ranksRaw);
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