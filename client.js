const chatBox = document.getElementById("chat-box");

const ws = new WebSocket("ws://localhost:8000");

window.addEventListener("beforeunload", () => {
  chatBox.value = "";
});

ws.addEventListener("message", (event) => {
  handleIncomingMessages(event);
});

function handleIncomingMessages(event) {
  try {
    parsedData = JSON.parse(event.data);
    if (Array.isArray(parsedData)) {
      parsedData.forEach((message) => {
        chatBox.value += "\n" + parseMessage(message);
      });
    } else {
      chatBox.value += "\n" + parseMessage(parsedData);
    }
  } catch (error) {
    chatBox.value += "\n" + event.data;
  }
  chatBox.scrollTop = chatBox.scrollHeight
}

function parseMessage(message) {
  return `[${message.timestamp}] ${message.user_name}: ${message.message} `
}

function sendMessage(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    const userInput = document.getElementById("user-input").value;
    ws.send(userInput);
    document.getElementById("user-input").value = "";
  }

}