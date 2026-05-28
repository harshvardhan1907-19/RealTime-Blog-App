// CSRF Token
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}

// Main comment form
document.getElementById("comment-form")?.addEventListener("submit", function (e) {
    e.preventDefault();

    let formData = new FormData(this);

    fetch(window.location.href, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() },
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.html) {
                const container = document.getElementById("comment-list");
                const emptyState = container.querySelector(".empty-comments");
                if (emptyState) emptyState.remove();

                container.insertAdjacentHTML("afterbegin", data.html);
                document.querySelector("textarea[name='text']").value = "";
            }
        })
        // .catch(error => console.error("Error:", error));
});

function showReplyForm(commentId) {
    let form = document.getElementById("reply-form-" + commentId);
    if (form) {
        form.style.display = form.style.display === "none" ? "block" : "none";
    }
}

// Scroll to comment if URL has hash
if (window.location.hash) {
    const element = document.querySelector(window.location.hash);
    if (element) {
        setTimeout(() => {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            element.style.background = '#fef3c7';
            setTimeout(() => {
                element.style.background = '';
            }, 2000);
        }, 500);
    }
}

function toggleReplies(commentId) {
    const repliesContainer = document.getElementById("replies-container-"+commentId);
    const toggleButton = document.getElementById("toggle-btn-"+commentId);

    if (!repliesContainer) return;

    if (repliesContainer.style.display === "none" || repliesContainer.style.display === "") {
        repliesContainer.style.display = "block";
        toggleButton.innerHTML = `📎 Hide ${repliesContainer.children.length} replies`;
    } else {
        repliesContainer.style.display = "none";
        toggleButton.innerHTML = `📎 Show ${repliesContainer.children.length} replies`;
    }
}

// function likeComment(commentId) {
//     fetch(`/comment/${commentId}/like/`, {
//         method: "POST",
//         headers: { "X-CSRFToken": getCSRFToken() }
//     })
//     .then(res => res.json())
//     .then(data => {
//         const likeSpan = document.getElementById(`comment-like-count-${commentId}`);
//         if (likeSpan) {
//             likeSpan.innerText = data.likes_count;
//         }
//     })
//     // .catch(error => console.error("Error:", error));
// }

// Updated reply form handler - keeps replies hidden until toggled
document.addEventListener("submit", function(e) {
    const form = e.target;
    if (form.classList && form.classList.contains("reply-form")) {
        e.preventDefault();
        
        let formData = new FormData(form);
        let parentid = form.querySelector("input[name='parent_id']").value;

        fetch(window.location.href, {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.html) {
                let repliesContainer = document.getElementById(`replies-container-${parentid}`);

                if (!repliesContainer) {
                    let commentWrapper = document.getElementById(`comment-wrapper-${parentid}`);
                    if (commentWrapper) {
                        const newReplies = document.createElement("div");
                        newReplies.id = `replies-container-${parentid}`;
                        newReplies.className = "replies";
                        newReplies.style.display = "none"; // Start hidden
                        commentWrapper.appendChild(newReplies);
                        repliesContainer = newReplies;
                    }
                }

                if (repliesContainer) {
                    repliesContainer.insertAdjacentHTML('afterbegin', data.html);

                    // update toggle button text
                    const toggleButton = document.getElementById(`toggle-btn-${parentid}`);
                    // After adding a new reply
                    if (toggleButton) {
                        const replyCount = repliesContainer.children.length;
                        // Check if replies container is currently visible or hidden
                        if (repliesContainer.style.display === 'block') {
                            toggleButton.innerHTML = `📎 Hide ${replyCount} replies`;
                        } else {
                            toggleButton.innerHTML = `📎 Show ${replyCount} replies`;
                        }
                        toggleButton.style.display = "inline-flex";
                    }
                }

                form.reset();
                form.style.display = "none";
            }
        })
    }
})

