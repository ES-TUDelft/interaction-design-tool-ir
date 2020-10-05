$(document).ready(function () {
    // Create qi session
    QiSession(function (session) {
        console.log("Created a session and connected!");
    }, function () {
        console.log("Disconnected");
    });
})

function raiseEvent(name, value) {
    QiSession(function (session) {
        session.service("ALMemory").then(function (mem) {
            mem.raiseEvent(name, value);
        }, function (error) {
            console.log("An error occurred: ", error);
        });
    });
}

function raiseInputFieldEvent() {
    fieldKey = "TabletInput";
    fieldValue = document.getElementById("inputField").value;

    // document.getElementById("result").innerHTML = fieldKey + " = " + fieldValue;
    raiseEvent(fieldKey, fieldValue);
}