const toggleSeeFriendsButton = () => {
    const moreFriendsBtn = document.getElementById("show-more-friends-button");
    if(!moreFriendsBtn){
        return;
    }
    const text = moreFriendsBtn.querySelector("p");
    const icon = moreFriendsBtn.querySelector("i");
    if(!text || !icon){
        return;
    }
    let newButtonHTML;
    if(text.textContent === "Show More Friends"){
        newButtonHTML = `
        <p class="d-inline">Show Less Friends</p>
        <i class="bi bi-chevron-up"></i>
        `;
    }
    else {
        newButtonHTML = `
        <p class="d-inline">Show More Friends</p>
        <i class="bi bi-chevron-down"></i>
        `;
    }
    moreFriendsBtn.innerHTML = "";
    moreFriendsBtn.insertAdjacentHTML("afterbegin", newButtonHTML);

}