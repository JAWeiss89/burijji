document.addEventListener('DOMContentLoaded', function() {
    let socket = io.connect(`//${document.domain}:${location.port}`)
    let currentRoom = "usa";
    join(currentRoom)

    socket.on('connect', function() {
        // socket.send({'msg': 'I am connected!'});
        console.log('socketIO connection established')
    })

    // What to do when message received from server
    socket.on("message", function(data) {
        console.log(data)

        if (data.user) {
            post_user_msg(data)
        } else {
            post_gen_msg(data)
        }

    });

    // event listeners

    document.querySelector('#input-form').addEventListener('submit', function(event) {
        event.preventDefault();
        socket.send({'msg': document.querySelector('#user-message').value,
                     'room': currentRoom});
        document.querySelector('#user-message').value = '';
    }) 


    // room event listeners

    document.querySelectorAll('.room').forEach(function(chatroom) {
        chatroom.addEventListener('click', function(event) {
            let newRoom = chatroom.innerHTML

            if (newRoom != currentRoom) {
                console.log(`Leaving chatroom ${currentRoom}`);
                leave(currentRoom);
                console.log(`Entering chatroom ${newRoom}`);
                join(newRoom);
                currentRoom = newRoom;
            }
        })
    })


    // leave room
    function leave(room) {
        console.log(`leave room function has been called with variable ${room}`)
        socket.emit('leave', {'room': room})
    }

    // join room
    function join(room) {
        console.log(`join room function has been called with variable ${room}`)
        document.querySelector('#messages-window').innerHTML="";
        socket.emit('join', {'room': room})

    }


    // helper functions 

    function post_user_msg(data) {
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
        document.querySelector('#messages-window').append(p1);
        document.querySelector('#messages-window').append(p2);
    }

    function post_gen_msg(data) {
        const p = document.createElement('p');
        p.classList.add('gen-message')
        p.innerHTML = `${data.msg}`;
        document.querySelector('#messages-window').append(p);
    }



})