console.log('app.js is connected');

function getRandomChatCode() {
    let chatcode = "";
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz123456789";

    for (let i=0; i<11; i++) {
        if (i==3 || i==7) {
            chatcode = chatcode + "-"
        } else {
            chatcode = chatcode + chars[Math.floor(Math.random()*61)]
        }
    }
    return chatcode;
}

