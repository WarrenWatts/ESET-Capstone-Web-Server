const dataFromDB = JSON.parse(
    document.currentScript.
    nextElementSibling.textContent
);



window.onload = function() {
    let dateSel = "";
    let startSel = document.getElementById("starttime");
    let endSel = document.getElementById("endtime");

        $("#datePicker").datepicker({
            dateFormat: 'yy-mm-dd',
            defaultDate: '0d',
            minDate: '0d',
            maxDate: '6d' ,
            onSelect: function() {
                startSel.length = 1;
                endSel.length = 1;
                dateSel = this.value;
                for(let start in dataFromDB[this.value])
                    startSel.options[startSel.options.length] = new Option(timeDisplayed(start), start);
            }
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