const dataFromDB = JSON.parse(
    document.currentScript.
    nextElementSibling.textContent
); // Parsing the JSON created and passed from Django Python with the dates and their respective start/end times

const noTimeAvailStr = "None available";
const timeAvailStr = "Select a time";
const startSel = document.getElementById("starttime"); // Const for selected start time
const endSel = document.getElementById("endtime"); // Const for selected end time


// Note: much of this code uses events...
window.onload = function() { // Function executes on the loading of the browser window
    let dateSel = ""; // Creating an empty string for the dateSel variable (global to all functions nested here)

    $("#datePicker").datepicker({ // Using jQuery's datepicker calendar
        dateFormat: 'yy-mm-dd', // ISO format
        minDate: '0d',
        maxDate: '6d',
        onSelect: function() { // When a date is selected, the function below will execute
            startSel.length = 1; // Resets the length of the start time dropdown options 
            endSel.length = 1; // Resets the length of the end time dropdown options
            dateSel = this.value;
            for(let start in dataFromDB[this.value]) // Filling the start time dropdown with start times respective of the date
                startSel.options[startSel.options.length] = new Option(timeDisplayed(start), start);

            startSel.options[0].innerHTML = endSel.options[0].innerHTML = 
                                                ((startSel.length === 1) ? noTimeAvailStr : timeAvailStr); // If no times are available for the date
        },
    });

    startSel.onchange = function() { // When a start time is selected, the function will execute
        endSel.length = 1; // Resets the length of the end time dropdown options
        let endTime = dataFromDB[dateSel][this.value];
        for(let i = 0; i < endTime.length; i++)
            endSel.options[endSel.options.length] = new Option(timeDisplayed(endTime[i]), endTime[i]);
    }       
}


// Function allows unix timestamps to be displayed in a human readable form for selection
// NOTE: Only worrying about times between 6:00am through 11:00pm
function timeDisplayed(theTime){
    const theDate = new Date(parseInt(theTime) * 1000); // Multiplied by 1000 to correct the unix timestamp value in Date()
    let displayHour = (theDate.getHours() > 12) ? theDate.getHours() - 12 : theDate.getHours();
    let displayMin = theDate.getMinutes();

    return `${displayHour}:${(displayMin == 30) ? "30" : "00"} 
            ${(theDate.getHours() >= 12) ? "P.M." : "A.M."}`;
}



// Using the DOM to get each field that needs to be possibly manipulated/changed

const firstNameField = document.getElementById("firstField");
const firstNameError = document.getElementById("firstError");

const lastNameField = document.getElementById("lastField");
const lastNameError = document.getElementById("lastError");

const emailField = document.getElementById("emailField");
const emailError = document.getElementById("emailError");

const form = document.querySelector("form");

const datePickError = document.getElementById("datePickError");
const startTimeError = document.getElementById("startTimeError");
const endTimeError = document.getElementById("endTimeError");

const regularExp = {
    email: RegExp(/^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/),
    name: RegExp(/^[A-za-z]{1,50}$/),
}

// Ordered list of fields and their error elements used by the DOM that come prior to the jQuery calendar
const typedFieldList = [firstNameField, lastNameField, emailField];
const typedErrorList = [firstNameError, lastNameError, emailError];

// Ordered list of fields and their error elements used by the DOM that come after the jQuery calendar
const otherFieldList =  [startSel, endSel];
const otherErrorList = [startTimeError, endTimeError];

// Specific error messages for name and email fields (repeat string for simplicity)
const errorMsgList = [
    "Please enter alphabetic characters only",
    "Please enter alphabetic characters only",
    "Please enter a proper email",
];

// Event listeners that recognize when they have been deselected and can be refocused on if submission is attempted and fails because of their field
firstNameField.addEventListener("blur", function() {blurFunction(errorMsgList[0], firstNameField, firstNameError)});
firstNameField.addEventListener("focus", focusFunction(regularExp.name, firstNameField, firstNameError));

lastNameField.addEventListener("blur", function() {blurFunction(errorMsgList[1], lastNameField, lastNameError)});
lastNameField.addEventListener("focus", focusFunction(regularExp.name, lastNameField, lastNameError));

emailField.addEventListener("blur", function() {blurFunction(errorMsgList[2], emailField, emailError)});
emailField.addEventListener("focus", focusFunction(regularExp.email, emailField, emailError));



form.addEventListener("submit", (event) => { // On the click of the submit button
    let prevent = false; // Boolean that if set to true, will prevent submission
    let theFocus = false; // Boolean that if false when first error is found, will be set equal to true (focuses on first input error field)

    // For loop specifically for the typed input fields (fields prior to jQuery calendar)
    for (let i = 0; i < typedFieldList.length; i++) {
        if(blurFunction(errorMsgList[i], typedFieldList[i], typedErrorList[i])) { // If blurFunction() returns true, error is found, prevent submission
            prevent = true;
            if(!theFocus) { // If this is the first error, set theFocus to true
                theFocus = true;
                typedFieldList[i].focus();
            }
        }
    }

    // For jQuery calendar
    if($("#datePicker").val() == "") { // If no value is selected for the calendar
        datePickError.textContent = "This field is required";
        prevent = true;
        if(!theFocus) {
            theFocus = true;
            $("#datePicker").focus();
        }
    }
    else{
        datePickError.textContent = ""; // Don't show an error otherwise
    }

     // For loop specifically for the other input fields (fields after jQuery calendar)
    for(let j = 0; j < otherFieldList.length; j++) {
        
        // If the currently selected value is "Select a time", i.e., no selection has been made
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


    if(prevent) // If the prevent Boolean is true, prevent submission
        event.preventDefault();
});


// Function executed upon deselection of input field
function blurFunction(theMsg, theField, theError){
    if(!theField.validity.valid) { // Checking the HTML validators for the input
        theField.style.borderColor = "red";
        theField.style.backgroundColor = "#fad4d4";
        if(!theField.value) { // Checking if the field is empty
            theError.innerHTML = "This field is required";
        }
        else{ // The field isn't empty but is improperly formatted
            theError.innerHTML = theMsg;
        }
        return true; // For the if statements in the submission event function
    }
    else{
        theField.style.backgroundColor = "white";
        return false; // For the if statements in the submission event function
    }
}


// Function that executes when a field has been selected (only for the "typedFields")
function focusFunction(expression, theField, theError) {
    
    // Event listener that what's for an input to occur before executing the function
    theField.addEventListener("input", function(){
        if(theField.value.match(expression)){
            theField.style.borderColor = "green"; // Turns green if the input matches the regex
            theError.innerHTML = "";
        }
        else{
            theField.style.borderColor = "black";
            theField.style.backgroundColor = "white";
        }
    });
}