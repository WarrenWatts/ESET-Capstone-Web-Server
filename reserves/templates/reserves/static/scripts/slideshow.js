/* Texas A&M University
** Electronic Systems Engineering Technology
** ESET-420 Engineering Technology Capstone II
** Author: Warren Watts
** File: slideshow.js
** --------
** Javascript code that utilizes the Document Object Model
** to hide and un-hide images in a set order after a certain
** period of time has elapsed. This (in-conjunction with CSS animation
** code) gives the effect of a slideshow.
*/


/* Constants */
const indexStart = 0; // Starting value for both index parameters in slideShow()
const delay = 10000; // Timer delay in milliseconds

slideShow(indexStart, indexStart);


/* Description:
** The slideshow() function is used to create the image slideshow effect seen on the home page.
**
** Parameters: 
** currIndexVal - the index value after incrementing in the previous function execution (current value).
** preIndexVal - the index value prior to incrementing in the previous function execution (previous value).
**
** Notes:
** This function does not have a return value in the normal sense, although it 
** does pass the index values (prior to and after incrementing) to a callback function 
** of itself. The function works by hiding the previously displayed image (all images are 
** set to "none" by default) and displays the current image. setTimeout() is then used to call the
** function after a set period of time.
*/
function slideShow(currIndexVal, prevIndexVal) { 
    const images = document.getElementsByClassName("statement-photo");

    if (currIndexVal > (images.length - 1))
    {
        currIndexVal = 0;
    }

    images[prevIndexVal].style.display = "none";
    // "inline-block" allows for a specified width and height to be set
    images[currIndexVal].style.display = "inline-block";

    prevIndexVal = currIndexVal;
    currIndexVal++;

    /* Notes:
    ** setTimeout() is an asynchronous Web API function. What this means is that once it is called, the function
    ** which its caller is in will continue/finish executing. The API specifically for this function will 
    ** set a timer, the time being specified by the variable delay. Once this timer has run its course, 
    ** it will place the callback function, the first parameter, in the event loop which will then be placed 
    ** on the stack when the stack is empty.
    ** The .bind() function allows a new function to be created, the null parameter stating that this function
    ** has global context.
    */
    setTimeout(slideShow.bind(null, currIndexVal, prevIndexVal), delay);
}