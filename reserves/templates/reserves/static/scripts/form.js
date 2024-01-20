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
    Dated : "Please use hyphenated ISO format",
    Email : "Please enter a proper email",
})

const RegExpEnum = Object.freeze({
    Email: RegExp(/^[A-Za-z\._\-0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/),
    Name: RegExp(/^[A-za-z]{1,50}$/),
    DateFormat : RegExp(/^(\d{4})-(\d{2})-(\d{2})$/),
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



class FormInputs 
{
    constructor(inputField, inputErr, errMsg) 
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
        let returnBool = true;

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
            
            returnBool = false;
        }
        else
        {
            blurInputField.style.borderColor = ColorsEnum.Black;
            blurInputField.style.backgroundColor = ColorsEnum.White;
            blurInputErr.innerHTML = emptyStr;
        }

        return returnBool;
    }

    onFocusValidator(focusInputField, focusInputErr) 
    {
        // Event listener that what's for an input to occur before executing the function
        focusInputField.addEventListener("input", () =>
        {
            this.formatBool = this.formatValidator(focusInputField);
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
                this.formatBool = this.onFocusValidator(this.inputField, this.inputErr);
                break;
            default: /* NOTE: Possibly add something to this default case!!! */
                break;
        }
    }
}



class TextInputs extends FormInputs 
{
    constructor(inputField, inputErr, errMsg, regEx) 
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
        this.inputField.removeEventListener("focus", this);
        this.selDate = emptyStr;
        let self = this;

        $("#datePicker").datepicker({ // Using jQuery's datepicker calendar
            dateFormat: "yy-mm-dd", // ISO format
            minDate: "0d",
            maxDate: "6d",
            onClose : function() {
                selStart.length = 1; // Resets the length of the start time dropdown options 
                selEnd.length = 1; // Resets the length of the end time dropdown options
                self.selDate = this.value;
    
                for (let i in dataFromDB[this.value]) 
                {
                    selStart.options[selStart.options.length] = new Option(unixToReadable(i), i);
                } // Filling the start time dropdown with start times respective of the date
    
                selStart.options[0].innerHTML = selEnd.options[0].innerHTML = 
                        ((selStart.length === 1) ? DropdownEnum.None : DropdownEnum.Select);
                self.formatValidator();
                self.emptyValueValidator();
                self.onBlurValidator(self.errMsg, self.inputField, self.inputErr);
            },
        });
    }

    formatValidator() 
    {
        if ($("#datePicker").val().match(RegExpEnum.DateFormat))
        {
            let dateCheck = new Date($("#datePicker").val());
            this.formatBool = (!isNaN(dateCheck)) ? true : false;
        }
        else
        {
            this.formatBool = false;
        }
    }

    emptyValueValidator()
    {
        this.emptyBool = (($("#datePicker")).val() === emptyStr) ? true : false;
    }
}



class DropdownInputs extends FormInputs 
{
    constructor(inputField, inputErr, errMsg)
    {
        super(inputField, inputErr, errMsg);
        this.inputField.removeEventListener("focus", this);
    }

    emptyValueValidator(dropdownField) 
    {
        if (dropdownField.options[dropdownField.selectedIndex].value === DropdownEnum.Select 
                || dropdownField.options[dropdownField.selectedIndex].value === DropdownEnum.None)
        {
            this.formatBool = false;
            this.emptyBool = true;
        }
        else
        {
            this.formatBool = true;
            this.emptyBool = false;
        }
    }
}



let formInputObjArr = [];

const textInputFields = [
    "firstField", 
    "lastField",
    "emailField",
]

const textErrFields = [
    "firstError", 
    "lastError",
    "emailError",
]

const textRegExArr = [
    RegExpEnum.Name,
    RegExpEnum.Name,
    RegExpEnum.Email
]

const textErrMsgArr = [
    ErrEnum.Name,
    ErrEnum.Name,
    ErrEnum.Email,
]

const ddInputFields = [
    "starttime",
    "endtime",
]

const ddErrFields = [
    "startTimeError",
    "endTimeError",
]


const selStart = document.getElementById(ddInputFields[0]); // Const for selected start time
const selEnd = document.getElementById(ddInputFields[1]); // Const for selected end time
const formElement = document.querySelector("form");

const dateInputField = "datePicker";
const dateErrField = "datePickError";

for (let i = 0; i < 3; i++)
{
    formInputObjArr.push(new TextInputs(textInputFields[i], textErrFields[i], textErrMsgArr[i], textRegExArr[i]));
}


formInputObjArr.push(new DatePickerInputs(dateInputField, dateErrField, ErrEnum.Dated));


for (let j = 0; j < 2; j++)
{
    formInputObjArr.push(new DropdownInputs(ddInputFields[j], ddErrFields[j], emptyStr));
}



selStart.onchange = function() 
{ // When a start time is selected, the function will execute
    selEnd.length = 1; // Resets the length of the end time dropdown options
    let endTime = dataFromDB[formInputObjArr[3].selDate][this.value];

    for (let i = 0; i < endTime.length; i++)
    {
        selEnd.options[selEnd.options.length] = 
                new Option(unixToReadable(endTime[i]), endTime[i]);
    }
}


formElement.addEventListener("submit", function(event) {
    let preventSubmitBool = false;
    let focusFirstBool = false;

    for (let i = 0; i < formInputObjArr.length; i++)
    {
        let formBool = formInputObjArr[i].onBlurValidator(
                        formInputObjArr[i].errMsg, 
                        formInputObjArr[i].inputField, 
                        formInputObjArr[i].inputErr
                    );
        
        if (!formBool)
        {
            preventSubmitBool = true;

            if (!focusFirstBool)
            {
                formInputObjArr[i].inputField.focus();
                focusFirstBool = true;
            }
        }
    }

    if (preventSubmitBool)
    {
        event.preventDefault();
    }
})

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