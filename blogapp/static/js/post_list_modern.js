let loading = false;
let currentParams = "";
let page = 2;
let hasNext = document.getElementById("hasNext")?.value === "true";
let scrollTimeout;
// const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
// const socket = new WebSocket(protocol + window.location.host + "/ws/notifications/");
// let notif_count = document.getElementById('notif-count');

// socket.onmessage = function (e) {
//     try {
//         let data = JSON.parse(e.data);
//         console.log("📦 Parsed notification:", data);
//         console.log("🔑 Notification ID:", data.notification_id);

//         // update notificaion bell
//         if (data.type === "notification" && typeof notif_count !== "undefined") {
//             let currCount = parseInt(notif_count.innerText) || 0;
//             notif_count.innerText = currCount + 1;
//         } else if (data.type === "update_like_count") {
//             console.log(`📡 Received live like update for Post ${data.post_id}: ${data.new_count}`);
//             // Find the Like Count span on the page
//             let countSpan = document.getElementById(`like-count-${data.post_id}`);
//             let likeBtn = document.getElementById(`like-btn-${data.post_id}`);
//             if (countSpan) {
//                 countSpan.innerText = data.new_count;
//             }

//             if (likeBtn) {
//                 // Replace the text inside the button. 
//                 // WARNING: This will wipe out the heart emoji if not careful!
//                 // Safer approach:
//                 let heartIcon = likeBtn.innerHTML.includes('❤️') ? '❤️' : '🤍';
//                 likeBtn.innerHTML = `${heartIcon} <span id="like-count-${data.post_id}">${data.new_count}</span>`;
//             }
//         }
//     } catch (error) {
//         console.error("❌ Error parsing socket message:", error);
//     }
// }

// socket.onopen = function () {
//     console.log("✅ WebSocket connected for Post List updates");
// };

// // Handle connection errors
// socket.onerror = function (e) {
//     console.log("❌ WebSocket Error in Post List:", e);
// };

// Sort dropdown handler
document.getElementById("sort-select")?.addEventListener("change", function() {
    document.getElementById("sort-hidden").value = this.value;
    document.getElementById("search-btn")?.click();
});

document.getElementById("search-btn")?.addEventListener("click", function (e) {
    e.preventDefault();

    let formData = new FormData(document.getElementById("filter-form"));
    let params = new URLSearchParams(formData).toString();
    let sortValue = document.getElementById("sort-select")?.value || "-created_at";
    // Why: Sort value must be included in filter requests, not just in scroll requests.

    currentParams = params ? `${params}&sort=${sortValue}` : `sort=${sortValue}`;
    page = 2;

    fetch("/filter-posts/?" + currentParams + "&page=1", {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById("post-container").innerHTML = '<div class="posts-grid">' + data.html + '</div>';
            hasNext = data.has_next;
            document.getElementById("hasNext").value = hasNext ? "true" : "false";
            page = 2;
            loading = false;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
});

// Scroll handler
window.addEventListener("scroll", () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 300) {
            if (!loading && hasNext) {
                loading = true;
                loadMorePost();
            }
        }
    }, 200);
});

function loadMorePost() {
    let hasNextValue = document.getElementById("hasNext")?.value === "true";

    if (!hasNextValue) {
        document.getElementById("loader").innerHTML = "📭 No more posts";
        document.getElementById("loader").style.display = "block";
        loading = false;
        return;
    }

    document.getElementById("loader").style.display = "block";
    document.getElementById("loader").innerHTML = "Loading more posts...";

    let sortValue = document.getElementById("sort-select")?.value || "-created_at";
    let url = currentParams ? `/?${currentParams}&page=${page}` : `/?page=${page}`;

    fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.text())
        .then(data => {
            // Get the grid container
            let container = document.getElementById("post-container");
            let grid = container.querySelector('.posts-grid');

            if (!grid) {
                // If no grid exists, create it
                container.innerHTML = '<div class="posts-grid"></div>';
                grid = container.querySelector('.posts-grid');
            }
            // Why: Filter response returns ONLY post cards(no grid wrapper).This wraps them back into the grid structure

            // Extract just the post cards from the response
            let tempDiv = document.createElement('div');
            tempDiv.innerHTML = data;

            // Get all post cards from the response
            let newCards = tempDiv.querySelectorAll('.post-card-modern');

            // Append each card to the grid
            newCards.forEach(card => {
                grid.appendChild(card.cloneNode(true));
            });

            let newHasNext = tempDiv.querySelector("#hasNext")?.value === "true";
            hasNext = newHasNext;
            document.getElementById("hasNext").value = newHasNext;

            if (!hasNext) {
                document.getElementById("loader").innerHTML = "📭 No more posts";
                document.getElementById("loader").style.display = "block";
            } else {
                document.getElementById("loader").style.display = "none";
            }

            page++;
            loading = false;
        })
        .catch(error => {
            console.error("Error loading posts:", error);
            loading = false;
        });
}

// Filter form handler - Simplified
document.getElementById("filter-form").addEventListener("submit", function (e) {
    e.preventDefault();

    let formData = new FormData(this);
    let params = new URLSearchParams(formData).toString();
    let sortValue = document.getElementById("sort-select")?.value || "-created_at";

    currentParams = params ? `${params}&sort=${sortValue}` : `sort=${sortValue}`;
    page = 2;

    fetch("/filter-posts/?" + currentParams + "&page=1", {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            // Reset the grid with new posts
            let container = document.getElementById("post-container");
            container.innerHTML = '<div class="posts-grid">' + data.html + '</div>';

            hasNext = data.has_next;
            document.getElementById("hasNext").value = hasNext ? "true" : "false";
            page = 2;
            loading = false;
            document.getElementById("loader").style.display = "none";
            window.scrollTo({ top: 0, behavior: 'smooth' });
        })
        .catch(error => console.error("Filter error:", error));
});

function likePost(postId) {
    fetch(`/post/${postId}/like/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
    })
    .then(res => res.json())
    .then(data => {
        let btn = document.getElementById(`like-btn-${postId}`);
        let countSpan = document.getElementById(`like-count-${postId}`);

        //  update the UI for the person who clicked
        if (data.liked) {
            btn.innerHTML = `❤️ <span id="like-count-${postId}">${data.total_likes}</span>`;
        } else {
            btn.innerHTML = `🤍 <span id="like-count-${postId}">${data.total_likes}</span>`;
        }
        if (countSpan) countSpan.innerText = data.total_likes;
    });
}

function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}