window.onload = function (event) {
    addSearchTerms();
};
var addSearchTerms = function () {
    var recentBody = document.getElementById("recent-body");
    if (recentBody === null) {
        return;
    }
    recentBody.innerHTML = "";
    var key = "quickSearch";
    var termStr = localStorage.getItem(key);
    if (!termStr) {
        var msgElement = document.createElement("p");
        msgElement.innerText = "You haven't searched anything";
        recentBody.append(msgElement);
    }
    else {
        var terms = JSON.parse(termStr);
        terms.reverse().forEach(function (term) {
            var link = document.createElement("a");
            var searchTerm = term.replace(" ", "+");
            link.classList.add("d-block", "mb-2");
            link.href = "search/?q=".concat(searchTerm);
            link.innerText = term;
            recentBody.append(link);
        });
    }
};
