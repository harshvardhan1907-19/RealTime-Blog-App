const box = document.getElementById('notif-box');
const wrapper = document.getElementById('wrapper');
let notif_count = document.getElementById('notif-count');
let notifLoading = false;

if ("Notification" in window) {
    if (Notification.permission === "default") {
        Notification.requestPermission();
    }
}

// Move this to line 1
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showDesktopNotification(message, postId = null, commentId = null, notificationId = null) {
    if (Notification.permission === "granted") {
        let notification = new Notification("🔔 New Notification", {
            body: message,
            icon: "https://cdn-icons-png.flaticon.com/512/1827/1827392.png"
        });

        notification.onclick = () => {
            window.focus();
            
            if (notificationId) {
                fetch(`/notification/markread/${notificationId}/`, {
                    method: "POST",
                    headers: {'X-CSRFToken': getCSRFToken()}
                })
            }

                if (commentId) {
                    window.location.href = `/post/${postId}/#comment-${commentId}`;
                } else {
                    window.location.href = `/post/${postId}`;
                }
        };
    }
}

function updateNotificationCount() {
    fetch("/notification/count/")
        .then(res => res.json())
        .then(data => {
            notif_count.innerText = data.count;
        });
}

function loadNotifications() {
    if (notifLoading) return;
    notifLoading = true;
    // e.preventDefault();
    fetch("/notification/data/")

        .then(res => res.json())
        .then(data => {

            if (!data.notifications.length) {
                box.innerHTML = "<p>No notifications</p>";
                return;
            }

            // let newNotifications = data.notifications.filter(n => n.id > lastNotificationId);

            // // 🔥 show notification ONLY once
            // if (newNotifications.length > 0) {
            //     let latest = newNotifications[0];
            //     showDesktopNotification(latest.message, latest.post_id, latest.comment_id);
            //     lastNotificationId = latest.id;
            //     localStorage.setItem("lastNotificationId", lastNotificationId)
            // }
            // let box = document.getElementById('notif-box');

            // if (data.notifications.length === 0) {
            //     box.innerHTML = "<p>No notifications</p>";
            //     return;
            // }


            // let latest = data.notifications[0]; // ✅ only first

            // data.notifications.forEach(n => {
            //     if (n.id > lastNotificationId) {
            //         showDesktopNotification(n.message, n.post_id, n.comment_id);
            //         lastNotificationId = n.id;
            //         localStorage.setItem("lastNotificationId", n.id);
            //     }
            // })
            // if (latest.id > lastNotificationId) {
            //     showDesktopNotification(latest.message, latest.post_id);
            //     lastNotificationId = latest.id;
            // }

            // render UI (dropdown)
            let html = "";
            data.notifications.forEach(element => {
                html += `   
                    <a href="javascript:void(0)"
                        onclick="notif_marked_read(${element.id}, ${element.post_id}, ${element.comment_id})">
                        <div style="padding:5px 0; border-bottom:1px solid #eee;">
                            ${element.message}<br>
                            <small>${element.time}</small>
                        </div>
                    </a>
                `;
            });

            box.innerHTML = html;
        })
        .finally(() => {
            notifLoading = false;
        });
}

function notif_marked_read(id, postId, comId) {
    console.log(id)
    fetch(`/notification/markread/${id}/`)
        .then(res => {
            if (!res.ok) throw new Error("Request failed");
            return res.json();
        })
        .then(data => {
            notif_count.innerText = parseInt(data.count);

            setTimeout(() => {
                if (comId) {
                    window.location.href = `/post/${postId}/#comment-${comId}`;
                } else {
                    window.location.href = `/post/${postId}/`;
                }
            }, 300); // small delay
        })
        .catch(err => {
            console.error("Error:", err);
            // fallback redirect anyway
            window.location.href = `/post/${postId}/`;
        });
}


// Websocket real time

const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

const socket = new WebSocket(
    protocol + window.location.host + "/ws/notifications/"
);

let isSocketReady = false
let pendingMessages = [];

function sendViaSocket(data) {
    if (isSocketReady && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
    } else {
        console.log("📦 Socket not ready, queueing message:", data);
        pendingMessages.push(data);
    }
}

function processPendingMessage() {
    while (pendingMessages.length > 0 && socket.readyState === WebSocket.OPEN) {
        const data = pendingMessages.shift();
        socket.send(JSON.stringify(data))
    }
}

socket.onopen = function() {
    console.log("✅ WebSocket connected - readyState:", socket.readyState);
    isSocketReady = true;
    processPendingMessage();
}

socket.onmessage = function (e) {
    console.log("🔥 MESSAGE FROM WS:", e.data);
    console.log("🔥 RAW DATA TYPE:", typeof e.data);

    // Add this alert for testing
    // alert("WebSocket message received: " + e.data);

    try {
        let data = JSON.parse(e.data);
        console.log("📦 Parsed notification:", data);
        console.log("🔑 Notification ID:", data.notification_id);

        showDesktopNotification(data.message, data.post_id, data.comment_id, data.notification_id);
        updateNotificationCount();
    } catch (error) {
        console.error("❌ Error parsing message:", error);
    }
}

socket.onerror = function(e) {
    console.log("❌ WebSocket Error", e);
    console.log("Socket readyState:", socket.readyState);
}

socket.onclose = function () {
    // Why reconnect ? If server restarts or network drops, automatically tries to recover.
    console.log("🔒 WebSocket closed - Code:", event.code, "Reason:", event.reason);
    isSocketReady = false;

    // Try to reconnect after 3 seconds
    setTimeout(function () {
        console.log("🔄 Attempting to reconnect...");
        window.location.reload(); // Simple reload
    }, 3000);
}

setInterval(() => {
    if (socket.readyState !== 1) {
        console.log("⚠️ Socket state:",
            socket.readyState === 0 ? "CONNECTING" :
            socket.readyState === 1 ? "OPEN" :
            socket.readyState === 2 ? "CLOSING" : "CLOSED"
        );
    }
}, 1000);

// auto update every 5 sec
// setInterval(updateNotificationCount, 6000);
wrapper.addEventListener("mouseenter", () => {
    box.style.display = 'block';
    loadNotifications();
});

wrapper.addEventListener("mouseleave", () => {
    box.style.display = 'none';
});

// call once
updateNotificationCount();