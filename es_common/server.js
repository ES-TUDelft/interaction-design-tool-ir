var http = require('http');
http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.write("http://" + req.headers.host + req.url);
  res.end();
}).listen(8080);
console.log("Successfully started the server.\nListening at: http://localhost:8080\nUse Ctrl+C to exit.");