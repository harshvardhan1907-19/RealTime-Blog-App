let loading = false;
let currentParams = "";
let page = 2;
let hasNext = document.getElementById("hasNext").value === "true";
let hasFilterApplied = false;
let scrollTimeout;

setTimeout(function() {
    let alerts = document.querySelectorAll('.alert');
alerts.forEach(function(alert) {
    let bsAlert = new bootstrap.Alert(alert);
bsAlert.close();
    });
}, 3000);

document.getElementById("sort-select")?.addEventListener("change", function (e) {
    document.getElementById("sort-hidden").value = this.value;  // Update hidden input for 

    document.getElementById("filter-form").dispatchEvent(new Event("submit"));
});

window.addEventListener("scroll", () => {
    clearTimeout(scrollTimeout);

    scrollTimeout = setTimeout(() => {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100) {
            if (!loading && hasNext) {
                loading = true;
                loadMorePost();
            }
        }
    }, 400);
})

function loadMorePost() {

    let hasNextValue = document.getElementById("hasNext")?.value === "true";

    if (!hasNextValue) {
        document.getElementById("loader").innerHTML = "📭 No more posts";
        document.getElementById("loader").style.display = "block";
        loading = false
        return;
    }

    document.getElementById("loader").style.display = "block";
    document.getElementById("loader").innerHTML = "Loading more posts...";

    // get current sort
    let sortValue = document.getElementById("sort-select")?.value || "-created_at";

    let url = currentParams ? `/?${currentParams}&page=${page}` : `/?page=${page}`;

    console.log(currentParams)
    console.log("Loading more posts with URL:", url);  // Debug

    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'  // ✅ Important for AJAX detection
        }
    })
        .then(res => res.text())
        .then(data => {
            let parser = new DOMParser();
            let doc = parser.parseFromString(data, "text/html");
            // doc = a temporary HTML page (in memory), created by JavaScript to hold the response HTML from the server. We can use it to extract the new posts and hasNext value.

            let newPosts = doc.querySelector("#post-container")?.innerHTML || "";
            let newHasNext = doc.querySelector("#hasNext")?.value === "true";

            if (newPosts) {
                // Append new posts
                document.getElementById("post-container").innerHTML += newPosts;
            }

            hasNext = newHasNext
            document.getElementById("hasNext").value = newHasNext;

            // Update loader based on remaining posts

            if (!hasNext) {
                document.getElementById("loader").innerHTML = "📭 No more posts";
                document.getElementById("loader").style.display = "block";
            } else {
                document.getElementById("loader").style.display = "none";
            }

            page++;
            loading = false;
        });
}

document.getElementById("filter-form").addEventListener("submit", function (e) {
    e.preventDefault();

    let formData = new FormData(this);
    let params = new URLSearchParams(formData).toString();

    // Get current sort from dropdown
    let sortValue = document.getElementById("sort-select")?.value || "-created_at";

    // Build currentParams with filter + sort
    // currentParams = params ? `${params}&sort=${sortValue}` : `sort=${sortValue}`;

    currentParams = params;

    // Reset page
    page = 2;

    console.log("Filtering with:", currentParams);  // Debug

    // ✅ Use currentParams (includes both filter and sort)
    fetch("/filter-posts/?" + currentParams + "&page=1", {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById("post-container").innerHTML = data.html;
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
        headers: {
            "X-CSRFToken": getCSRFToken(),
        }
    })
        .then(response => response.json())
        .then(data => {
            let btn = document.getElementById(`like-btn-${postId}`);
            let count = document.getElementById(`like-count-${postId}`);
            // console.log(count)
            // console.log(postId)
            //let heart = document.getElementById(`heart-${postId}`);

            if (data.liked) {
                btn.innerHTML = "❤️ Remove";
                //heart.innerHTML = "❤️";   // SHOW heart
            } else {
                btn.innerHTML = "🤍 Like";
                //heart.innerHTML = "";     // HIDE heart
            }
            // console.log(data.total_likes)
            count.innerHTML = "❤️ " + data.total_likes;
        });
}

// Get CSRF token
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        .split('=')[1];
}