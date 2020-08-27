document.addEventListener('DOMContentLoaded', function() {
    let currentRoom = ""; // What room do we want the user to be at the beginning?
    let preferredLanguage = document.querySelector(".my-language").innerHTML;
    let currentUserID = document.querySelector(".my-user-id").innerHTML;
    console.log(preferredLanguage);
    joinNewMeeting(currentRoom);

    // ==================================================
    // SOCKET-IO FUNCTIONALITY
    // ==================================================

    // SOCKET CONNECT
    let socket = io.connect(`//${document.domain}:${location.port}`)

    // What to do when connection is established:
    socket.on("connect", function() {
        console.log("socketIO connection established")
    })

    // SOCKET MESSAGE
    // What to do with message received from server:
    // Message will have 3 defining featues: 
    // - If message has USER key then it's a user message
    // - If message has JOIN_REQUEST key, then it's a system message showing if request to join was a success
    // - If message doesn't have the above keys, then it's a general system message

    socket.on("message", function(data) {
        if (data.user) {
            post_user_msg(data)
        } else if (data.join_request) {
            if (data.join_request == "success" && currentUserID == data.user_id) {
                console.log("join function being called");
                console.log(`currentUserID: ${currentUserID} and data['user_id']: ${data.user_id}`)
                // Now proceed to join. 
                meetingName = data.roomname
                meetingCode = data.roomcode         
                // use broader function of join room
                joinNewMeeting(meetingCode);
                // Add meeting to my rooms list on page
                addJoinedMeetingToList(meetingCode, meetingName);

            } else {
                // Joining of new room failed. Let user know
                post_gen_msg(data)
            }

        } else {
            post_gen_msg(data)
        }
    })

    // SOCKET JOIN USING EMIT('JOIN')
    // The join function will be called with one argument when attempting to join existing meeting
    // or with two aarguments when joining an entirely new room being created
    // 

    function join(roomCode) {
        socket.emit('join', {'room': roomCode})
    }

    // SOCKET LEAVE
    function leave(roomCode) {
        socket.emit('leave', {'room': roomCode})
    }

    // SOCKET NEW MEETING REQUEST 

    function newMeetingRequest(roomcode, roomname) { // second arg (roomname) is optional
        if (roomname) { // Then request is to create a new meeting
            socket.emit('new_meeting_request', {'roomname': roomname, 'roomcode': roomcode, 'currentroom': currentRoom})
        } else { // Then request is to join existing meeting
            socket.emit('new_meeting_request', {'roomcode': roomcode, 'currentroom': currentRoom})
        }
    }

    // SOCKET SEND USER MESSAGE

    function sendUserMessage(message, roomcode) {
        // user information will be retrieved from cookies
        socket.send({'msg': message, 'room': roomcode})
    }



    // ==================================================
    // NEW MEETING FUNCTIONALITY 
    // ==================================================
    // Not the same as socket join function above. This will actually leave the current meeting, join new one, and clear screen.  

    async function joinNewMeeting(meetingCode) {
        if (!meetingCode) {
            meetingCode="lounge"
        } else {
            leave(currentRoom)
        }
        clearMessages();

        // Now get old messages 
        let response = await axios.get(`http://127.0.0.1:5000/chatroom/${meetingCode}/info`)
        
        let messages = response.data.messages;
        if (!messages.errors) {
            for (let message of messages) {
                post_user_msg(message);
            }           
        }

        let users = response.data.users;
        if (users) {
            let meetingMembers = document.querySelector("#meeting-members").innerHTML="";
            for (let user of users) {
                add_user_to_member_list(user);
            }
        }

        let meetingInfo = response.data.info;
        post_meeting_info(meetingInfo);
    

        join(meetingCode);
        currentRoom = meetingCode;
    }

    // Window Selectors
    let newMeetingWindow = document.querySelector("#new-meeting-window");
    let createOrJoinWindow = document.querySelector("#create-or-join-window");
    let createNewWindow = document.querySelector("#create-new-window");
    let joinExistWindow = document.querySelector("#join-exist-window");
    let createSuccessWindow = document.querySelector("#create-success-window");
    let joinSuccessWindow = document.querySelector("#join-success-window");

    // Button Selectors
    let newMeetingBtn = document.querySelector("#new-meeting-btn");
    let createNewBtn = document.querySelector("#create-new-btn");
    let joinExistBtn = document.querySelector("#join-exist-btn");
    let finalCreateNewBtn = document.querySelector("#final-create-new-btn");
    let finalJoinExistBtn = document.querySelector("#final-join-exist-btn");
    let startOverBtn = document.querySelector("#start-over-btn");

    // Form Field Selectors
    let newMeetingNameInput = document.querySelector("#new-meeting-name-input");
    let newMeetingCodeGen = document.querySelector("#new-meeting-code-gen");
    let joinMeetingCodeInput = document.querySelector("#join-meeting-code-input");
    let meetingCodeShare = document.querySelector("#meeting-code-share");

    // Event Listeners
    newMeetingBtn.addEventListener('click', () => {
        newMeetingWindow.classList.add('hidden');
        createOrJoinWindow.classList.remove('hidden');
        createOrJoinWindow.classList.add("current-window");
        startOverBtn.classList.remove("hidden");
    })

    startOverBtn.addEventListener('click', resetNewMeetingForm)

    createNewBtn.addEventListener('click', () => {
        createOrJoinWindow.classList.add("hidden");
        createOrJoinWindow.classList.remove("current-window");
        createNewWindow.classList.remove("hidden");
        
        // Generate New Unique Code
        newMeetingCodeGen.innerHTML = getRandomChatCode();
    })

    joinExistBtn.addEventListener('click', () => {
        createOrJoinWindow.classList.add("hidden");
        createOrJoinWindow.classList.remove("current-window");
        joinExistWindow.classList.remove("hidden");
    })

    finalCreateNewBtn.addEventListener('click', () => {

        // process information and send to server

        let meetingName = newMeetingNameInput.value
        let meetingCode = newMeetingCodeGen.innerHTML


        newMeetingRequest(meetingCode, meetingName);


        // reset inputs
        newMeetingNameInput.value = "";

        // show next window
        createNewWindow.classList.add("hidden");
        createSuccessWindow.classList.remove("hidden");
        meetingCodeShare.innerHTML = meetingCode;
    })

    finalJoinExistBtn.addEventListener('click', () => {
        // process information and send to server
        let meetingCode = joinMeetingCodeInput.value
        
        newMeetingRequest(meetingCode)

        // reset inputs
        joinMeetingCodeInput.value = "";

        // show next window
        joinExistWindow.classList.add("hidden");
        joinSuccessWindow.classList.remove("hidden");
    })

    function resetNewMeetingForm() {
        createOrJoinWindow.classList.add("hidden");
        createNewWindow.classList.add("hidden");
        joinExistWindow.classList.add("hidden");
        createSuccessWindow.classList.add("hidden");
        joinSuccessWindow.classList.add("hidden");
        startOverBtn.classList.add("hidden");

        newMeetingWindow.classList.remove("hidden");
        createOrJoinWindow.classList.remove("current-window");
    }

    // ==================================================
    // USER SECTION NAVIGATION (CHANGE USER SETTINGS)
    // ==================================================
    let userInfoWindow = document.querySelector("#user-info");
    let changeLanguageWindow = document.querySelector("#change-language")
    let settingsIcon = document.querySelector(".settings");
    let goBackButton = document.querySelector("#go-back");

    settingsIcon.addEventListener("click", function() {
        userInfoWindow.classList.add("hidden");
        changeLanguageWindow.classList.remove("hidden");
    })

    goBackButton.addEventListener("click", function() {
        changeLanguageWindow.classList.add("hidden");
        userInfoWindow.classList.remove("hidden");
    })

   




    // ==================================================
    // CHANGE BETWEEN MY MEETINGS FUNCTIONALITY
    // ==================================================

    let roomsList = document.querySelector('#joined-rooms');
    roomsList.addEventListener("click", function(event) {

        let newRoom = event.target.attributes.meetingcode.value;
            if (newRoom != currentRoom) {
                joinNewMeeting(newRoom);
            }
    });



    // ==================================================
    // SEND MESSAGE FUNCTIONALITY
    // ==================================================
    document.querySelector('#input-form').addEventListener('submit', function(event) {
        event.preventDefault();
        let userMessage = document.querySelector("#user-message")
        if (userMessage.value != "") {
            sendUserMessage(userMessage.value, currentRoom);
            userMessage.value = "";
        }
    }) 


    // ==================================================
    // UNSUBSCRIBE FROM MEETING FUNCTIONALITY
    // ==================================================
    let unsubscribeButton = document.querySelector("#unsubscribe");
    unsubscribeButton.addEventListener("click", function() {
        unsubscribe(currentRoom)
    })

    // ==================================================
    //  HELPER FUNCTIONS
    // ==================================================

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

    function addJoinedMeetingToList(meetingCode, meetingName) {
        // Add meeting to my rooms list
        let li = document.createElement('li');
        li.setAttribute('meetingcode', meetingCode);
        li.setAttribute('class', 'room');
        li.setAttribute('id', meetingCode);
        li.innerText= meetingName;
        
        let joinedRooms = document.querySelector("#joined-rooms");
        joinedRooms.appendChild(li);
    }

    function add_user_to_member_list(user) {
        let meetingMembers = document.querySelector('#meeting-members')
        let li = document.createElement('li');
        li.innerHTML=user.username

        meetingMembers.append(li);
    }

    function post_meeting_info(info) {
        let inviteCode = document.querySelector("#invite-code");
        let thisMeetingName = document.querySelector("#this-meeting-name");
        inviteCode.innerHTML= info.roomcode;
        thisMeetingName.innerHTML= info.name;
    }

    async function unsubscribe(meetingCode) {
        console.log(`Attempting to unsubscribe from ${meetingCode}`)
        let response = await axios.get(`http://127.0.0.1:5000/chatroom/${meetingCode}/unsubscribe`)
        console.log(response);
        if (response.data.msg == "Unsubscribed Succesfully") {
            let listedMeeting = document.querySelector(`#${meetingCode}`);
            listedMeeting.remove();
        } else {
            console.log(response.data.msg)
        }
        joinNewMeeting('lounge');
    }

});