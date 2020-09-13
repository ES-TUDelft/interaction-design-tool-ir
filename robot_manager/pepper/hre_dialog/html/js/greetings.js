$(document).ready(function () {
    // Create qi session
    QiSession(function (session) {
        console.log("Created a session and connected!");

        // Load the ALmemory service and raise an event that shows that the greeting page was loaded
        session.service("ALMemory").then(function (mem) {
            mem.raiseEvent("pageLoaded", "greetings");

        }, function(error) {
            console.log("An error occurred:", error);
        });
    }, function () {
        console.log("disconnected");
    });
})

function getPage(pageName) {
    pageName = pageName.toLowerCase();
    switch(pageName) {
        case "index":
            window.location = "../index.html";
            break;
        case "consent":
            window.location = "consent.html";
            break;
        default:
            window.location = "../index.html";
            return;
    }
}