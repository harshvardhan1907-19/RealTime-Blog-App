let lastNotificationId = parseInt(localStorage.getItem("lastNotificationId") || 0);

window.onload = function () {
    let hash = window.location.hash; // Gets #comment-123 from URL

    if (hash) {
        let el = document.querySelector(hash); // Finds element with that ID

        if (el) {
            el.scrollIntoView({ behavior: "smooth" }); // Scrolls to comment

            // highlight effect
            el.style.background = "#fff3cd";

            setTimeout(() => {
                el.style.background = "";
            }, 2000);
        }
    }
};

document.getElementById("comment-form").addEventListener("submit", function (e) {
    e.preventDefault();
    console.log("📝 Main comment submitted");

    let formData = new FormData(this);

    fetch(window.location.href, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
        },
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.html) {
                const container = document.getElementById("comment-list");
                container.innerHTML = data.html + container.innerHTML;
                document.querySelector("textarea[name='text']").value = "";
            }
        })
    //.catch(error => console.error("❌ Comment error:", error))
});

function getCSRFToken() {
    return document.cookie.split("; ").find(row => row.startsWith("csrftoken")).split("=")[1];
}

document.addEventListener("submit", function (e) {
    e.preventDefault();
    let form = e.target;
    if (e.target.id.startsWith("reply-form-")) {
        e.preventDefault();
        console.log("📝 Reply submitted");

        let form = e.target
        let formData = new FormData(form);
        let parentId = form.querySelector("input[name='parent_id']").value;

        fetch(window.location.href, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
            },
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                console.log("Reply data", data)
                if (data.html) {
                    let container = document.getElementById("reply-list-" + parentId);
                    if (container) {
                        container.innerHTML = data.html + container.innerHTML;
                    }
                    form.style.display = "none";
                    form.querySelector("textarea").value = "";
                }

            })
        //.catch(error => console.error("❌ Reply error:", error))
    }
});

function showReplyForm(commentId) {
    let form = document.getElementById("reply-form-" + commentId);
    if (form) {
        if (form.style.display === "none" || form.style.display === "") {
            form.style.display = "block";
        } else {
            form.style.display = "none";
        }
    }
}