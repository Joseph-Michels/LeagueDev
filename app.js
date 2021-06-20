// node_modules imports
const express = require('express');

// other file imports
const requester_module = require("./code/requester");


// node_modules initialization
const app = express();
app.set('view engine', 'ejs');

const PORT = 6500;

// other files initialization
const requester = new requester_module.Requester();




app.listen(PORT, (err) => {
    if(err) {
        console.log("ERROR in app.listen:");
        console.log(err);
    } else {
        console.log(`Server running on port ${PORT}`);
    }
});

app.get("/", (req, res) => {
    let objects = {
        test: requester.getStatus(),
        test_array: [
            "test1", "test2", "test3"
        ]
    };
    res.render('pages/index', objects);
});