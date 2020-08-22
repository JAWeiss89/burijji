console.log('app.js is connected');

function getRandomChatCode() {
    let chatcode = "";
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    for (let i=0; i<11; i++) {
        if (i==3 || i==7) {
            chatcode = chatcode + "-"
        } else {
            chatcode = chatcode + letters[Math.floor(Math.random()*12)]
        }
    }
    return chatcode;
}

// let newMeetingBtn = document.querySelector("#new-meeting");
// let chatroomCodeField = document.querySelector("#chatroom-code-input")

// newMeetingBtn.addEventListener('click', function() {
//     chatroomCodeField.value=getRandomChatCode();
// })


// let joinForm = document.querySelector("#join-meeting-form");

// joinForm.addEventListener("submit", function(event) {
//     event.preventDefault();
//     // Add meeting to list
//     let li = document.createElement('li');
//     li.setAttribute('meetingcode', chatroomCodeField.value);
//     li.setAttribute('class', 'room');
//     li.innerText= chatroomCodeField.value // This will be the name of the room. for now name is unique code
    
//     let joinedRooms = document.querySelector("#joined-rooms");
//     joinedRooms.appendChild(li);
    
//     // create room membership for user

// })






/* <button id="new-meeting">New Meeting</button>
<form id="join-meeting-form">
    <input id="join-existing-meeting" type="text" placeholder="Enter chatroom code">
    <button>Join</button>
</form> */