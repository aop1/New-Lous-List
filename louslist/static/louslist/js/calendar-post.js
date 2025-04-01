let calendar;
const colors = ["#C5C1FF", "#D3E5F0", "#74DAED", "#C0FFDF", "#4BFF97", "#C7FF10", "#DFEFA9", "#FFFA9F", "#FFF200", "#FFDDB9", "#FFB3F2", "#D2A2FF"]

window.addEventListener("load", () => {
    loadCalendar();
});

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
    try {
        const response = await fetch(`/api/${route}/`, request);
        return await response.json();
    }
    catch {
        return { "Result": "Failure" };
    }

}

const loadEventsFromSchedule = (schedule) => {
    schedule["classes"].forEach((section) => {
        addToCalendar(section, section.id);
    });
}

const loadCalendar = () => {
    const schedules = getSchedule();
    let calendarBody = document.getElementById("calendar");
    calendar = new FullCalendar.Calendar(calendarBody, {
        themeSystem: "bootstrap5",
        initialView: "timeGridWeek",
        slotMinTime: "06:00:00",
        slotMaxTime: "21:00:00",
        //allDaySlot: false,
        nowIndicator: true,
        eventTextColor: "#000000",
        eventMouseEnter: (info) => {
            onMouseEnter(info.el);
        },
        eventMouseLeave: (info) => {
            onMouseLeave(info.el);
        },
    })
    calendar.render();
    let allDayLabel = document.querySelector("#calendar > div.fc-view-harness.fc-view-harness-active > div > table > tbody > tr:nth-child(1) > td > div > div > div > table > tbody > tr > td.fc-timegrid-axis.fc-scrollgrid-shrink > div > span");
    allDayLabel.insertAdjacentHTML("afterend", "<p class=\"me-2\">TBD</p>");
    loadEventsFromSchedule(schedules);

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

const parseData = (dataId) => {
    let data = document.getElementById(dataId).value;
    if (!data) {
        return [];
    }
    return JSON.parse(data);
}


const getSchedule = () => {
    const schedule = parseData("schedule-value");
    return schedule;
}

const getDateOfCurrentWeek = (dayOfWeekStr) => {
    const daysToNum = { "Su": 0, "Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6 };
    const today = new Date();
    const offset = today.getDate() - today.getDay() + daysToNum[dayOfWeekStr];
    return new Date(today.setDate(offset));
}

const addTBDCourseMeeting = (sectionData, meetingId) => {
    let color = colors.pop()
    colors.unshift(color);
    let eventData = {
        id: meetingId,
        title: `${sectionData["subject"]} ${sectionData["catalog_number"]} - ${sectionData["component"]}`,
        start: getDateOfCurrentWeek("Mo"),
        allDay: true,
        description: "TBD",
        color: color,
    }
    calendar.addEvent(eventData);
    calendar.render();

}

const addCourseMeeting = (sectionData, meetingId, days, startTime, endTime, facility_description) => {
    let color = colors.pop()
    colors.unshift(color);
    let eventData = {
        id: meetingId,
        title: `${sectionData["subject"]} ${sectionData["catalog_number"]} - ${sectionData["component"]}`,
        startTime: startTime,
        endTime: endTime,
        daysOfWeek: days,
        allDay: false,
        description: facility_description,
        color: color,
    }
    calendar.addEvent(eventData);
    calendar.render();
}

const getDaysOfWeek = (daysStr) => {
    if (daysStr === "-") {
        return [1];
    }
    let days = daysStr.match(/.{2}/g)
    const daysToNum = { "Su": 0, "Mo": 1, "Tu": 2, "We": 3, "Th": 4, "Fr": 5, "Sa": 6 };
    let dayNums = []
    days.forEach((day) => {
        dayNums.push(daysToNum[day]);
    })
    return dayNums;
}


const addToCalendar = (courseData, baseId) => {
    let courseMeetings = courseData["meetings"];
    courseMeetings.forEach((meeting, index) => {
        const meetingId = `${baseId.toString()}-${index}`
        let daysOfWeek = getDaysOfWeek(meeting["days"]);
        if (meeting["start_time"] === ":" || meeting["end_time"] === ":") {
            addTBDCourseMeeting(courseData, meetingId);
        }
        else {
            addCourseMeeting(courseData, meetingId, daysOfWeek, meeting["start_time"], meeting["end_time"], meeting["facility_description"]);
        }

    });
}


const onMouseEnter = (eventElement) => {
    eventElement.classList.add("shadow");
}

const onMouseLeave = (eventElement) => {
    eventElement.classList.remove("shadow");
}

const parseCommentField = () => {
    const commentField = document.getElementById("comment-field");
    return commentField.value;
}

const addCommentToDB = async (commentText, scheduleId) => {
    const data = {
        "schedule_id": scheduleId,
        "text": commentText
    };
    let response = await postToLousList("post-comment", data);
    if (response["result"] === "Success") {
        return response["id"];
    }
    return null;
}

const removeCommentFromDB = async (commentID) => {
    const data = {
        "comment_id": commentID
    };
    let response = await postToLousList("delete-comment", data);
    if (response["result"] == "Success") {
        return true;
    }
    return false;
}

const displayNewComment = (username, profileImg, commentText, commentID) => {
    const date = new Date();
    const dateStr = `${date.toLocaleDateString("en-us")} ${date.toLocaleTimeString("en-us")}`
    const commentHTML = `
    <div class="comment d-flex flex-row align-items-center mb-3" id="comment-${commentID}" onmouseenter="showCommentAction(${commentID}, true);" onmouseleave="showCommentAction(${commentID}, false);">
            <img src="https://iili.io/${profileImg}" class="d-block me-2" alt-text="profile-image-${username}" width="40px" height="40px" />
            <div class="comment-body">
                <p class="fw-bold me-3 d-inline">${username}</p>
                <p class="text-muted d-inline">${dateStr}</p>
                <p class="mb-0">${commentText}</p>
            </div>
            <div class="dropdown ms-auto">
                    <button class="comment-action btn m-0 p-0 d-none text-danger" id="comment-action-${commentID}" onclick="deleteComment(${commentID});">
                        <i class="bi bi-trash3"></i>
                    </button>
                </div>
        </div>
    `
    const commentBody = document.getElementById("comments-body");
    commentBody.insertAdjacentHTML("afterbegin", commentHTML)
}

const hideComment = (commentId) => {
    const comment = document.querySelector(`#comment-${commentId}`);
    comment.classList.add("d-none");
}

const addComment = () => {
    const schedule = parseData("schedule-value");
    const comment = parseCommentField();
    const user = parseData("user-value");
    addCommentToDB(comment, schedule.id)
        .then((id) => {
            if (id) {
                let headerText = `
                <i class="bi bi-chat"></i>
                <p class="d-inline">Successfully posted comment</p>
                `
                addToast(headerText, `Successfully added your comment to ${schedule["name"]}`, true);
                displayNewComment(user["username"], user["profile_pic"], comment, id);
            }
            else {
                let headerText = `
                <i class="bi bi-chat"></i>
                <p class="d-inline">Error when posting comment</p>
                `
                addToast(headerText, `We were unable add your comment to ${schedule["name"]}`, false);
            }
        });
}

const deleteComment = (commentID) => {
    const schedule = parseData("schedule-value");
    removeCommentFromDB(commentID)
        .then((isSuccessful) => {
            if (isSuccessful) {
                let headerText = `
                <i class="bi bi-trash3"></i>
                <p class="d-inline">Successfully deleted comment</p>
                `
                addToast(headerText, `Successfully deleted your comment from ${schedule["name"]}`, true);
                hideComment(commentID);
            }
            else {
                let headerText = `
                <i class="bi bi-trash3"></i>
                <p class="d-inline">Unable to delete your comment</p>
                `
                addToast(headerText, `We were unable to delete your comment from ${schedule["name"]}`, false);
            }
        })
}

const showCommentAction = (commentId, isShown) => {
    const actionButton = document.getElementById(`comment-action-${commentId}`);
    if (isShown) {
        actionButton.classList.remove("d-none");
    }
    else {
        actionButton.classList.add("d-none");
    }

}

const updateFriendToDB = async (friendID, addingFriend) => {
    const data = {
        "user_id": friendID
    };
    let response;
    if (addingFriend) {
        response = await postToLousList("add-friend", data);
    }
    else {
        response = await postToLousList("remove-friend", data);
    }

    if (response["result"] === "Success") {
        return true;
    }
    return false;
}

const showFriendButton = (friendID, friendUsername, showAdd) => {
    const friendButtonsBody = document.getElementById("friend-buttons");
    if (showAdd) {
        const removeButton = document.getElementById(`remove-friend-${friendID}`);
        removeButton.remove();
        const addButtonHTML = `<button type="button" id="add-friend-${friendID}" class="btn btn-outline-success float-end ms-5" onclick="addFriend(${friendID}, '${friendUsername}')">Add Friend</button>`;
        friendButtonsBody.insertAdjacentHTML("beforeend", addButtonHTML);
    }
    else {
        const addButton = document.getElementById(`add-friend-${friendID}`);
        addButton.remove();
        const removeButtonHTML = `<button type="button" id="remove-friend-${friendID}" class="btn btn-outline-danger float-end ms-5" onclick="removeFriend(${friendID}, '${friendUsername}')">Remove Friend</button>`;
        friendButtonsBody.insertAdjacentHTML("beforeend", removeButtonHTML);

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


