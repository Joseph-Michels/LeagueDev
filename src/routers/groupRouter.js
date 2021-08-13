const express = require('express');
const ejs = require('ejs');

const RankedUtil = require('../utils/rankedUtil');

/*
liveGames: [
    // {
    //     start: "23:45",
    //     mode1: "Ranked",
    //     mode2: "S/D",
    //     names: ["TsimpleT", "Tzuyu Fanboy"]
    // },
    // {
    //     start: "34:56",
    //     mode1: "Normal",
    //     mode2: "Draft",
    //     names: ["SpikyBuffalo", "vFirePat"]
    // }
]
*/

class GroupRouter {
    constructor(database, verbose=false) {
        this.VERBOSE = verbose;

        this.router = express.Router();

        this.router.get("/:groupId", async (req, res) => {
            res.redirect(`/group/${req.params.groupId}/leaderboard`);
        });
        
        this.router.get("/:groupId/leaderboard", async (req, res) => {
            let group = await database.firestore.getGroup(req.params.groupId);
            let leaderboard = await RankedUtil.getLeaderboardRanksSummoners(group, database);
        
            let objects = {
                liveGames: [],
                ranks: leaderboard.ranks,
                summoners: leaderboard.summoners
            };
        
            res.send(await ejs.renderFile('views/pages/groupLeaderboard.ejs', objects, {async: true}));
        });
    }
}

module.exports = GroupRouter;