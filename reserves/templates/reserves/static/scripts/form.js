const data = JSON.parse(
    document.currentScript.
    nextElementSibling.textContent
);

function main() {
    let dateSel = document.getElementById("calendardate");
    console.log("here");
    dateSel.setAttribute("min", data[0]);
    let startSel = document.getElementById("starttime");
    let endSel = document.getElementById("endtime");

}

