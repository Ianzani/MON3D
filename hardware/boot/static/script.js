function checkSSID() {
   var ssid = document.getElementById("ssid").value;
   var errorMessage = document.getElementById("error-message");

   if (ssid.trim() === "") {
       errorMessage.innerText = "Campo obrigatório.";
       return false;
   } else {
      errorMessage.innerText = "";
   }
}

function triggerCopy() {   
   var tempInput = document.createElement("input");
   tempInput.value = document.getElementById("pwsd1").value;
   document.body.appendChild(tempInput);
   tempInput.select();
   document.execCommand("copy");
   document.body.removeChild(tempInput);
 }