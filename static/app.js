class ChatBox {
    constructor() {
        this.args = {
            chatInput: document.querySelector('#chat-input'),
            sendButton: document.querySelector('#send-btn'),
            themeButton: document.querySelector('#theme-btn'),
            deleteButton: document.querySelector('#delete-btn')
        }
        this.messages = [];
    }

    display() {
        const {chatInput, sendButton, themeButton, deleteButton} = this.args;

        sendButton.addEventListener('click', () => this.onSendButton(chatInput));

        chatInput.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatInput);
            }
        });

        deleteButton.addEventListener("click", () => {
            if (confirm("Are you sure you want to delete all the chats?")) {
                chatInput.value = '';
            }
        });

        themeButton.addEventListener("click", () => {
            document.body.classList.toggle("light-mode");
            localStorage.setItem("themeColor", themeButton.innerText);
            themeButton.innerText = document.body.classList.contains("light-mode") ? "dark_mode" : "light_mode";
        });
    }

    onSendButton(chatInput) {
        let text = chatInput.value;
        if (text === "") {
            return;
        }

        let msg = {name: "User", message: text};
        this.messages.push(msg);

        fetch('/predict', {
            method: 'POST',
            body: JSON.stringify({message: text}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                let botMsg = {name: "Sam", message: r.answer};
                this.messages.push(botMsg);
                this.updateChatText(chatInput);
                chatInput.value = '';
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    updateChatText(chatInput) {
        let html = '';
        this.messages.forEach(function (item) {
            if (item.name === "Sam") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>';
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            }
        });

        const chatMessage = document.querySelector('.chat-container');
        chatMessage.innerHTML = html;
    }
}

const chatbox = new ChatBox();
chatbox.display();
