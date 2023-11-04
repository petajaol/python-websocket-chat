const chatBox = document.getElementById("chat-box");
const userList = document.getElementById("user-list");

const ws = new WebSocket("ws://localhost:8000");

window.addEventListener("beforeunload", () => {
  chatBox.value = "";
  userList.value = "";
});

ws.addEventListener("message", (event) => {
  handleIncomingMessages(event);
});

function handleIncomingMessages(event) {
  try {
    const parsedData = JSON.parse(event.data);

    const handleJoinMessage = () => {
      chatBox.value += "\n" + parsedData.message;
      userList.value += "\n" + parsedData.user_name;
    };

    const handleLeaveMessage = () => {
      chatBox.value += "\n" + parsedData.message;
      const userToRemove = parsedData.user_name;
      const userListArray = userList.value.split('\n');
      const userIndex = userListArray.indexOf(userToRemove);
      if (userIndex !== -1) {
        userListArray.splice(userIndex, 1);
        userList.value = userListArray.join('\n');
      };
    };

    const handleChatMessage = () => {
      chatBox.value += "\n" + parseChatMessage(parsedData);
    };

    const handleMessageLog = () => {
      parsedData.messages.forEach((message) => {
        chatBox.value += "\n" + parseChatMessage(message);
      });
    };

    const handleUserList = () => {
      parsedData.users.forEach((user) => {
        userList.value += "\n" + user;
      });
    };

    const messageHandlers = {
      join_message: handleJoinMessage,
      part_message: handleLeaveMessage,
      chat_message: handleChatMessage,
      message_log: handleMessageLog,
      user_list: handleUserList,
    };

    const messageType = parsedData.type;
    if (messageHandlers[messageType]) {
      messageHandlers[messageType]();
    }
  } catch (error) {
    chatBox.value += "\n" + event.data;
  }

  chatBox.scrollTop = chatBox.scrollHeight
}

function parseChatMessage(message) {
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