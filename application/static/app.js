// // Global variables
// const API_BASE_URL = (() => {
//   // Check if we're in development (localhost)
//   if (
//     window.location.hostname === "localhost" ||
//     window.location.hostname === "127.0.0.1"
//   ) {
//     return "" // Use relative URLs for localhost
//   }
//   // Use full URL for production
//   return "https://erik-chatapp.ddnsking.com"
// })()
let currentRoom = ""
let currentUsername = ""
let pollInterval
let lastMessageCount = 0
let messageCache = []
let lastUsernameHash = ""

/**
 * Initialize the application
 */
function init() {
  // Focus on room input when page loads
  document.getElementById("roomInput").focus()
}

/**
 * Join a chat room
 */
function joinRoom() {
  const room = document.getElementById("roomInput").value.trim()
  const username = document.getElementById("usernameInput").value.trim()

  if (!room || !username) {
    alert("Please enter both room name and username")
    return
  }

  currentRoom = room
  currentUsername = username

  // Update UI
  document.getElementById("joinForm").style.display = "none"
  document.getElementById("chatContainer").style.display = "flex"
  document.getElementById(
    "roomInfo"
  ).textContent = `Room: ${room} | User: ${username}`

  // Load messages and start polling
  loadMessages()
  startPolling()
}

/**
 * Leave the current room
 */
function leaveRoom() {
  clearInterval(pollInterval)
  currentRoom = ""
  currentUsername = ""

  // Reset cache and counters
  messageCache = []
  lastMessageCount = 0
  lastUsernameHash = ""

  // Reset UI
  document.getElementById("joinForm").style.display = "block"
  document.getElementById("chatContainer").style.display = "none"
  document.getElementById("roomInfo").textContent =
    "Enter a room to start chatting"
  document.getElementById("chatMessages").innerHTML =
    '<div class="empty-state">No messages yet. Start the conversation!</div>'

  // Clear inputs
  document.getElementById("roomInput").value = ""
  document.getElementById("usernameInput").value = ""
  document.getElementById("messageInput").value = ""
}

/**
 * Send a new message
 */
function sendMessage() {
  const messageInput = document.getElementById("messageInput")
  const message = messageInput.value.trim()

  if (!message) return

  const formData = new FormData()
  formData.append("username", currentUsername)
  formData.append("msg", message)

  fetch(`/api/chat/${currentRoom}`, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        showError("Error sending message: " + data.error)
      } else {
        messageInput.value = ""
        // Force immediate refresh to show the new message
        setTimeout(loadMessages, 100)
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      showError("Failed to send message")
    })
}

/**
 * Generate a simple hash of all usernames in messages
 * @param {Array} messages - Array of message strings
 * @returns {string} - Simple hash of usernames
 */
function generateUsernameHash(messages) {
  const usernames = messages
    .map((msg) => {
      const match = msg.match(/^\[(.+?) (.+?)\] (.+?): (.+)$/)
      return match ? match[3] : ""
    })
    .filter(Boolean)

  return usernames.sort().join("|")
}

/**
 * Load messages from the server (enhanced with username change detection)
 */
function loadMessages() {
  fetch(`/api/chat/${currentRoom}`)
    .then((response) => response.text())
    .then((data) => {
      const messagesContainer = document.getElementById("chatMessages")

      if (!data.trim()) {
        // Messages were cleared or empty
        messageCache = []
        lastMessageCount = 0
        lastUsernameHash = ""
        messagesContainer.innerHTML =
          '<div class="empty-state">No messages yet. Start the conversation!</div>'
        return
      }

      const messages = data.trim().split("\n")

      // Check if usernames have changed (indicating external username update)
      const currentUsernameHash = generateUsernameHash(messages)
      const usernamesChanged =
        lastUsernameHash && currentUsernameHash !== lastUsernameHash

      // Force refresh if usernames changed or message count changed
      if (
        messages.length !== lastMessageCount ||
        usernamesChanged ||
        messageCache.length === 0
      ) {
        if (usernamesChanged) {
          console.log("Username change detected, forcing full refresh")
          messageCache = [] // Force full refresh
        }

        updateMessagesDisplay(messages, messagesContainer)
        lastMessageCount = messages.length
        lastUsernameHash = currentUsernameHash
      }
    })
    .catch((error) => {
      console.error("Error loading messages:", error)
      showError("Failed to load messages")
    })
}

/**
 * Update messages display efficiently
 * @param {Array} messages - Array of message strings
 * @param {HTMLElement} messagesContainer - Container element
 */
function updateMessagesDisplay(messages, messagesContainer) {
  const newMessages = []

  // Parse all messages
  messages.forEach((messageText) => {
    const messageElement = parseMessage(messageText)
    if (messageElement) {
      newMessages.push({
        text: messageText,
        element: messageElement,
      })
    }
  })

  let hasNewMessages = false

  // Check if we need to add new messages only or do full refresh
  if (messageCache.length > 0 && newMessages.length > messageCache.length) {
    // Add only new messages
    const messagesToAdd = newMessages.slice(messageCache.length)
    messagesToAdd.forEach((msg) => {
      messagesContainer.appendChild(msg.element)
    })
    hasNewMessages = true
  } else if (
    newMessages.length < messageCache.length ||
    messageCache.length === 0
  ) {
    // Full refresh (initial load, messages deleted, or cache mismatch)
    messagesContainer.innerHTML = ""
    newMessages.forEach((msg) => {
      messagesContainer.appendChild(msg.element)
    })
    hasNewMessages = newMessages.length > 0
  }

  // Update cache
  messageCache = [...newMessages]

  // Always scroll to bottom when new messages are added
  if (hasNewMessages) {
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight
    }, 50) // Small delay to ensure DOM is updated
  }
}

/**
 * Parse a message string into HTML element
 * @param {string} messageText - Raw message text from server
 * @returns {HTMLElement|null} - Parsed message element
 */
function parseMessage(messageText) {
  const match = messageText.match(/^\[(.+?) (.+?)\] (.+?): (.+)$/)
  if (!match) return null

  const [, date, time, username, content] = match

  const messageDiv = document.createElement("div")
  messageDiv.className = "message"

  messageDiv.innerHTML = `
        <div class="message-header">
            <span class="username">${escapeHtml(username)}</span>
            <span class="timestamp">${escapeHtml(date)} ${escapeHtml(
    time
  )}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `

  return messageDiv
}

/**
 * Change username in the current room
 */
function changeUsername() {
  const newUsername = prompt(
    `Change your username from "${currentUsername}" to:`,
    currentUsername
  )

  if (!newUsername || newUsername.trim() === "") {
    return
  }

  const trimmedUsername = newUsername.trim()

  if (trimmedUsername === currentUsername) {
    alert("New username must be different from your current username")
    return
  }

  const formData = new FormData()
  formData.append("old_username", currentUsername)
  formData.append("new_username", trimmedUsername)

  fetch(`/api/chat/${currentRoom}`, {
    method: "PUT",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert("Error changing username: " + data.error)
      } else {
        // Update current username
        currentUsername = trimmedUsername

        // Update room info display
        document.getElementById(
          "roomInfo"
        ).textContent = `Room: ${currentRoom} | User: ${currentUsername}`

        // Clear cache to force full refresh with updated usernames
        messageCache = []
        lastMessageCount = 0

        // Force full refresh of messages
        loadMessages()
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      showError("Failed to change username")
    })
}
function clearChat() {
  if (!confirm("Are you sure you want to clear all messages in this room?")) {
    return
  }

  fetch(`/api/chat/${currentRoom}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => {
      // Reset cache and counters
      messageCache = []
      lastMessageCount = 0
      loadMessages()
    })
    .catch((error) => {
      console.error("Error:", error)
      showError("Failed to clear chat")
    })
}

/**
 * Start polling for new messages
 */
function startPolling() {
  // Poll every 2 seconds for new messages
  pollInterval = setInterval(loadMessages, 2000)
}

/**
 * Handle Enter key press in join form inputs
 * @param {KeyboardEvent} event
 */
function handleJoinKeyPress(event) {
  if (event.key === "Enter") {
    joinRoom()
  }
}

/**
 * Handle Enter key press in message input
 * @param {KeyboardEvent} event
 */
function handleKeyPress(event) {
  if (event.key === "Enter") {
    sendMessage()
  }
}

/**
 * Escape HTML characters to prevent XSS
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
  const div = document.createElement("div")
  div.textContent = text
  return div.innerHTML
}

/**
 * Show error message to user
 * @param {string} message
 */
function showError(message) {
  alert(message) // Simple alert for now, could be improved with toast notifications
}

// Initialize app when DOM is loaded
document.addEventListener("DOMContentLoaded", init)
