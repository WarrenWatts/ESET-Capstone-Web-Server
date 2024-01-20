/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: form.js
** --------
** Javascript code for the Form Page of the website.
** It provides a way to display the available dates and their
** respective start times and end times in addition to providing
** UI and input validation features.
*/


// Gets the dates, start times, and end times from Django Python
const dataFromDB = JSON.parse(document.currentScript.
                                    nextElementSibling.textContent);

const timeCorrection = 1000;
const emptyStr = "";

const MeridiemEnum = Object.freeze({
    Ante : "A.M.",
    Post : "P.M.",
})

const ErrEnum = Object.freeze({
    Required : "This field is required",
    Name : "Please enter alphabetic characters only",
})

const RegExpEnum = Object.freeze({
    Email: RegExp(/^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/),
    Name: RegExp(/^[A-za-z]{1,50}$/),
    DateFormat : RegExp(/^(?:\d{4})-(?:\d{2})-(?:\d{2})$/),

})

const DropdownEnum = Object.freeze({
    Select : "Select a time",
    None : "None available",
})

const MinutesEnum = Object.freeze({
    Zero : "00",
    Thirty : "30",
})

const ColorsEnum = Object.freeze({
    Red : "#ff0000",
    White : "#ffffff",
    BrightGreen : "#43e000",
    Black : "#000000",
    LightRed : "#fad4d4",
    LightGreen : "#dffad4",
})

const selStart = document.getElementById("starttime"); // Const for selected start time
const selEnd = document.getElementById("endtime"); // Const for selected end time



// Note: much of this code uses events...
// Function executes on the loading of the browser window
let selDate = emptyStr; // Creating an empty string for the selDate variable (global to all functions nested here)

selStart.onchange = function() 
{ // When a start time is selected, the function will execute
    selEnd.length = 1; // Resets the length of the end time dropdown options
    let endTime = dataFromDB[selDate][this.value];

    for (let i = 0; i < endTime.length; i++)
    {
        selEnd.options[selEnd.options.length] = 
                new Option(unixToReadable(endTime[i]), endTime[i]);
    }
}       


// Function allows unix timestamps to be displayed in a human readable form for selection
// NOTE: Only worrying about times between 6:00am through 11:00pm in increments of 30 minutes
function unixToReadable(timestampVal)
{
    const dateVal = new Date(parseInt(timestampVal) * timeCorrection); // Multiplied by 1000 to correct the unix timestamp value in Date()
    let hourVal24Clk = dateVal.getHours();

    let minuteVal = (dateVal.getMinutes() === 30) ? MinutesEnum.Thirty : MinutesEnum.Zero;

    let hourVal12Clk = (hourVal24Clk > 12) ? hourVal24Clk - 12 : hourVal24Clk;

    let meridiemVal = (hourVal24Clk >= 12) ? MeridiemEnum.Post : MeridiemEnum.Ante;
    
    return `${hourVal12Clk}:${minuteVal} ${meridiemVal}`;
}



class FormInputs 
{
    constructor (inputField, inputErr, errMsg) 
    {
        this.inputField = document.getElementById(inputField);
        this.inputErr = document.getElementById(inputErr);

        this.errMsg = errMsg;
        this.formatBool = false;
        this.emptyBool = true;

        this.inputField.addEventListener("focus", this);
        this.inputField.addEventListener("blur", this);
    }

    formatValidator(dateInputField){}

    emptyValueValidator(dateInputField){}

    onBlurValidator(errMessage, blurInputField, blurInputErr) 
    {
        if (!this.formatBool)
        { // Checking the HTML validators for the input
            blurInputField.style.outlineColor = ColorsEnum.Black;
            blurInputField.style.borderColor = ColorsEnum.Red;
            blurInputField.style.backgroundColor = ColorsEnum.LightRed;
    
            if (this.emptyBool)
            { // Checking if the field is empty
                blurInputErr.innerHTML = ErrEnum.Required;
            }
            else
            { // The field isn't empty but is improperly formatted
                blurInputErr.innerHTML = errMessage;
            }
        }
        else
        {
            blurInputField.style.borderColor = ColorsEnum.Black;
            blurInputField.style.backgroundColor = ColorsEnum.White;
        }
    }

    onFocusValidator(regularExp, focusInputField, focusInputErr) 
    {
        // Event listener that what's for an input to occur before executing the function
        focusInputField.addEventListener("input", () =>
        {
            this.formatValidator(focusInputField);
            if (this.formatBool)
            { // Turns green if the input matches the regex
                focusInputField.style.outlineColor = ColorsEnum.BrightGreen;
                focusInputField.style.backgroundColor = ColorsEnum.White;
                focusInputErr.innerHTML = emptyStr;
            }
            else
            { 
                focusInputField.style.outlineColor = ColorsEnum.Black;
                focusInputField.style.backgroundColor = ColorsEnum.White;
            }
        });
    }

    handleEvent (e) 
    {
        switch (e.type) 
        {
            case "blur":
                this.formatValidator(this.inputField)
                this.emptyValueValidator(this.inputField)
                this.onBlurValidator(this.errMsg, this.inputField, this.inputErr);
                break;
            case "focus":
                this.formatBool = this.onFocusValidator(this.regEx, this.inputField, this.inputErr);
                break;
            default: /* NOTE: Possibly add something to this default case!!! */
                break;
        }
    }
}



class TextInputs extends FormInputs 
{
    constructor(inputField, inputErr, regEx, errMsg) 
    {
        super(inputField, inputErr, errMsg);
        this.regEx = regEx;
    }

    formatValidator(textInputField)
    {
        this.formatBool = (textInputField.value.match(this.regEx)) ? true : false;
    }

    emptyValueValidator(textInputField)
    {
        this.emptyBool = (textInputField.value) ? false : true;
    }
}



class DatePickerInputs extends FormInputs 
{
    constructor(inputField, inputErr, errMsg) 
    {
        super(inputField, inputErr, errMsg);
        this.inputField.removeEventListener("blur", this);
        $("#datePicker").datepicker({ // Using jQuery's datepicker calendar
            dateFormat: "yy-mm-dd", // ISO format
            minDate: "0d",
            maxDate: "6d",
            onSelect: function() 
            { // When a date is selected, the function below will execute
                selStart.length = 1; // Resets the length of the start time dropdown options 
                selEnd.length = 1; // Resets the length of the end time dropdown options
                selDate = this.value;
    
                for (let i in dataFromDB[this.value]) 
                {
                    selStart.options[selStart.options.length] = new Option(unixToReadable(i), i);
                } // Filling the start time dropdown with start times respective of the date
    
                selStart.options[0].innerHTML = selEnd.options[0].innerHTML = 
                        ((selStart.length === 1) ? DropdownEnum.None : DropdownEnum.Select);
            },
            onClose : () => {
                this.formatValidator(this.inputField);
                this.emptyValueValidator(this.inputField);
                this.onBlurValidator(this.errMsg, this.inputField, this.inputErr);
            },
        });
    }

    formatValidator(dateInputField) 
    {
        if ($("#datePicker").val() === RegExpEnum.DateFormat)
        {
            let dateCheck = new Date($("#datePicker").val());

            this.formatBool = (!isNaN(dateCheck)) ? true : false;
        }
        else
        {
            this.formatBool = false;
        }
    }

    emptyValueValidator(dateInputField)
    {
        this.emptyBool = (($("#datePicker")).val() === emptyStr) ? false : true;
    }

    handleEvent (e) 
    {
        switch (e.type) 
        {
            case "focus":
                this.formatBool = this.onFocusValidator(this.regEx, this.inputField, this.inputErr);
                break;
            default: /* NOTE: Possibly add something to this default case!!! */
                break;
        }
    }
}

// Using the DOM to get each field that needs to be possibly manipulated/changed

const firstNameField = "firstField";
const firstNameErr = "firstError";
const firstErrorMsg = "Bruh Momento";

const dateField = "datePicker";
const dateErr = "datePickError";
const dateErrorMsg = "Bruh Moment";

let testCase = new TextInputs(firstNameField, firstNameErr, RegExpEnum.Name, ErrEnum.Name);


let testCase2 = new DatePickerInputs(dateField, dateErr, dateErrorMsg);


/*const lastNameField = document.getElementById("lastField");
const lastNameErr = document.getElementById("lastError");

const emailField = document.getElementById("emailField");
const emailErr = document.getElementById("emailError");

const formElement = document.querySelector("form");

const DATE_PICKER_ERR = document.getElementById("datePickError");
const START_TIME_ERR = document.getElementById("startTimeError");
const END_TIME_ERR = document.getElementById("endTimeError");

// Ordered list of fields and their error elements used by the DOM that come prior to the jQuery calendar
const KEY_INPUT_FIELD = [firstNameField, lastNameField, emailField];
const KEY_INPUT_ERR = [firstNameErr, lastNameErr, emailErr];

// Ordered list of fields and their error elements used by the DOM that come after the jQuery calendar
const SEL_INPUT_FIELD =  [selStart, selEnd];
const SEL_INPUT_ERR = [START_TIME_ERR, END_TIME_ERR];

// Specific error messages for name and email fields (repeat string for simplicity)
const ERR_MESSAGES = [
    "Please enter alphabetic characters only",
    "Please enter alphabetic characters only",
    "Please enter a proper email",
];

// Event listeners that recognize when they have been deselected and can be refocused on if submission is attempted and fails because of their field
firstNameField.addEventListener("blur", function() {onBlurValidator(ERR_MESSAGES[0], firstNameField, firstNameErr)});
firstNameField.addEventListener("focus", onFocusValidator(RegExpEnum.Name, firstNameField, firstNameErr));

lastNameField.addEventListener("blur", function() {onBlurValidator(ERR_MESSAGES[1], lastNameField, lastNameErr)});
lastNameField.addEventListener("focus", onFocusValidator(RegExpEnum.Name, lastNameField, lastNameErr));

emailField.addEventListener("blur", function() {onBlurValidator(ERR_MESSAGES[2], emailField, emailErr)});
emailField.addEventListener("focus", onFocusValidator(RegExpEnum.Email, emailField, emailErr));*/



/*formElement.addEventListener("submit", (event) => { // On the click of the submit button
    let prevent = false; // Boolean that if set to true, will prevent submission
    let theFocus = false; // Boolean that if false when first error is found, will be set equal to true (focuses on first input error field)

    // For loop specifically for the typed input fields (fields prior to jQuery calendar)
    for (let i = 0; i < KEY_INPUT_FIELD.length; i++) 
    {
        if (onBlurValidator(ERR_MESSAGES[i], KEY_INPUT_FIELD[i], KEY_INPUT_ERR[i])) 
        { // If onBlurValidator() returns true, error is found, prevent submission
            prevent = true;

            if (!theFocus) 
            { // If this is the first error, set theFocus to true
                theFocus = true;
                KEY_INPUT_FIELD[i].focus();
            }
        }
    }

    // For jQuery calendar
    if ($("#datePicker").val() === emptyStr) { // If no value is selected for the calendar
        DATE_PICKER_ERR.textContent = ErrEnum.Required;
        prevent = true;
        if (!theFocus) 
        {
            theFocus = true;
            $("#datePicker").focus();
        }
    }
    else
    {
        DATE_PICKER_ERR.textContent = emptyStr; // Don't show an error otherwise
    }

     // For loop specifically for the other input fields (fields after jQuery calendar)
    for (let j = 0; j < SEL_INPUT_FIELD.length; j++) 
    {
        
        // If the currently selected value is "Select a time", i.e., no selection has been made
        if (SEL_INPUT_FIELD[j].options[SEL_INPUT_FIELD[j].selectedIndex].value === DropdownEnum.Select) //CHANGED
        { 
            SEL_INPUT_ERR[j].innerHTML = ErrEnum.Required;
            prevent = true;

            if (!theFocus) 
            {
                theFocus = true;
                SEL_INPUT_FIELD[j].focus();
            }
        }
        else
        {
            SEL_INPUT_ERR[j].innerHTML = emptyStr;
        }
    }


    if (prevent)
    {
        event.preventDefault();
    } // If the prevent Boolean is true, prevent submission
});*/


// Function executed upon deselection of input field
/* function onBlurValidator(errMessage, blurInputField, blurInputErr)
{
    if (!blurInputField.validity.valid) 
    { // Checking the HTML validators for the input
        blurInputField.style.borderColor = ColorsEnum.Red;
        blurInputField.style.backgroundColor = ColorsEnum.LightRed;

        if (!blurInputField.value) 
        { // Checking if the field is empty
            blurInputErr.innerHTML = ErrEnum.Required;
        }
        else
        { // The field isn't empty but is improperly formatted
            blurInputErr.innerHTML = errMessage;
        }

        return true; // For the if statements in the submission event function
    }
    else
    {
        blurInputField.style.backgroundColor = ColorsEnum.White;
        return false; // For the if statements in the submission event function
    }
}


// Function that executes when a field has been selected (only for the "typedFields")
function onFocusValidator(regularExp, focusInputField, focusInputErr) 
{
    // Event listener that what's for an input to occur before executing the function
    focusInputField.addEventListener("input", function()
    {
        if (focusInputField.value.match(regularExp))
        {
            focusInputField.style.borderColor = ColorsEnum.Green; // Turns green if the input matches the regex
            focusInputErr.innerHTML = emptyStr;
        }
        else
        {
            focusInputField.style.borderColor = ColorsEnum.Black;
            focusInputField.style.backgroundColor = ColorsEnum.White;
        }
    });
} */