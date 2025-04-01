type AccountFormData = {
    [key: string]: string;
    first_name: string;
    last_name: string;
    username: string;
    major: string;
    grad_year: string;
    profile_pic: string;
}

type SettingsAPIData = {
    result: string;
}

const postToLousListAPI = async (route: string, data: object):Promise<SettingsAPIData> => {
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

const addToastToPage = (header: string, message: string, successful: boolean) => {
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


const setProfileImg = (profileImgFile: string) => {
    const profileImg = document.getElementById("profile-image");
    const profileImgValue = document.getElementById("profile-img-value");
    if (!profileImg || !profileImgValue) {
        return;
    }
    const path = `https://iili.io/${profileImgFile}`;
    profileImg.setAttribute("src", path);
    profileImgValue.setAttribute("value", profileImgFile);
}

const getProfileImgValue = (): string | null => {
    const profileImgInput = document.getElementById("profile-img-value") as HTMLInputElement;
    if (!profileImgInput) {
        return null;
    }
    return profileImgInput.value;
}

const updateNavProfile = (oldUsername: string, newUsername: string) => {
    const imgFilePath = getProfileImgValue();
    const navProfileImg = document.querySelector(`img[alt-text='profile-image-${oldUsername}']`);
    const username = document.getElementById("navbar-username") as HTMLParagraphElement;
    if (!imgFilePath || !navProfileImg || !username) {
        return;
    }
    navProfileImg.setAttribute("src", `https://iili.io/${imgFilePath}`);
    if(newUsername !== ""){
        username.textContent = newUsername;
    }
}

const getOldUserData = () => {
    const dataTag = document.getElementById("user-dict") as HTMLInputElement;
    if(!dataTag){
        return null;
    }
    return JSON.parse(dataTag.value);
}

const updateUserDataValue = (userData: object) => {
    const dataTag = document.getElementById("user-dict") as HTMLInputElement;
    if(!dataTag){
        return null;
    }
    dataTag.value = JSON.stringify(userData);
}

const updateBlankFields = () => {
    const accountForm = document.getElementById("account-form") as HTMLFormElement;
    if (!accountForm) {
        return;
    }
    const textInputs: HTMLInputElement[] = [...accountForm.querySelectorAll("input[type='text']") as NodeListOf<HTMLInputElement>];
    const userData = getOldUserData();
    if(!userData){
        return;
    }
    textInputs.forEach((input) => {
        if(input.value === ""){
            input.value = userData[input.name];
        }
        else {
            userData[input.name] = input.value;
        }
    })
    updateUserDataValue(userData);
}

const getGradYear = (accountForm: HTMLFormElement): string | null => {
    const gradYear = accountForm.querySelector("select[name='grad_year']") as HTMLSelectElement;
    if (!gradYear || gradYear.selectedOptions[0].textContent === "Select your graduation year") {
        return null;
    }
    return gradYear.selectedOptions[0].textContent;
}

const getFormData = (): AccountFormData => {
    const formData: AccountFormData = {
        first_name: "",
        last_name: "",
        username: "",
        major: "",
        grad_year: "",
        profile_pic: "yhRgWb.md.png",
    }

    const accountForm = document.getElementById("account-form") as HTMLFormElement;
    if (!accountForm) {
        return formData;
    }
    const textInputs: HTMLInputElement[] = [...accountForm.querySelectorAll("input[type='text']") as NodeListOf<HTMLInputElement>];
    const gradYear = getGradYear(accountForm);
    const profileImgFile = getProfileImgValue();

    textInputs.forEach((input) => {
        formData[input.name] = input.value;
    })
    formData.grad_year = gradYear || "";
    formData.profile_pic = profileImgFile || "yhRgWb.md.png";
    return formData;
}

const addSettingsToast = (newUsername: string, successful: boolean) => {
    const success = {
        header: `<i class="bi bi-gear-wide me-1"></i> Successfully Updated Account ${newUsername}`,
        message: "We updated your account successfully."
    }

    const failure = {
        header: `<i class="bi bi-gear-wide me-1"></i> Unable to Update Account Settings`,
        message: "We were unable to update your account. Please try again."
    }

    if (successful) {
        addToastToPage(success.header, success.message, successful);
    }
    else {
        addToastToPage(failure.header, failure.message, successful);
    }
}

const showUserError = (newUsername: string, alreadyExists: boolean) => {
    const userField = document.getElementById("username-input") as HTMLInputElement;
    if(!userField){
        return;
    }
    if(!alreadyExists){
        userField.setCustomValidity("");
    }
    else {
        userField.setCustomValidity(`User with username ${newUsername} already exists.`);
        userField.reportValidity();
    }
}


const updateAccountSettings = (oldUsername: string) => {
    const formData = getFormData();
    postToLousListAPI("update-account", formData)
    .then((result) => {
        if(result["result"] === "Success"){
            addSettingsToast(formData.username, true);
            updateNavProfile(oldUsername, formData.username);
            updateBlankFields();
            showUserError(formData.username, false);
        }
        else if(result["result"] === "User Already Exists"){
            showUserError(formData.username, true);
        }
        else {
            addSettingsToast(formData.username, false);
        }
    })
}

const removeValidity = () => {
    const userField = document.getElementById("username-input") as HTMLInputElement;
    if(!userField){
        return;
    }
    userField.setCustomValidity("");
}