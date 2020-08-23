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

