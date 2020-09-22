function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}

function getUrlParam(parameter, defaultvalue){
    var urlparameter = defaultvalue;
    if(window.location.href.indexOf(parameter) > -1){
        urlparameter = getUrlVars()[parameter];
        }
    return urlparameter;
}

function displayPageInformation() {
    imageName = getUrlParam("image", "");
    if (imageName) {
        document.getElementById("pageImage").src = "../pics/" + imageName;
    }
    document.getElementById("pageHeading").innerHTML = decodeURI(getUrlParam("pageHeading", ""));
    document.getElementById("pageText").innerHTML  = decodeURI(getUrlParam("pageText", ""));
}

function getPage(pageName) {
    pageName = pageName.toLowerCase();

    switch(pageName) {
        case "index":
            window.location = "../index.html";
            break;
        case "help":
            window.location = "help.html";
            break;
        case "displayinfo":
            window.location = "displayinfo.html";
            break;
        case "confirmation":
            window.location = "confirmation.html";
            break;
        case "displayimage":
            window.location = "displayimage.html";
            break;
        default:
            window.location = "../index.html";
            return;
    }
}

function confirmationButtonListener(n) {
    raiseEvent(getButtonId(n), n);
    //raiseEvent("serviceType", getButtonId(n));
}

function getButtonId(n) {
    switch(parseInt(n)) {
        case 1:
            return "noAnswer";
        case 2:
            return "yesAnswer";
        default:
            return "yesAnswer";
    }
}