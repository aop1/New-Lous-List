var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
const postToLousList = (route, data) => __awaiter(this, void 0, void 0, function* () {
    const token = document.getElementsByName("csrfmiddlewaretoken")[0];
    let request = {
        method: "POST",
        headers: {
            "X-CSRFToken": token.value,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data),
    };
    const response = yield fetch(`/api/${route}/`, request);
    return yield response.json();
});

const toggleAddRemoveButton = (subject, catalogNumber, showAdd) => {
    const addButton = document.getElementById(`add-${subject}-${catalogNumber}`);
    const removeButton = document.getElementById(`remove-${subject}-${catalogNumber}`);
    if (!addButton || !removeButton) {
        return;
    }
    if (!showAdd) {
        addButton.classList.add("d-none");
        removeButton.classList.remove("d-none");
    }
    else {
        addButton.classList.remove("d-none");
        removeButton.classList.add("d-none");
    }
};
const getSectionNumbers = (subject, catalogNumber) => {
    const sections = [];
    const sectionElements = Array.from(document.getElementsByClassName(`${subject}-${catalogNumber}`));
    sectionElements.forEach((section) => {
        sections.push(section.value);
    });
    return sections;
};
const getMeetingData = (courseData) => {
    let meetings = courseData["meetings"];
    let topMeeting = {
        "days": courseData["days"],
        "start_time": courseData["start_time"],
        "end_time": courseData["end_time"],
        "facility_description": courseData["facility_description"]
    };
    meetings.push(topMeeting);
    return meetings;
};
const getSectionData = (subject, catalogNumber) => {
    const sectionData = [];
    const sectionElements = Array.from(document.getElementsByClassName(`${subject}-${catalogNumber}`));
    sectionElements.forEach((section) => {
        const dataCourse = section.getAttribute("data-course");
        const data = dataCourse ? JSON.parse(dataCourse === null || dataCourse === void 0 ? void 0 : dataCourse) : null;
        if (data) {
            const meetingData = getMeetingData(data);
            sectionData.push({
                "instructor": data["instructor"]["name"],
                "course_number": data["course_number"],
                "semester_code": data["semester_code"],
                "course_section": data["course_section"],
                "subject": data["subject"],
                "catalog_number": data["catalog_number"],
                "description": data["description"],
                "units": data["units"],
                "component": data["component"],
                "topic": data["topic"],
                "meetings": meetingData,
            });
        }
    });
    return sectionData;
};
const addToast = (header, message, successful) => {
    var _a;
    //Get template for the toast
    const toast = (_a = document.getElementById("success-toast")) === null || _a === void 0 ? void 0 : _a.cloneNode(true);
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
    setTimeout(() => { toastContainer.removeChild(toast); }, 5000);
};
const sendSectionNumbers = (route, subject, sectionNumbers) => __awaiter(this, void 0, void 0, function* () {
    let data = [];
    console.log(subject);
    console.log(sectionNumbers);
    //Send a POST request for each section number
    for (let i = 0; i < sectionNumbers.length; i++) {
        try {
            const requestData = {
                "prefix": subject,
                "number": sectionNumbers[i],
            };
            data[i] = yield postToLousList(route, requestData);
            if (data[i].result === "Failure") {
                return false;
            }
        }
        catch (_a) {
            return false;
        }
    }
    return data.length === sectionNumbers.length;
});
const sendSectionData = (route, subject, sectionData) => __awaiter(this, void 0, void 0, function* () {
    let data = [];
    //Send a POST request for each section number
    for (let i = 0; i < sectionData.length; i++) {
        try {
            data[i] = yield postToLousList(route, sectionData[i]);
            if (data[i].result !== "Success") {
                console.log(data[i].result);
                return false;
            }
        }
        catch (_b) {
            return false;
        }
    }
    return data.length === sectionData.length;
});
const addClassToCart = (subject, catalogNumber) => {
    //Get section numbers for the course
    const sectionData = getSectionData(subject, catalogNumber);
    //Send a POST request with the section numbers, send to add to cart
    sendSectionData("add-course-to-cart", subject, sectionData)
        .then((success) => {
        if (success) {
            //Show success message
            const header = "<i class='bi bi-check-circle-fill me-1'></i><strong>Successfully added to cart</strong>";
            const message = `Successfully added ${subject} ${catalogNumber} to your cart.`;
            addToast(header, message, success);
            //Show remove button
            toggleAddRemoveButton(subject, catalogNumber, false);
        }
        else {
            //Show failure message
            const header = "<i class=\"bi bi-exclamation-circle-fill me-1\"></i><strong>Unable to add to cart</strong>";
            const message = `We were unable to add ${subject} ${catalogNumber} to your cart.`;
            addToast(header, message, false);
        }
    });
};
const removeClassCart = (subject, catalogNumber) => {
    //Get section numbers for the course
    const sectionNumbers = getSectionNumbers(subject, catalogNumber);
    console.log(sectionNumbers);
    //Send a POST request with the section numbers, send to remove from cart
    sendSectionNumbers("remove-course-from-cart", subject, sectionNumbers)
        .then((successful) => {
        if (successful) {
            //Show success message
            const header = "<i class='bi bi-check-circle-fill me-1'></i><strong>Successfully deleted from cart</strong>";
            const message = `Successfully deleted ${subject} ${catalogNumber} from your cart.`;
            addToast(header, message, successful);
            document.location.reload();
        }
        else {
            //Show failure message
            const header = "<i class=\"bi bi-exclamation-circle-fill me-1\"></i><strong>Unable to delete from cart</strong>";
            const message = `We were unable to delete ${subject} ${catalogNumber} from your cart.`;
            addToast(header, message, false);
        }
    });
};
