document.addEventListener('DOMContentLoaded', function() {
    let socket = io.connect(`//${document.domain}:${location.port}`)
    let currentRoom = "lounge";
    let preferredLanguage = document.querySelector(".my-language").innerHTML


    joinNewRoom(currentRoom);

     // WHAT TO DO WHEN CONNECTION IS ESTABLISHED

    socket.on('connect', function() {
        console.log('socketIO connection established')
    })

    // WHAT TO DO WITH MESSAGE RECEIVED FROM SERVER

    socket.on("message", function(data) {
        console.log(data)
        
        if (data.user) {
            post_user_msg(data)
        } else {
            post_gen_msg(data)
        }

    });

    // SENDING A MESSAGE WHEN SUBMITTING MESSAGE FORM

    document.querySelector('#input-form').addEventListener('submit', function(event) {
        event.preventDefault();
        if (document.querySelector('#user-message').value != "") {
            socket.send({'msg': document.querySelector('#user-message').value,
            'room': currentRoom});
            document.querySelector('#user-message').value = '';
        }

    }) 


    // JOINING A NEW ROOM BY CLICKING ONE ONE FROM ROOM LIST

    let roomsList = document.querySelector('#joined-rooms');
    roomsList.addEventListener("click", function(event) {

        let newRoom = event.target.attributes.meetingcode.value;
            if (newRoom != currentRoom) {
                joinNewRoom(newRoom);
            }
    });


    // PROCESS FORM TO CREATE OR JOIN A NEW ROOM
    

    let newMeetingBtn = document.querySelector("#new-meeting");
    let chatroomCodeField = document.querySelector("#chatroom-code-input")
    
    newMeetingBtn.addEventListener('click', function() {
        chatroomCodeField.value=getRandomChatCode();
    })
    
    
    let joinForm = document.querySelector("#join-meeting-form");
    
    joinForm.addEventListener("submit", function(event) {
        event.preventDefault();

        // Add meeting to my rooms list
        let li = document.createElement('li');
        li.setAttribute('meetingcode', chatroomCodeField.value);
        li.setAttribute('class', 'room');
        li.innerText= chatroomCodeField.value // This will be the name of the room. for now name is unique code
        
        let joinedRooms = document.querySelector("#joined-rooms");
        joinedRooms.appendChild(li);

        // actually join room & clear chat screen
        
        joinNewRoom(chatroomCodeField.value);
        chatroomCodeField.value="";
    })


    // LEAVE ROOM

    function leave(room) {
        socket.emit('leave', {'room': room})
    }

    // JOIN ROOM

    function join(room, roomName) {
        // 2nd arg is optional 

        if (roomName) {
            socket.emit('join', {'room': room, 'roomname': roomName})
        } else {
            socket.emit('join', {'room': room})
        }
    }


    // HANDLES LEAVING ROOM, CLEARING SCREEN, GETTING OLD MESSAGES, JOINING ROOM
    async function joinNewRoom(roomcode) {
        leave(currentRoom);
        clearMessages();
        
        // Now get old messages 
        let response = await axios.get(`http://127.0.0.1:5000/chatroom/${roomcode}/messages`)
        let messages = response.data;

        if (!messages.errors) {
            for (let message of messages) {
                post_user_msg(message);
            }           
        }

        join(roomcode);
        currentRoom = roomcode;
    }

    // ==========================================
    //  HELPER FUNCTIONS
    // ==========================================

    function post_user_msg(data) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(`${data.language}`)
        if (data.language != preferredLanguage) {
            messageDiv.classList.add("hidden");
        }
        const p1 = document.createElement('p');
        const p2 = document.createElement('p');
        const nameSpan = document.createElement('span');
        const dateSpan = document.createElement('span');
        dateSpan.classList.add('date-span');
        nameSpan.classList.add('name-span');
        p1.classList.add('message-header')
        p2.classList.add('user-message')
        nameSpan.innerHTML = `${data.user} `;
        dateSpan.innerHTML = `${data.time} `;
        p2.innerHTML = `${data.msg}`;
        p1.prepend(dateSpan);
        p1.prepend(nameSpan);
        messageDiv.append(p1);
        messageDiv.append(p2);

        document.querySelector('#messages-window').append(messageDiv);

    }

    function post_gen_msg(data) {
        const p = document.createElement('p');
        p.classList.add('gen-message')
        p.innerHTML = `${data.msg}`;
        document.querySelector('#messages-window').append(p);
    }

    function clearMessages() {
        document.querySelector('#messages-window').innerHTML="";
    }


})