window.onload = (event) => {
    addSearchTerms();
}

const addSearchTerms = () => {
    const recentBody = document.getElementById("recent-body");
    if (recentBody === null) {
        return;
    }
    recentBody.innerHTML = "";
    const key = "quickSearch";
    const termStr = localStorage.getItem(key);
    if (!termStr) {
        const msgElement = document.createElement("p");
        msgElement.innerText = "You haven't searched anything";
        recentBody.append(msgElement);
    }
    else {
        const terms = JSON.parse(termStr);
        terms.reverse().forEach((term: string) => {
            const link = document.createElement("a");
            const searchTerm = term.replace(" ", "+");
            link.classList.add("d-block", "mb-2")
            link.href = `search/?q=${searchTerm}`;
            link.innerText = term;
            recentBody.append(link);
        })
    }
}