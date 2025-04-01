var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
const postToLousListAPI = (route, data) => __awaiter(this, void 0, void 0, function* () {
    try {
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
    }
    catch (error) {
        return { "result": "Failure" };
    }
});
const addToastToPage = (header, message, successful) => {
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
const setProfileImg = (profileImgFile) => {
    const profileImg = document.getElementById("profile-image");
    const profileImgValue = document.getElementById("profile-img-value");
    if (!profileImg || !profileImgValue) {
        return;
    }
    const path = `https://iili.io/${profileImgFile}`;
    profileImg.setAttribute("src", path);
    profileImgValue.setAttribute("value", profileImgFile);
};
const getProfileImgValue = () => {
    const profileImgInput = document.getElementById("profile-img-value");
    if (!profileImgInput) {
        return null;
    }
    return profileImgInput.value;
};
const updateNavProfile = (oldUsername, newUsername) => {
    const imgFilePath = getProfileImgValue();
    const navProfileImg = document.querySelector(`img[alt-text='profile-image-${oldUsername}']`);
    const username = document.getElementById("navbar-username");
    if (!imgFilePath || !navProfileImg || !username) {
        return;
    }
    navProfileImg.setAttribute("src", `https://iili.io/${imgFilePath}`);
    if (newUsername !== "") {
        username.textContent = newUsername;
    }
};
const getOldUserData = () => {
    const dataTag = document.getElementById("user-dict");
    if (!dataTag) {
        return null;
    }
    return JSON.parse(dataTag.value);
};
const updateUserDataValue = (userData) => {
    const dataTag = document.getElementById("user-dict");
    if (!dataTag) {
        return null;
    }
    dataTag.value = JSON.stringify(userData);
};
const updateBlankFields = () => {
    const accountForm = document.getElementById("account-form");
    if (!accountForm) {
        return;
    }
    const textInputs = [...accountForm.querySelectorAll("input[type='text']")];
    const userData = getOldUserData();
    if (!userData) {
        return;
    }
    textInputs.forEach((input) => {
        if (input.value === "") {
            input.value = userData[input.name];
        }
        else {
            userData[input.name] = input.value;
        }
    });
    updateUserDataValue(userData);
};
const getGradYear = (accountForm) => {
    const gradYear = accountForm.querySelector("select[name='grad_year']");
    if (!gradYear || gradYear.selectedOptions[0].textContent === "Select your graduation year") {
        return null;
    }
    return gradYear.selectedOptions[0].textContent;
};
const getFormData = () => {
    const formData = {
        first_name: "",
        last_name: "",
        username: "",
        major: "",
        grad_year: "",
        profile_pic: "yhRgWb.md.png",
    };
    const accountForm = document.getElementById("account-form");
    if (!accountForm) {
        return formData;
    }
    const textInputs = [...accountForm.querySelectorAll("input[type='text']")];
    const gradYear = getGradYear(accountForm);
    const profileImgFile = getProfileImgValue();
    textInputs.forEach((input) => {
        formData[input.name] = input.value;
    });
    formData.grad_year = gradYear || "";
    formData.profile_pic = profileImgFile || "yhRgWb.md.png";
    return formData;
};
const addSettingsToast = (newUsername, successful) => {
    const success = {
        header: `<i class="bi bi-gear-wide me-1"></i> Successfully Updated Account ${newUsername}`,
        message: "We updated your account successfully."
    };
    const failure = {
        header: `<i class="bi bi-gear-wide me-1"></i> Unable to Update Account Settings`,
        message: "We were unable to update your account. Please try again."
    };
    if (successful) {
        addToastToPage(success.header, success.message, successful);
    }
    else {
        addToastToPage(failure.header, failure.message, successful);
    }
};
const showUserError = (newUsername, alreadyExists) => {
    const userField = document.getElementById("username-input");
    if (!userField) {
        return;
    }
    if (!alreadyExists) {
        userField.setCustomValidity("");
    }
    else {
        userField.setCustomValidity(`User with username ${newUsername} already exists.`);
        userField.reportValidity();
    }
};
const updateAccountSettings = (oldUsername) => {
    const formData = getFormData();
    postToLousListAPI("update-account", formData)
        .then((result) => {
        if (result["result"] === "Success") {
            addSettingsToast(formData.username, true);
            updateNavProfile(oldUsername, formData.username);
            updateBlankFields();
            showUserError(formData.username, false);
        }
        else if (result["result"] === "User Already Exists") {
            showUserError(formData.username, true);
        }
        else {
            addSettingsToast(formData.username, false);
        }
    });
};
const removeValidity = () => {
    const userField = document.getElementById("username-input");
    if (!userField) {
        return;
    }
    userField.setCustomValidity("");
};
