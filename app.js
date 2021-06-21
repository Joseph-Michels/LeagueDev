// node_modules imports
const express = require('express');
const ejs = require('ejs');

// other file imports
const requester_module = require("./code/requester");


// node_modules initialization
const app = express();
app.set('view engine', 'ejs');

const PORT = 6500;

// other files initialization
const requester = new requester_module.Requester();


// tests
let objects = {
    test: "test value",
    test_array: [
        "test1", "test2", "test3"
    ],
    live_games: [
        {
            start: "23:45",
            mode1: "Ranked",
            mode2: "S/D",
            names: ["TsimpleT", "Tzuyu Fanboy"]
        },
        {
            start: "34:56",
            mode1: "Normal",
            mode2: "Draft",
            names: ["SpikyBuffalo", "vFirePat"]
        },
        {
            start: "23:45",
            mode1: "Ranked",
            mode2: "S/D",
            names: ["TsimpleT", "Tzuyu Fanboy"]
        },
        {
            start: "34:56",
            mode1: "Normal",
            mode2: "Draft",
            names: ["SpikyBuffalo", "vFirePat"]
        },
        {
            start: "23:45",
            mode1: "Ranked",
            mode2: "S/D",
            names: ["TsimpleT", "Tzuyu Fanboy"]
        },
        {
            start: "34:56",
            mode1: "Normal",
            mode2: "Draft",
            names: ["SpikyBuffalo", "vFirePat"]
        }
    ]
};



app.listen(PORT, (err) => {
    if(err) {
        console.log("ERROR in app.listen:");
        console.log(err);
    } else {
        console.log(`Server running on port ${PORT}`);
    }
});

app.get("/", (req, res) => {
    console.log("top function");
    requester.getSummoner('TsimpleT', true).then(async (value) => {
        console.log("objects");
        objects.async_test = value.name;
        console.log(objects)
        const html = await ejs.renderFile('views/pages/index.ejs', objects, {async: true});
        res.send(html);
        // res.render('pages/index', objects);
    });
});