const admin = require('firebase-admin');

const HR_TO_MS = 60*60*1000;
const MIN_TO_MS = 60*1000;

const DATE_FROM = (timestamp) => {
    return new Date(1000*timestamp._seconds)
};

class Firestore {
    constructor() {
        let serviceAccount;

        try {
            serviceAccount = require('./credentials.js').FIRESTORE;
        } catch(e) {
            serviceAccount = {
                type:                           process.env['FS_type'],
                project_id:                     process.env['FS_project_id'],
                private_key_id:                 process.env['FS_private_key_id'],
                private_key:                    process.env['FS_private_key'],
                client_email:                   process.env['FS_client_email'],
                client_id:                      process.env['FS_client_id'],
                auth_uri:                       process.env['FS_auth_uri'],
                token_uri:                      process.env['FS_token_uri'],
                auth_provider_x509_cert_url:    process.env['FS_auth_provider_x509_cert_url'],
                client_x509_cert_url:           process.env['FS_client_x509_cert_url']
            };
            console.log(serviceAccount);
        }
        
        admin.initializeApp({
            credential: admin.credential.cert(serviceAccount)
        });
        this.db = admin.firestore();
    }

    /*
        ACCESS GROUP METHODS
    */

    async getTestSummonerName() {
        return (await this.db.collection('test').doc('testdocument').get()).data();
    }

    async getGroups() {
        let collection = await this.db.collection('groups').get();
        let groupIds = { names: [], ids: []};
        collection.forEach(group => {
            groupIds.names.push(group.data().name);
            groupIds.ids.push(group.id);
        });
        return groupIds;
    }

    async getGroup(groupId) {
        return (await this.db.collection('groups').doc(groupId).get()).data();
    }

    /*
        ACCESS METHODS
    */
    async getSummonerById(id, verbose) {
        let summoner = (await this.db.collection('cachedSummoners').doc(id).get()).data();
        if(summoner) {
            let expiresAt = DATE_FROM(summoner.expiresAt);
            if(new Date() < expiresAt) {
                summoner.expiresAt = expiresAt;
                return summoner;
            }
        }
    }

    async getSummonerByName(name, verbose) {
        let id = (await this.db.collection('cachedSummonerNames').doc(name).get()).data()?.puuid;
        if(id) {
            let summoner = await this.getSummonerById(id, verbose);
            if(summoner) {
                let expiresAt = DATE_FROM(summoner.expiresAt);
                if(new Date() < expiresAt) {
                    summoner.expiresAt = expiresAt;
                    return summoner;
                }
            }
        }
    }

    async getRanksById(summonerId, verbose) {
        let ranks = (await this.db.collection('cachedRanks').doc(summonerId).get()).data();
        if(ranks) {
            let expiresAt = DATE_FROM(ranks.expiresAt);
            if(new Date() <= expiresAt) {
                ranks.expiresAt = expiresAt;
                return ranks;
            }
        }
    }

    /*
        STORAGE METHODS
    */
    cacheSummoner(summoner, storeName) {
        let time = new Date();
        time.setTime(time.getTime() + 2*HR_TO_MS);
        summoner.expiresAt = time;
        this.db.collection('cachedSummoners').doc(summoner.puuid).set(summoner);
        if(storeName) {
            this.db.collection('cachedSummonerNames').doc(summoner.name).set({puuid: summoner.puuid, summonerId: summoner.id});
        }
    }

    cacheRanks(summonerId, ranks) {
        let time = new Date();
        time.setTime(time.getTime() + 30*MIN_TO_MS);
        ranks.expiresAt = time;
        this.db.collection('cachedRanks').doc(summonerId).set(ranks);
    }
}

module.exports = Firestore;