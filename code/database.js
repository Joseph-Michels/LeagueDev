const admin = require('firebase-admin');

class Database {
    constructor() {
        const envSet = (process.env['FS_type'] === true);
        let serviceAccount;

        if(envSet) {
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
        } else {
            serviceAccount = require('./credentials.js').FIRESTORE;
        }
        
        admin.initializeApp({
            credential: admin.credential.cert(serviceAccount)
        });
        this.db = admin.firestore();
    }

    async getSummonerName() {
        return (await this.db.collection('test').doc('testdocument').get('testkey')).data();
    }

    // const docRef = this.db.collection('test').doc('alovelace');
    // return docRef.set({
    //     first: 'Ada',
    //     last: 'Lovelace',
    //     born: 1815
    // });
}

module.exports = Database;