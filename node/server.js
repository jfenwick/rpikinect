var fs = require("fs");
var express = require('express');
var app = express();
var bodyParser = require('body-parser');

// Create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: false })

app.use(express.static('public'));

app.get('/', function (req, res) {
   res.sendFile( __dirname + "/" + "index.htm" );
})

app.get('/index.htm', function (req, res) {
   res.sendFile( __dirname + "/" + "index.htm" );
})

app.post('/process_post', urlencodedParser, function (req, res) {

   // Prepare output in JSON format
   response = {
       start_depth:req.body.start_depth,
       end_depth:req.body.end_depth,
       min_area:req.body.min_area,
       blob_delta:req.body.blob_delta
   };
   fs.writeFile('input.txt', JSON.stringify(response),  function(err) {
     if (err) {
         return console.error(err);
     }
     console.log("Data written successfully!");
   });
   console.log(response);
   //res.end(JSON.stringify(response));
   //res.sendFile( __dirname + "/" + "index.htm" );
})

var server = app.listen(8081, function () {

  var host = server.address().address
  var port = server.address().port

  console.log("Example app listening at http://%s:%s", host, port)

})
