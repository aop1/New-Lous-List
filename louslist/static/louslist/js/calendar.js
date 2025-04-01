let calendar;
const colors = ["#C5C1FF", "#D3E5F0", "#74DAED", "#C0FFDF", "#4BFF97", "#C7FF10", "#DFEFA9", "#FFFA9F", "#FFF200", "#FFDDB9", "#FFB3F2", "#D2A2FF"]

window.addEventListener("load", () => {
    loadCalendar();
    initializeToolTip();
});

const initializeToolTip = () => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

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
    const response = await fetch(`/api/${route}/`, request);
    return await response.json();
}

const onScheduleSelectChange = () => {
    const scheduleData = getSchedules();
    const cartClasses = getCartClasses();
    cartClasses.forEach((cartClass) => {
        toggleAddAll(cartClass.id, true);
    })
    calendar.removeAllEvents();
    loadEventsFromSchedule(scheduleData);
}

const editDeleteSchedule = (scheduleId, scheduleData) => {
    const scheduleDeleteInput = document.getElementById("schedule-to-delete");
    scheduleDeleteInput.value = scheduleId;
    const scheduleDeleteMsgBody = document.getElementById("delete-warning-message");
    scheduleDeleteMsgBody.innerHTML = "";
    const scheduleDeleteMsg = `
    <p>You are about to delete ${scheduleData.name}.</p>
    <p>This operation cannot be undone.</p>`
    scheduleDeleteMsgBody.insertAdjacentHTML("beforeend", scheduleDeleteMsg);   
}

const editScheduleSettings = (scheduleId, scheduleData) => {
    const modal = document.querySelector("#schedule-settings");
    const id = modal.querySelector("#schedule-id");
    const title = modal.querySelector(".modal-title");
    const name = modal.querySelector("input[name='schedule_name']");
    const color = modal.querySelector("input[type='color']");
    const visibilityOptions = modal.querySelectorAll(`option`);
    
    id.value = scheduleId;
    title.textContent = `Schedule Settings - ${scheduleData.name}`
    name.value = scheduleData.name;
    color.value = scheduleData.color;
    
    visibilityOptions.forEach((option) => {
        const value = option.getAttribute("value");
        if(value && Number.parseInt(value) === scheduleData.is_private){
            option.setAttribute("selected", "");
        }
        else {
            option.removeAttribute("selected");
        }
    });
    
}

const loadEventsFromSchedule = (allScheduleData) => {
    const scheduleId = Number.parseInt(document.getElementById("select-schedule").value);
    const schedule = allScheduleData.get(scheduleId);
    schedule["classes"].forEach((section) => {
        addToCalendar(section, section.id);
        toggleAddAll(section.id, false);
    });
    editDeleteSchedule(scheduleId, schedule);
    editScheduleSettings(scheduleId, schedule);
}

const loadCalendar = () => {
    const schedules = getSchedules();
    if (schedules.size > 0) {
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
            eventDidMount: (info) => {
                onEventRender(info.event, info.el);
            }
        })
        calendar.render();
        let allDayLabel = document.querySelector("#calendar > div.fc-view-harness.fc-view-harness-active > div > table > tbody > tr:nth-child(1) > td > div > div > div > table > tbody > tr > td.fc-timegrid-axis.fc-scrollgrid-shrink > div > span");
        allDayLabel.insertAdjacentHTML("afterend", "<p class=\"me-2\">TBD</p>");
        loadEventsFromSchedule(schedules);
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

const parseData = (dataId) => {
    let cartClasses = document.getElementById(dataId);
    if (!cartClasses) {
        console.log(dataId);
        return [];
    }
    return JSON.parse(cartClasses.value);
}

const getCartClasses = () => {
    let cartClassesArr = parseData("cart-value");
    let cartClassesMap = new Map();
    cartClassesArr.forEach((cartClass) => {
        cartClassesMap.set(cartClass.id, cartClass)
    });
    return cartClassesMap;
}

const getSchedules = () => {
    const schedulesArr = parseData("schedule-value");
    const schedulesMap = new Map();
    schedulesArr.forEach((schedule) => {
        schedulesMap.set(schedule.id, schedule)
    })
    return schedulesMap;
}

const getSectionsMap = () => {
    return parseData("sections-map");
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
    if(daysStr === "-"){
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
        if(meeting["start_time"] === ":" || meeting["end_time"] === ":"){
            addTBDCourseMeeting(courseData, meetingId);
        }
        else {
            addCourseMeeting(courseData, meetingId, daysOfWeek, meeting["start_time"], meeting["end_time"], meeting["facility_description"]);
        }
       
    });
}

const getCourseSections = (courseId) => {
    const sections = getSectionsMap();
    const courses = getCartClasses();
    const courseNum = `${courses.get(courseId).subject} ${courses.get(courseId).catalog_number}`;
    return sections[courseNum];
}

const toggleAdd = (courseId, showAdd) => {
    let addButton = document.getElementById(`add-${courseId}`);
    if(!addButton){
        return;
    }
    if (showAdd) {
        addButton.classList.remove("disabled", "text-muted");
    }
    else {
        addButton.classList.add("disabled", "text-muted");
    }

}

const toggleAddAll = (courseId, showAdd) =>{
    const courseData = getCartClasses().get(courseId);
    //If we can't get the courseData from the cart, then it's not in the cart, so we don't need to modify any add buttons.
    if(!courseData){
        return;
    }

    const sections = getCourseSections(courseId);
    sections.forEach((section) => {
        if(section.component === courseData.component && section.topic === courseData.topic){
            toggleAdd(section.id, showAdd);
        }
    });
}

const removeFromCalendar = (course) => {
    let meetings = course.meetings;
    meetings.forEach((meeting, index) => {
        const event = calendar.getEventById(`${course.id}-${index}`);
        event.remove();
    })
    calendar.render();
}

const addSectionToScheduleDB = async (courseNumber, courseName) => {
    const scheduleId = Number.parseInt(document.getElementById("select-schedule").value);
    const scheduleName = getSchedules().get(scheduleId).name;
    const apiData = {
        "course_number": courseNumber,
        "schedule_id": scheduleId,
    }

    try {
        let response = await postToLousList('add-course-to-schedule', apiData);
        let toastHeader = "";
        if (response["result"] === "Success") {
            toastHeader = `
                <i class="bi bi-calendar-check me-2"></i>
                <p class="d-inline">Successfully added to schedule</p>`
            addToast(toastHeader, `Added ${courseName} to ${scheduleName}`, true);
            return true;
        }
        else if (response["result"] === "Time Conflict") {
            toastHeader = `
                <i class="bi bi-clock-fill me-2"></i>
                <p class="d-inline">Time Conflict Detected</p>
                `
            addToast(toastHeader, `Cannot add ${courseName} to ${scheduleName} because of a time conflict with another course`, false);
            return false;
        }

        toastHeader =
            `<i class="bi bi-calendar-x me-2"></i>
                Error when adding to schedule
            `
        addToast(toastHeader, `An error occured when we tried to add  ${courseName} to ${scheduleName}`, false);
        return false;
    }
    catch {
        toastHeader =
            `<i class="bi bi-calendar-x"></i>
                Error when adding to schedule
            `
        addToast(toastHeader, `An error occured when we tried to add  ${courseName} to ${scheduleName}`, false);
        return false;
    }
}

const removeSectionFromScheduleDB = async (courseNumber, courseName) => {
    const scheduleId = Number.parseInt(document.getElementById("select-schedule").value);
    const scheduleName = getSchedules().get(scheduleId).name;
    const apiData = {
        "course_number": courseNumber,
        "schedule_id": scheduleId,
    }
    try {
        let response = await postToLousList('remove-course-from-schedule', apiData);
        if (response["result"] === "Success") {
            toastHeader = `
                <i class="bi bi-trash3 me-2"></i>
                <p class="d-inline">Successfully removed from schedule</p>`
            addToast(toastHeader, `Removed ${courseName} from ${scheduleName}`, true);
            return true;
        }
        else {
            toastHeader = `
                <i class="bi bi-trash3 me-2"></i>
                <p class="d-inline">Unable to remove from schedule</p>`
            addToast(toastHeader, `An error occured when we tried to remove ${courseName} from ${scheduleName}`, false);
            return false;
        }
    }
    catch {
        toastHeader = `
                <i class="bi bi-trash3 me-2"></i>
                <p class="d-inline">Unable to remove from schedule</p>`
        addToast(toastHeader, `An error occured when we tried to remove ${courseName} from ${scheduleName}`, false);
        return false;
    }

}

const updateScheduleValues = () => {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0];
    let request = {
        method: "GET",
        headers: {
            "X-CSRFToken": token.value,
            "Content-Type": "application/json"
        },
    };
    fetch("/api/get-all-schedules", request)
    .then((response) => response.json())
    .then((data) => {
        const scheduleDataValue = document.getElementById("schedule-value");
        scheduleDataValue.value = JSON.stringify(data["schedules"]);
    })
}

const getScheduleCourse = (scheduleId, classId) => {
    const schedule = getSchedules().get(Number.parseInt(scheduleId));
    const courses = schedule.classes;
    if(courses){
        for(let i = 0; i < courses.length; i++){
            if(courses[i].id === classId){
                return courses[i];
            }

        }
    }
    return null;
}

const getSelectedSchedule = () => {
    const selectedSchedule = document.getElementById("select-schedule");
    const scheduleId = selectedSchedule.options[selectedSchedule.selectedIndex].value;
    if(!scheduleId){
        return -1;
    }
    return scheduleId;
}


const addToSchedule = (courseId) => {
    const cartClasses = getCartClasses();
    const courseName = `${cartClasses.get(courseId).subject} ${cartClasses.get(courseId).catalog_number} - ${cartClasses.get(courseId).component}`;
    const courseNum = cartClasses.get(courseId).course_number;
    addSectionToScheduleDB(courseNum, courseName)
        .then((result) => {
            if (result) {
                addToCalendar(cartClasses.get(courseId), courseId);
                toggleAddAll(courseId, false);
            }
            updateScheduleValues();
        });
}


const removeFromSchedule = (courseId) => {
    const cartClasses = getCartClasses();
    const scheduleId = getSelectedSchedule();
    const course = getScheduleCourse(scheduleId, courseId);
    if(scheduleId === -1 || !course || !cartClasses){
        return;
    }
    const courseName = `${course.subject} ${course.catalog_number} - ${course.component}`;
    const courseNum = course.course_number;
    removeSectionFromScheduleDB(courseNum, courseName)
        .then((result) => {
            if (result) {
                removeFromCalendar(course);
                if (cartClasses.get(courseId)) {
                    toggleAddAll(courseId, true);
                }
                updateScheduleValues();
            }

        });

}

const onMouseEnter = (eventElement) => {
    eventElement.classList.add("shadow");
}

const onMouseLeave = (eventElement) => {
    eventElement.classList.remove("shadow");
}

const onEventRender = (calendarEvent, eventElement) => {
    let fullId = calendarEvent._def.publicId;
    let courseId = fullId.substring(0, fullId.search("-"));
    let header;
    if(calendarEvent._def.extendedProps.description === "TBD"){
        header = eventElement.querySelector(".fc-event-title");
    }
    else {
        header = eventElement.querySelector(".fc-event-time");
    }
    let closeButton = `
        <button class="bg-transparent border-0 p-0 float-end">
            <i class="bi bi-x" onclick="removeFromSchedule(${courseId});"></i>
        </button>
    `
    header.insertAdjacentHTML("beforeend", closeButton);
}

const toggleCourseDisplay = (courseId, showCourse) => {
    const courseCard = document.getElementById(`course-card-${courseId}`);
    if(showCourse){
        courseCard.classList.remove("d-none")
    }
    else {
        courseCard.classList.add("d-none");
    }
}

const getMeetingStr = (meetingArr) => {
    let meetingStr = ""
    meetingArr.forEach((meeting) => {
        meetingStr += Object.values(meeting);
    });
    return meetingStr;
}


const showSearchResults = () => {
    const searchCartInputValue = document.getElementById("search-cart-input").value.toLowerCase();
    const classesInCart = getCartClasses();
    let searchMap = new Map();
    classesInCart.forEach((course) => {
        searchMap.set(course.id, (Object.values(course).join(" ") + getMeetingStr(course["meetings"])).toLowerCase());
    })
    let results = [];
    searchMap.forEach((value, key) => {
        if(value.indexOf(searchCartInputValue) !== -1){
            results.push(key);
            toggleCourseDisplay(key, true);
        }
    });
    classesInCart.forEach((course) => {
        if(!results.includes(course.id)){
            toggleCourseDisplay(course.id, false);
        }
    })   
}


