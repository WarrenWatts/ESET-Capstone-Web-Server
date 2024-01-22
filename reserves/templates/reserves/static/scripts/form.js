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


/* NOTE:
** Any conditional operators used were due to the trivial nature of their
** statement in addition to keeping with the DRY principle.
*/


/* Variable Naming Abbreviations Legend:
**
** DB - database
** str - string
** regEx || regExp - regular expression
** obj - object
** arr - array
** err - error
** msg - message
** sel - select
** Bool - boolean
** dd - dropdown
** val - value
** 24Clk - 24 hour clock
** 12Clk - 12 hour clock
*/

/* Function Prefix Legend:
**
** h - handle
** d - display
*/


/* Constants */

// Gets the dates, start times, and end times from Django Python
const dataFromDB = JSON.parse(document.currentScript.
                                    nextElementSibling.textContent);
const emptyStr = "";

/* Notes:
** Below are a number of JavaScript objects
** made to function as Enums (to an extent).
** This was done in order to follow the DRY
** principle, but also to avoid inserting 
** "magic" values or numbers.
*/
const MeridiemEnum = Object.freeze({
    Ante : "A.M.",
    Post : "P.M.",
})

// Enum for the an input fields specific formatting error message
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

// Enum for the two default dropdown select options
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


/* Notes:
** Is the only non-const global variable.
** Is the array for form input objects.
*/
let formInputObjArr = [];


/* Notes:
** Below are a number of arrays and variables
** that contain the ids of HTML elements and 
** other important information necessary to
** create each of the input objects for the form.
** Each input field on the form will always be in
** the same order, so arrays of the like make sense.
*/
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

const dateInputField = "datePicker";
const dateErrField = "datePickError";

const ddInputFields = [
    "starttime",
    "endtime",
]

const ddErrFields = [
    "startTimeError",
    "endTimeError",
]

// Const for selected start time
const selStart = document.getElementById(ddInputFields[0]);

// Const for selected end time
const selEnd = document.getElementById(ddInputFields[1]);

const formElement = document.querySelector("form");




/* Description:
** FormInputs is the parent class for all form input child/sub classes.
** It provides a number of base variables, event listeners, and functions
** that will be utilized by each child class.
**
** Parameters:
** inputField - the id of the input field in the page's HTML
** inputErr - the id of the input's error field in the page's HTML
** errMsg - the error message associated with incorrect formatting for this field
**
** Notes:
** The "focus" event occurs when someone selects the input field. The "blur" event occurs
** when someone clicks off of an input field.
*/
class FormInputs 
{
    constructor(inputField, inputErr, errMsg) 
    {
        this.inputField = document.getElementById(inputField);
        this.inputErr = document.getElementById(inputErr);

        this.errMsg = errMsg;
        this.formatBool = false; // Initially empty, so the input cannot have the correct format
        this.emptyBool = true; // Initially empty

        this.inputField.addEventListener("focus", this);
        this.inputField.addEventListener("blur", this);
    }


    /* Description:
    ** The hFormatValidator() function here is simply a placeholder/base function
    ** that is replaced by each child classes' own hEmptyValValidator()
    ** function. Each child class will use this function to verify that their input
    ** is properly formatted in their own unique way. The this.formatBool variable
    ** is then changed accordingly to signify the status of the input field's format.
    **
    ** Parameters:
    ** formInputField - takes the this.inputField variable to check the specified input's format
    **
    ** Notes:
    ** This function does not have a return value in the normal sense, but instead changes
    ** the object's this.emptyBool variable value accordingly.
    */
    hFormatValidator(formInputField){}


    /* Description:
    ** The hEmptyValValidator() function here is simply a placeholder/base function
    ** that is replaced by each child classes' own hEmptyValValidator()
    ** function. Each child class will use this function to check whether or not their input
    ** is empty in their own unique way. The this.emptyBool variable is then changed accordingly 
    ** to signify the state of the input field.
    **
    ** Parameters:
    ** formInputField - takes the this.inputField variable to check the if the input is empty
    **
    ** Notes:
    ** This function does not have a return value in the normal sense, but instead changes
    ** the object's this.formatBool variable value accordingly.
    */
    hEmptyValValidator(formInputField){}


    /* Description:
    ** The dOnBlurValidator() function is used to display (via the Document Object Model)
    ** whether or not the user has correctly provided their information into a specified 
    ** input field. (Is manipulating the UI.) Since all field inputs on the form will do this, 
    ** this function was designed in a way that it only has to rely on the Boolean variables 
    ** this.formatBool and this.emptyBool (given to each class and sub-class object) to work as intended. 
    **
    ** Parameters:
    ** blurInputField - takes the this.inputField variable to change the styling accordingly
    ** blurInputErr - takes the this.inputErr variable to change the error field text accordingly
    ** errMessage - takes the this.errMsg variable to substitute the error message for wrong formatting
    **
    ** Return:
    ** Will return a Boolean value of true if this.formatBool is also true, otherwise it returns false.
    **
    ** Notes:
    ** The return value here is used specifically for validation (both visual and non-visual) when
    ** form submission is attempted.
    */
    dOnBlurValidator(blurInputField, blurInputErr, errMessage) 
    {
        let returnBool = true;

        if (!this.formatBool) // The field is improperly formatted
        {
            blurInputField.style.outlineColor = ColorsEnum.Black; // Outline for the selector
            blurInputField.style.borderColor = ColorsEnum.Red;
            blurInputField.style.backgroundColor = ColorsEnum.LightRed;
    
            if (this.emptyBool) // The field is empty
            {
                blurInputErr.innerHTML = ErrEnum.Required;
            }
            else // The field isn't empty but is improperly formatted
            {
                blurInputErr.innerHTML = errMessage;
            }
            
            returnBool = false;
        }
        else // The field is properly formatted
        {
            blurInputField.style.borderColor = ColorsEnum.Black;
            blurInputField.style.backgroundColor = ColorsEnum.White;
            blurInputErr.innerHTML = emptyStr;
        }

        return returnBool;
    }


    /* Description:
    ** The dOnFocusValidator() function is one that activates on selection of an input field.
    ** Once the input field has been selected, another event listener is added to see if
    ** the input field has received any input. If input is received, it checks if the current input
    ** text matches the format or not for the input field. It uses the DOM to signify to the user if their
    ** input is correct by highlighting the textbox is green.
    **
    ** Parameters:
    ** focusInputField - takes the this.inputField variable to change the styling accordingly
    ** focusInputErr - takes the this.inputErr variable to change the error field text accordingly
    **
    ** Notes:
    ** This function ended up only being utilized, in this case, for the TextInputs sub-class.
    ** This is due in one part because it is not necessary for the date or dropdown selectors,
    ** and in another part because of the errors it was creating.
    */
    dOnFocusValidator(focusInputField, focusInputErr) 
    {
        // Event listener that waits for an input to occur before executing the function
        focusInputField.addEventListener("input", () =>
        {
            let checkBool = this.hFormatValidator(focusInputField);
            if (checkBool)
            {
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


    /* Description of function
    ** This function simply handles the events from the event listeners as they come in.
    ** It does this by making use of a switch statement.
    **
    ** Parameters:
    ** e - the specific event from the event listener
    **
    ** Notes:
    ** Although each child class has this, they can simply remove their event listeners
    ** in their constructors (if they don't need the event or it is detrimental to them),
    ** while still allowing their code to function as intended. If there are no events,
    ** then events don't need to be handled.
    */
    hEvent (e) 
    {
        switch (e.type) 
        {
            case "blur":
                this.hFormatValidator(this.inputField)
                this.hEmptyValValidator(this.inputField)
                this.dOnBlurValidator(this.inputField, this.inputErr, this.errMsg);
                break;
            case "focus":
                this.formatBool = this.dOnFocusValidator(this.inputField, this.inputErr);
                break;
            default:
                break;
        } /* End of switch statement */
    }
}




/* Description:
** Another child class of the FormInputs parent class, the TextInputs class
** was created to utilize its own variations of the validator functions that differ
** from the other child classes. Validation here occurs through the use of regular
** expressions according to the text field's type as well as through empty string
** comparison.
**
** Parameters:
** *Are the same as the parent class except...*
** regEx - the regular expression associated with the text field to check its format
**
** Notes:
** This sub-class most aligns with the base format setup in the FormInputs parent class.
*/
class TextInputs extends FormInputs 
{
    constructor(inputField, inputErr, errMsg, regEx) 
    {
        super(inputField, inputErr, errMsg);
        this.regEx = regEx;
    }

    /* Notes:
    ** This hFormatValidator has a return function in order to be handled by the
    ** dOnFocusValidator()'s anonymous function. Otherwise, the value of
    ** this.formatBool cannot be utilized. Since this is a TextInputs specific
    ** problem and no other sub-classes utilize the dOnFocusValidator() function,
    ** the return value is being placed here instead of FormInputs.
    */
    hFormatValidator(textInputField)
    {
        this.formatBool = (textInputField.value.match(this.regEx)) ? true : false;

        return this.formatBool;
    }


    hEmptyValValidator(textInputField)
    {
        this.emptyBool = (textInputField.value) ? false : true;
    }
}




/* Description:
** Another child class of the FormInputs parent class, the DatePickerInputs class
** was created to utilize its own variations of the validator functions that differ
** from the other child classes. However, this sub-class differs from all the others
** in that it does not utilize base HTML structures, but instead jQuery. Validation 
** here occurs by checking if an input has been formatted using ISO standards and
** after de-selecting the input field, if there is any text in the field.
**
** Parameters:
** *Are the same as the parent class*
**
** Notes:
** Since this sub-class is based around the jQuery Datepicker element,
** both the "blur" and "focus" events were removed from the class in the constructor.
** This is due to the jQuery element's inability to function properly with the regular
** JavaScript event listeners.
*/
class DatePickerInputs extends FormInputs 
{
    constructor(inputField, inputErr, errMsg) 
    {
        super(inputField, inputErr, errMsg);
        this.inputField.removeEventListener("blur", this);
        this.inputField.removeEventListener("focus", this);
        this.selDate = emptyStr;
        let self = this;


        /* Description:
        ** This is the jQuery Datepicker element. It is being declared
        ** here in the constructor because it can only be called once,
        ** otherwise it resets itself and all its previous parameters.
        ** Inside this declaration is an anonymous function that executes
        ** once the input for the DatePicker element has been closed/
        ** de-selected. In doing this, it will fill out start time dropdown
        ** according to the date, as well as verify the format of the date.
        **
        ** Parameters:
        ** dateFormat - specifies the input format for the date (currently using ISO format)
        ** minDate - the minimum selectable date (set to the current day)
        ** maxDate - the maximum selectable date (set to have 7 selectable days)
        ** onClose : function() - the anonymous function discussed in the description
        **
        ** Notes:
        ** The hFormatValidator(), hEmptyValValidator(), and dOnBlurValidator() functions are
        ** still utilized and checked in the anonymous function (done at the function's end).
        ** This anonymous function also considers the possibility of no times being available
        ** for a selected day due to them all being taken.
        */
        $("#datePicker").datepicker({
            dateFormat: "yy-mm-dd",
            minDate: "0d",
            maxDate: "6d",
            onClose : function() {
                
                // Resets the length of the dropdown options (frees memory)
                selStart.length = 1; 
                selEnd.length = 1;

                self.selDate = this.value;
    
                for (let i in dataFromDB[this.value]) 
                {
                    selStart.options[selStart.options.length] = new Option(hUnixToReadable(i), i);
                }
                
                /* Notes:
                ** If there are no start times AT ALL, then there cannot be any end times either.
                ** Therefore, we can assign the result from this conditional operator to both 
                ** the selStart and selEnd option text fields. 
                */
                selStart.options[0].innerHTML = selEnd.options[0].innerHTML = 
                        ((selStart.length === 1) ? DropdownEnum.None : DropdownEnum.Select);
                
                self.hFormatValidator();
                self.hEmptyValValidator();
                self.dOnBlurValidator(self.inputField, self.inputErr, self.errMsg);
            },
        });
    }


    /* Notes:
    ** No parameters used in either the hFormatValidator() or hEmptyValValidator() functions
    ** This works because the event listeners for both "blur" and "focus" were removed since 
    ** this is a jQuery object that has its own set of event listener values.
    */
    hFormatValidator() 
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


    hEmptyValValidator()
    {
        this.emptyBool = (($("#datePicker")).val() === emptyStr) ? true : false;
    }
}




/* Description:
** Another child class of the FormInputs parent class, the DropdownInputs class
** was created to utilize its own variations of the validator functions that differ
** from the other child classes. This class utilizes only the hEmptyValValidator()
** function to validate the field's input.
**
** Parameters:
** *Are the same as the parent class*
**
** Notes:
** The "focus" event and the dOnFocusValidator() function are not needed for this class.
** This is why the event listener is removed for "focus" in the constructor.
*/
class DropdownInputs extends FormInputs 
{
    constructor(inputField, inputErr, errMsg)
    {
        super(inputField, inputErr, errMsg);
        this.inputField.removeEventListener("focus", this);
    }

    
    /* Notes:
    ** Checks if the current option selected after the cursor de-selects the dropdown is either 
    ** "Select a time" or "None Available". If this is the case, then the format is incorrect 
    ** and the dropdown selection can be said to be empty since nothing of true value has 
    ** been selected.
    ** The hFormatValidator() function is not utilized in this sub-class since the dropdown 
    ** selections are already formatted (typed input is not required and isn't possible 
    ** without manipulating the HTML).
    */
    hEmptyValValidator(dropdownField) 
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



/* Notes:
** Although not a function, displayed below is the code for
** the initialization of each FormInput object through their
** designated sub-classes. Since the form will ALWAYS be in the
** same order, each object is pushed into the formInputObjArr array
** in this fashion.
*/
for (let i = 0; i < 3; i++)
{
    formInputObjArr.push(new TextInputs(
                        textInputFields[i], 
                        textErrFields[i], 
                        textErrMsgArr[i], 
                        textRegExArr[i],
                    ));              
}


formInputObjArr.push(new DatePickerInputs(
                        dateInputField, 
                        dateErrField, 
                        ErrEnum.Dated,
                    ));


for (let j = 0; j < 2; j++)
{
    formInputObjArr.push(new DropdownInputs(
                            ddInputFields[j], 
                            ddErrFields[j], 
                            emptyStr,
                        ));
}



/* Description:
** An anonymous function connected to an onchange event listener,
** this function fills out the dropdown menu of the selEnd (end time) 
** dropdown field with option values according to the currently selected 
** selStart (start time) option value. Each time a new start time is 
** selected, the function resets the end time options.
**
** Parameters:
** No parameters are present, however, an onchange event
** (selection in the dropdown made) must occur for this function 
** to be triggered.
**
** Notes:
** Using formInputObjArr[3] directly here since the date object
** will ALWAYS be the fourth value in the array of form inputs.
*/
selStart.onchange = function() 
{
    // Resets the length of the end time dropdown options (frees memory)
    selEnd.length = 1;

    // "this" being the currently selected selStart value
    let endTime = dataFromDB[formInputObjArr[3].selDate][this.value];

    for (let i = 0; i < endTime.length; i++)
    {
        selEnd.options[selEnd.options.length] = 
                new Option(hUnixToReadable(endTime[i]), endTime[i]);
    }
}



/* Description:
** An anonymous function on an event listener for a "submit" event,
** this function verifies whether or not all the fields have been
** filled out and filled out properly (properly formatted). If not,
** the incorrect fields are displayed using the dOnBlurValidator()
** function. The first incorrect field in the form will be "focused",
** meaning your cursor is within said field.
**
** Parameters:
** event - occurs when a "submit" event is registered
**
** Notes:
** The default that we are preventing, in the case of an error,
** is the submission of the form.
** This function makes use of the dOnBlurValidator() function's
** return values in order to verify whether or not the form is
** ready for submission.
*/
formElement.addEventListener("submit", function(event) 
{
    let preventSubmitBool = false;
    let focusFirstBool = false;

    for (let i = 0; i < formInputObjArr.length; i++)
    {
        let formBool = formInputObjArr[i].dOnBlurValidator( 
                        formInputObjArr[i].inputField, 
                        formInputObjArr[i].inputErr,
                        formInputObjArr[i].errMsg,
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
});



/* Description:
** The hUnixToReadable() function allows unix timestamps to be 
** displayed in a human readable form for selection.
**
** Parameters:
** timeStampVal - the unix timestamp value sent to the function
**
** Return:
** returns a string of the time in the format... 9:30 P.M.
**
** Notes:
** We are ONLY concerned with times between 6:00am and 11:00pm 
** in increments of 30 minutes, which is why this function works
** properly with such simplicity.
*/
function hUnixToReadable(timestampVal)
{
    /* Notes:
    ** Multiplied by the timeCorrection variable, which is a value of 1000.
    ** This is done because the unix timestamp values in Date() are measured
    ** in milliseconds instead of seconds like normal unix timestamp values.
    */
    const timeCorrection = 1000;
    const dateVal = new Date(parseInt(timestampVal) * timeCorrection);
    
    // .getHours() uses a 24 hour clock, i.e., values from 0 to 23.
    let hourVal24Clk = dateVal.getHours();

    let minuteVal = (dateVal.getMinutes() === 30) ? MinutesEnum.Thirty : MinutesEnum.Zero;

    let hourVal12Clk = (hourVal24Clk > 12) ? hourVal24Clk - 12 : hourVal24Clk;

    let meridiemVal = (hourVal24Clk >= 12) ? MeridiemEnum.Post : MeridiemEnum.Ante;
    
    return `${hourVal12Clk}:${minuteVal} ${meridiemVal}`;
}