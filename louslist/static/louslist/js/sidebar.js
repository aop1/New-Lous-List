var toggleSeeFriendsButton = function () {
    var moreFriendsBtn = document.getElementById("show-more-friends-button");
    if (!moreFriendsBtn) {
        return;
    }
    var text = moreFriendsBtn.querySelector("p");
    var icon = moreFriendsBtn.querySelector("i");
    if (!text || !icon) {
        return;
    }
    var newButtonHTML;
    if (text.textContent === "Show More Friends") {
        newButtonHTML = "\n        <p class=\"d-inline\">Show Less Friends</p>\n        <i class=\"bi bi-chevron-up\"></i>\n        ";
    }
    else {
        newButtonHTML = "\n        <p class=\"d-inline\">Show More Friends</p>\n        <i class=\"bi bi-chevron-down\"></i>\n        ";
    }
    moreFriendsBtn.innerHTML = "";
    moreFriendsBtn.insertAdjacentHTML("afterbegin", newButtonHTML);
};
