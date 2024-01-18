slideShow(0);

function slideShow(indexVal) {
    let index = indexVal;
    const images = document.getElementsByClassName("statement-photo");
    
    for (let i = 0; i < images.length; i++)
        images[i].style.display = "none";
    
    index++;
    if (index > images.length)
        index = 1;
    
    images[index-1].style.display = "inline";

    setTimeout(slideShow.bind(null, index), 10000);
}