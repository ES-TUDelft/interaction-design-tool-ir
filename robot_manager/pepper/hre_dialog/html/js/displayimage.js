function displayPageImage() {
    imageName = localStorage.getItem("pageImage");
    if (imageName) {
        document.getElementById("pageImage").src = "../pics/" + localStorage.getItem("pageImage");
    }
}