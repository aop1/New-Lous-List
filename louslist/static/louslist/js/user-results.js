const postToLousList = async (route, data) => {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0];
    let request = {
        method: "POST",
        headers: {
            "X-CSRFToken": token.value,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data),
    };
    try{
        const response = await fetch(`/api/${route}/`, request);
        return await response.json();
    }
    catch{
        return {"Result": "Failure"};
    }
    
}

const addToast = (header, message, successful) => {
    //Get template for the toast
    const toast = document.getElementById("success-toast")?.cloneNode(true);
    const toastContainer = document.getElementById("toast-container");
    if (!toast || !toastContainer) {
        return;
    }
    //Display the toast as block - make it visible
    toast.classList.add("d-block");
    toast.innerHTML = `
    <div class="toast-header">
        <span class="header me-auto ${successful ? "text-success" : "text-danger"}">
            ${header}
        </span>
    </div>
    <div class="toast-body">
        <p>${message}</p>
    </div>`;
    //Add child to toast container
    toastContainer.appendChild(toast);
    //Make toast disappear after 5000 ms
    setTimeout(() => { toastContainer.removeChild(toast) }, 5000);
}

const updateFriendToDB = async (friendID, addingFriend) => {
    const data = {
        "user_id": friendID
    };
    let response;
    if(addingFriend){
        response = await postToLousList("add-friend", data);
    }
    else {
        response = await postToLousList("remove-friend", data);
    }
    
    if (response["result"] === "Success"){
        return true;
    }
    return false;
}

const showFriendButton = (friendID, friendUsername, showAdd) => {
    const friendButtonsBody = document.getElementById(`friend-buttons-${friendID}`);
    if(showAdd){
        const removeButton = document.getElementById(`remove-friend-${friendID}`);
        removeButton.remove();
        const addButtonHTML = `<button type="button" id="add-friend-${friendID}" class="btn btn-outline-success w-132px" onclick="addFriend(${friendID}, '${friendUsername}')">Add Friend</button>`;
        friendButtonsBody.insertAdjacentHTML("afterbegin", addButtonHTML);
    }
    else {
        const addButton = document.getElementById(`add-friend-${friendID}`);
        addButton.remove();
        const removeButtonHTML = `<button type="button" id="remove-friend-${friendID}" class="btn btn-outline-danger w-132px" onclick="removeFriend(${friendID}, '${friendUsername}')">Remove Friend</button>`;
        friendButtonsBody.insertAdjacentHTML("afterbegin", removeButtonHTML);
        
    }

}

const insertFriendHTML = (allFriends, friendID, friendHTML) => {
    const friendsBody = document.getElementById("friends-list");
    if(!friendsBody){
        return;
    }

    for(let i = 0; i < allFriends.length; i++){
        const id = Number.parseInt(allFriends[i].id.substring(7));
        if(id > friendID){
            allFriends[i].insertAdjacentHTML("beforebegin", friendHTML);
            return;
        }
    }
    friendsBody.insertAdjacentHTML("beforeend", friendHTML);
}

const addFriendToList = (friendID, friendUsername) => {
    const profileImg = document.querySelector(`img[alt-text='profile-image-${friendUsername}']`);
    const friendsBody = document.getElementById("friends-list");
    //const moreFriendsBody = document.getElementById("morefriends");
    const allFriends = document.querySelectorAll(".friend-block");
    if (!profileImg || !friendsBody || !allFriends) {
        return;
    }
    const friendHTML = `
    <div class="friend-block d-flex flex-row align-items-center my-2" id="friend-${friendID}">
        <img src="${profileImg.src}" class="d-block me-3" alt-text="profile-image-${friendUsername}"
            width="50px" height="50px" />
            <a href="/social/user/${friendUsername}" class="d-block text-decoration-none link">
                ${friendUsername}
            </a>
    `
    insertFriendHTML(allFriends, friendID, friendHTML);
}

const removeFriendFromList = (friendID) => {
    const friendElement = document.getElementById(`friend-${friendID}`)
    if(!friendElement){
        return;
    }
    friendElement.remove();
}

const addFriend = (friendID, friendUsername) => {
    updateFriendToDB(friendID, friendUsername, true)
        .then((isSuccessful) => {
            if (isSuccessful) {
                let headerText = `
                <i class="bi bi-person-plus-fill"></i>
                <p class="d-inline">Successfully added friend</p>
                `
                addToast(headerText, `You are now friends with ${friendUsername}`, true);
                showFriendButton(friendID, friendUsername, false);
                addFriendToList(friendID, friendUsername);
            }
            else {
                let headerText = `
                <i class="bi bi-x-circle-fill"></i>
                <p class="d-inline">Error when adding friend</p>
                `
                addToast(headerText, `We were unable to add ${friendUsername} to your friends list.`, false);
            }
        });


}

const removeFriend = (friendID, friendUsername) => {
    updateFriendToDB(friendID, false)
        .then((isSuccessful) => {
            if (isSuccessful) {
                let headerText = `
            <i class="bi bi-person-x-fill"></i>
            <p class="d-inline">Successfully removed friend</p>
            `
                addToast(headerText, `You are now not friends with ${friendUsername}`, true);
                showFriendButton(friendID, friendUsername, true);
                removeFriendFromList(friendID);
            }
            else {
                let headerText = `
            <i class="bi bi-x-circle-fill"></i>
            <p class="d-inline">Error when removing friend</p>
            `
                addToast(headerText, `We were unable to remove ${friendUsername} from your friends list.`, false);
            }
        })
}