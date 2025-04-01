type MeetingData = {
    "days": string,
    "start_time": string,
    "end_time": string,
    "facility_description": string,
}

type CourseData = {
    "instructor": {
        "name": string,
        "email": string,
    }
    "course_number": number,
    "semester_code": number,
    "course_section": string,
    "subject": string,
    "catalog_number": string,
   "description": string,
   "units": string,
   "component": string,
   "class_capacity": number,
   "wait_list": number,
   "wait_cap": number,
   "enrollment_total": number,
   "enrollment_available":number,
   "topic": string,
   "meetings": MeetingData[],
   "start_time": string,
   "end_time":string,
   "days": string,
   "facility_description": string,
   "color": string,
}

type APIData = {
    result: string;
}

const postToLousList = async (route: string, data: object):Promise<SettingsAPIData> => {
    try {
        const token = document.getElementsByName("csrfmiddlewaretoken")[0] as HTMLInputElement;
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
    catch(error){
        return {"result": "Failure"}
    }
}

const addSpinner = (spinnerBodyId: string) => {
    let spinnerBody = document.getElementById(spinnerBodyId);
    if (!spinnerBody || spinnerBody.querySelector(".spinner-border")) {
        return;
    }
    let spinner = document.createElement("div");
    spinner.classList.add("spinner-border", "text-blue");
    spinnerBody.appendChild(spinner);
}

const toggleAddRemoveButton = (subject: string, catalogNumber: string, showAdd: boolean) => {
    const addButton = document.getElementById(`add-${subject}-${catalogNumber}`)
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
}

const getSectionNumbers = (subject: string, catalogNumber: string): string[] => {
    const sections: string[] = [];
    const sectionElements = Array.from(document.getElementsByClassName(`${subject}-${catalogNumber}`)) as HTMLElement[];
    sectionElements.forEach((section) => {
        sections.push(section.innerText);
    })
    return sections;
}

const getMeetingData = (courseData: CourseData): MeetingData[] => {
    let meetings = courseData["meetings"];
    let topMeeting = {
        "days": courseData["days"],
        "start_time": courseData["start_time"],
        "end_time": courseData["end_time"],
        "facility_description": courseData["facility_description"]
    }
    meetings.push(topMeeting);
    return meetings;
}

const getSectionData = (subject: string, catalogNumber: string): object[] => {
    const sectionData:object[] = [];
    const sectionElements = Array.from(document.getElementsByClassName(`${subject}-${catalogNumber}`)) as HTMLElement[];
    sectionElements.forEach((section) => {
        const dataCourse = section.getAttribute("data-course");
        const data = dataCourse ? JSON.parse(dataCourse) : null;
        if(data){
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
            })
        }
    })
    return sectionData;
}

const addToast = (header: string, message: string, successful: boolean) => {
    //Get template for the toast
    const toast = document.getElementById("success-toast")?.cloneNode(true) as HTMLElement;
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

const sendSectionNumbers = async (route: string, subject: string, sectionNumbers: string[]): Promise<boolean> => {
    let data:SettingsAPIData[] = [];
    //Send a POST request for each section number
    for(let i = 0; i < sectionNumbers.length; i++){
        try {
            const requestData = {
                "prefix": subject,
                "number": sectionNumbers[i],
            }
            data[i] = await postToLousList(route, requestData);
            if(data[i].result === "Failure"){
                return false;
            }
        }
        catch{
            return false;
        }
        
    }
    return data.length === sectionNumbers.length;
}

const sendSectionData = async (route: string, subject: string, sectionData: object[]):Promise<boolean> => {
    let data:SettingsAPIData[] = [];
    //Send a POST request for each section number
    for(let i = 0; i < sectionData.length; i++){
        try {
            data[i] = await postToLousList(route, sectionData[i]);
            if(data[i].result !== "Success"){
                return false;
            }
        }
        catch{
            return false;
        }
        
    }
    return data.length === sectionData.length;
}

const addClassToCart = (subject: string, catalogNumber: string) => {
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

}

const removeClassFromCart = (subject: string, catalogNumber: string) => {
    //Show remove button
    toggleAddRemoveButton(subject, catalogNumber, true);

    //Get section numbers for the course
    const sectionNumbers = getSectionNumbers(subject, catalogNumber);

    //Send a POST request with the section numbers, send to remove from cart
    sendSectionNumbers("remove-course-from-cart", subject, sectionNumbers)
        .then((successful) => {
            if (successful) {
                //Show success message
                const header = "<i class='bi bi-check-circle-fill me-1'></i><strong>Successfully deleted from cart</strong>";
                const message = `Successfully deleted ${subject} ${catalogNumber} from your cart.`;
                addToast(header, message, successful);
            }
            else {
                //Show failure message
                const header = "<i class=\"bi bi-exclamation-circle-fill me-1\"></i><strong>Unable to delete from cart</strong>";
                const message = `We were unable to delete ${subject} ${catalogNumber} from your cart.`;
                addToast(header, message, false);
            }
        });
}