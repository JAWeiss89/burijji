document.addEventListener('DOMContentLoaded', function() {
    let socket = io.connect(`//${document.domain}:${location.port}`)

    socket.on('connect', function() {
        socket.send(' has connected');
    })

    socket.on("message", function(data) {
        console.log(data)
        const p1 = document.createElement('p');
        const p2 = document.createElement('p');
        const nameSpan = document.createElement('span');
        const dateSpan = document.createElement('span');
        const br = document.createElement('br');
        dateSpan.classList.add('date-span');
        nameSpan.classList.add('name-span');
        p1.classList.add('message-header')
        p2.classList.add('user-message')
        nameSpan.innerHTML = `${data.user} `;
        dateSpan.innerHTML = `${data.time} `;
        p2.innerHTML = `${data.data}`;
        p1.prepend(dateSpan);
        p1.prepend(nameSpan);
        document.querySelector('#messages-window').append(p1);
        document.querySelector('#messages-window').append(p2);
    });

    document.querySelector('#input-form').addEventListener('submit', function(event) {
        event.preventDefault();
        socket.send(document.querySelector('#user-message').value);
        document.querySelector('#user-message').value = '';
    }) 


})