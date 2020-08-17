document.addEventListener('DOMContentLoaded', function() {
    let socket = io.connect(`//${document.domain}:${location.port}`)

    socket.on('connect', function() {
        socket.send("I am connected");
    })

    socket.on("message", function(data) {
        console.log(data)
        const p = document.createElement('p');
        const br = document.createElement('br');
        p.innerHTML = data;
        document.querySelector('#messages-window').append(p);
    });

    document.querySelector('#input-form').addEventListener('submit', function(event) {
        event.preventDefault();
        socket.send(document.querySelector('#user-message').value);
        document.querySelector('#user-message').value = '';
    }) 


})