import {
  askCvAssistant,
  initializeCvChat
} from "./cv-chat-engine.js";



document.addEventListener(
"DOMContentLoaded",
()=>{


const openButtons = [

  document.getElementById(
    "cv-chat-open"
  ),

  document.getElementById(
    "cv-chat-floating"
  )

];



const windowBox =
document.getElementById(
"cv-chat-window"
);



const close =
document.getElementById(
"cv-chat-close"
);



const form =
document.getElementById(
"cv-chat-form"
);



const input =
document.getElementById(
"cv-chat-input"
);



const messages =
document.getElementById(
"cv-chat-messages"
);



const status =
document.getElementById(
"cv-chat-status"
);





function addMessage(
text,
type
){


const div =
document.createElement(
"div"
);


div.className =
`cv-chat-message ${type}`;


div.textContent =
text;


messages.appendChild(div);


messages.scrollTop =
messages.scrollHeight;


return div;

}








openButtons.forEach(
button=>{


if(button){


button.onclick =
()=>{


windowBox.classList.add(
"active"
);


windowBox.setAttribute(
"aria-hidden",
"false"
);


};


}


}

);







close.onclick =
()=>{


windowBox.classList.remove(
"active"
);


windowBox.setAttribute(
"aria-hidden",
"true"
);


};









form.addEventListener(
"submit",
async(e)=>{


e.preventDefault();




const question =
input.value.trim();



if(!question)
return;





addMessage(
question,
"user"
);



input.value = "";





const loading =
addMessage(
"Loading AI...",
"ai"
);







try {



status.textContent =
"Initializing local AI model...";





await initializeCvChat(
(progress)=>{


if(progress.message){

status.textContent =
progress.message;

}


}

);







status.textContent =
"Searching CV knowledge...";







const result =
await askCvAssistant(
question,
{


onProgress:(progress)=>{


if(progress.message){

status.textContent =
progress.message;

}


}


}

);







loading.remove();




addMessage(
result.answer,
"ai"
);






}


catch(error){



console.error(
error
);



loading.remove();



addMessage(

"Error: " +
error.message,

"ai"

);



status.textContent =
"Error";


}





}

);




});