const chatArea = document.getElementById("chatArea");

function connectWebSocket() {
  const ws = new WebSocket("ws://localhost:8000");

  ws.addEventListener("message", (event) => {
    chatArea.innerHTML += `${event.data}<br>`;
  });

  return ws;
}

const ws = connectWebSocket();

function checkEnter(event) {
  if (event.key === "Enter") {
    event.preventDefault();
    submitInput();
  }
}

function submitInput() {
  const userInput = document.getElementById("user-input").value;
  ws.send(userInput);
}
