const dataFromDB = JSON.parse(
    document.currentScript.
    nextElementSibling.textContent
);

const startSel = document.getElementById("starttime");
const endSel = document.getElementById("endtime");


window.onload = function() {
    let dateSel = "";

    $("#datePicker").datepicker({
        dateFormat: 'yy-mm-dd',
        minDate: '0d',
        maxDate: '6d' ,
        onSelect: function() {
            startSel.length = 1;
            endSel.length = 1;
            dateSel = this.value;
            for(let start in dataFromDB[this.value])
                startSel.options[startSel.options.length] = new Option(timeDisplayed(start), start);
        },
    });

    startSel.onchange = function() {
        endSel.length = 1;
        let endTime = dataFromDB[dateSel][this.value];
        for(let i = 0; i < endTime.length; i++)
            endSel.options[endSel.options.length] = new Option(timeDisplayed(endTime[i]), endTime[i]);
    }
}



function timeDisplayed(theTime){
    const theDate = new Date(parseInt(theTime) * 1000);
    let displayHour = theDate.getHours();
    let displayMin = theDate.getMinutes();
    let hourPeriod = "A.M.";
    let extraZero = "";

    if(displayHour > 12) {
        displayHour -= 12;
        hourPeriod = "P.M.";
    }

    if(displayMin <= 9)
        extraZero = 0;

    return `${displayHour}:${extraZero}${displayMin} 
            ${hourPeriod}`;
}



const emailField = document.getElementById("emailField");
const emailError = document.getElementById("emailError");

const firstNameField = document.getElementById("firstField");
const firstNameError = document.getElementById("firstError");

const lastNameField = document.getElementById("lastField");
const lastNameError = document.getElementById("lastError");

const form = document.querySelector("form");

const datePickError = document.getElementById("datePickError");
const startTimeError = document.getElementById("startTimeError");
const endTimeError = document.getElementById("endTimeError");

const regularExp = {
    email: RegExp(/^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/),
    name: RegExp(/^[A-za-z]{1,50}$/),
}

const typedFieldList = [emailField, firstNameField, lastNameField];
const typedErrorList = [emailError, firstNameError, lastNameError];
const otherFieldList =  [startSel, endSel];
const otherErrorList = [startTimeError, endTimeError];
const errorMsgList = [
    "Please enter a proper email",
    "Please enter alphabetic characters only",
    "Please enter alphabetic characters only",
];


emailField.addEventListener("blur", function() {blurFunction(errorMsgList[0], emailField, emailError)});
emailField.addEventListener("focus", focusFunction(regularExp.email, emailField, emailError));

firstNameField.addEventListener("blur", function() {blurFunction(errorMsgList[1], firstNameField, firstNameError)});
firstNameField.addEventListener("focus", focusFunction(regularExp.name, firstNameField, firstNameError));

lastNameField.addEventListener("blur", function() {blurFunction(errorMsgList[2], lastNameField, lastNameError)});
lastNameField.addEventListener("focus", focusFunction(regularExp.name, lastNameField, lastNameError));



form.addEventListener("submit", (event) => {
    let prevent = false;
    let theFocus = false;
    // For the typed fields
    for (let i = 0; i < typedFieldList.length; i++) {
        if(blurFunction(errorMsgList[i], typedFieldList[i], typedErrorList[i])) {
            prevent = true;
            if(!theFocus) {
                theFocus = true;
                typedFieldList[i].focus();
            }
        }
    }

    // For jQuery calendar
    if($("#datePicker").val() == "") {
        datePickError.textContent = "This field is required";
        prevent = true;
        if(!theFocus) {
            theFocus = true;
            $("#datePicker").focus();
        }
    }
    else{
        datePickError.textContent = "";
    }

    // For
    for(let j = 0; j < otherFieldList.length; j++) {
        
        if(otherFieldList[j].options[otherFieldList[j].selectedIndex].value == "Select a time"){
            otherErrorList[j].innerHTML = "This field is required";
            prevent = true;
            if(!theFocus) {
                theFocus = true;
                otherFieldList[j].focus();
            }
        }
        else{
            otherErrorList[j].innerHTML = "";
        }
    }


    if(prevent)
        event.preventDefault();
});



function blurFunction(theMsg, theField, theError){
    if(!theField.validity.valid) {
        theField.style.backgroundColor = "red";
        if(!theField.value) { // Checking if the field is empty
            theError.innerHTML = "This field is required";
        }
        else{
            theError.innerHTML = theMsg;
        }
        return true;
    }
    else{
        theField.style.backgroundColor = "white";
        return false;
    }
}



function focusFunction(expression, theField, theError) {
    theField.addEventListener("input", function(){
        if(theField.value.match(expression)){
            theField.style.backgroundColor = "green";
            theError.innerHTML = "";
        }
        else{
            theField.style.backgroundColor = "white";
        }
    });
}