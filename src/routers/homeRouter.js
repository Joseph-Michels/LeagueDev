const express = require('express');
const ejs = require('ejs');

class HomeRouter {
    constructor(database, verbose=false) {
        this.VERBOSE = verbose;

        this.router = express.Router();

        this.router.get("/", async (req, res) => {
            let groupDict = (await database.firestore.getGroups());
        
            let objects = {
                groupNames: groupDict.names,
                groupIds: groupDict.ids
            }
        
            res.send(await ejs.renderFile('views/pages/home.ejs', objects, {async: true}));
        });
    }
}

module.exports = HomeRouter;