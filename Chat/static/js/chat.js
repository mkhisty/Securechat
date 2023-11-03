function renderhistory(datetimes,people,text,mediadata){
  for (i = 0; i < datetimes.length; i++) {
  console.log(datetimes,people,text,mediadata)
  recepient  = '"'
  mediatag = " "
  if (people[i]!==myname){
    recepient = '1" ';
    }  
    console.log("mediatag"+mediadata[i])
  if (typeof mediadata[i] !== 'undefined' ){
    var mdt = mediadata[i];
    console.log(mdt)
    mdt = mdt.slice(5,10);
    if (mdt=="image"){
    mediatag = " <br><img class ='textimage' src = '"+mediadata[i]+"'>" ; 
    } else if(mdt=="video"){
      mediatag = ' <br><video width="320" height="240"  class = "textvideo" controls><source src='+mediadata[i]+' type="video/mp4"></video>'
  }
  }else{
    mediatag = ""
  }
  if(  text[i] !== 'undefined' || mediadata[i] !== ' ' ) {
    $( 'div.message_holder' ).append( '<br><div class = "messagebox'+recepient+'> '+text[i]+mediatag+' <p class = datetime>'+datetimes[i]+' </p></div><br>' )
  }
}}
window.mediadata = " "
window.mysid = ""
function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}
window.myname = getParameterByName("usrnm")
function rendermedia(){
  var selectedFile = $('#fileinput')[0].files[0] ;
  var name = selectedFile.name
  var filereader = new FileReader();
  filereader.readAsDataURL(selectedFile);
  filereader.addEventListener("load",function(){
  mediadata = filereader.result;
  document.getElementById("filecover").innerHTML = name;
})}
var socket = io.connect('http://' + document.domain + ':' + location.port);

window.onload = function(){
    socket.emit( 'sessionstarted', {"usrnm":getParameterByName("usrnm"),"chatid":getParameterByName("chatid")} )
    socket.on( 'serversetup', function( sid ) {
    mysid = sid;
})
}

socket.on( 'connect', function() {
  var form = $( 'form' ).on( 'submit', function( event ) {
    event.preventDefault()
    document.getElementById("filecover").innerHTML = "Choose File";
    document.getElementById("fileinput").value = null;
    var user_input = $( 'input.messageentry' ).val();
    document.getElementById("messageentry").value="";
    console.log(user_input);
    var now = new Date();
    var minutes = now.getMinutes();
    var hours = now.getHours();
    if (minutes<10){minutes = "0"+minutes}
    if (hours>12){
      hours = hours-12;
      m = " pm";
    }else{ m = "am"}
    var datetime = (now.getMonth()+1)+"/"+now.getDate()+"/"+now.getFullYear()+"  "+hours+":"+minutes+m
    socket.emit( 'my event', {
      "user_name" : getParameterByName("usrnm"),
      "chatid"  :getParameterByName("chatid"),
      "message" : user_input,
      "mediadata":mediadata,
      "datetime":datetime
    } )
    $( 'input.message' ).val( '' ).focus()
    mediadata  = " "
    console.log("nm"+mediadata)
  } )
} )
socket.on( 'my response', function( msg ) {
  recepient='"'
  if (msg.user_name!==myname){
    recepient = '1" ';
    }  
  if (msg.mediadata!==" "){
    var mdt = msg.mediadata;
    mdt = mdt.slice(5,10);
    console.log(msg.message)
    if (mdt=="image"){
    mediatag = " <br><img class ='textimage' src = '"+msg.mediadata+"'>" ; 
    } else if(mdt=="video"){
      mediatag = ' <br><video width="320" height="240"  class = "textvideo" controls><source src='+msg.mediadata+' type="video/mp4"></video>'
  }
  }else{
    mediatag = ""
  }
  console.log(mediatag)
  if( typeof msg.user_name !== 'undefined' || msg.mediadata !== ' ' ) {
    $( 'div.message_holder' ).append( '<br><div class = "messagebox'+recepient+'> '+msg.message+mediatag+' <p class = datetime>'+msg.datetime+' </p></div><br>' )
  }
})
window.onbeforeunload = function(){
  socket.emit( 'sessionended', {
      "usrnm":getParameterByName("usrnm"),
      "chatid":getParameterByName("chatid"),
      "sid":mysid
  } )
}