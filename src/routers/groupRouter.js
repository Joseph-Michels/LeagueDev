const express = require('express');
const ejs = require('ejs');

const RankedUtil = require('../utils/rankedUtil');
const LiveGameUtil = require('../utils/liveGameUtil');

class GroupRouter {
    constructor(database, verbose=false) {
        this.VERBOSE = verbose;

        this.router = express.Router();

        this.router.get("/:groupId", async (req, res) => {
            res.redirect(`/group/${req.params.groupId}/leaderboard`);
        });
        
        this.router.get("/:groupId/leaderboard", async (req, res) => {
            let group = await database.firestore.getGroup(req.params.groupId);
            let leaderboard = await RankedUtil.getLeaderboardRanksSummoners(database, group);
            let liveGames = await LiveGameUtil.getLiveGames(database, group);
        
            let objects = {
                liveGames: liveGames,
                ranks: leaderboard.ranks,
                summoners: leaderboard.summoners
            };
        
            res.send(await ejs.renderFile('views/pages/groupLeaderboard.ejs', objects, {async: true}));
        });
    }
}

module.exports = GroupRouter;