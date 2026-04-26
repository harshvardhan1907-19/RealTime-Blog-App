let loading = false;
let currentParams = "";
let page = 2;
let hasNext = document.getElementById("hasNext").value === "true";
let hasFilterApplied = false;
let scrollTimeout;

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

    // if (page > 2 && hasFilterApplied && currentParams !== "") {
    //     page = 2;
    //     hasFilterApplied = false;
    //     console.log(currentParams)
    // }

    let url = currentParams ? `/?${currentParams}&page=${page}` : `/?page=${page}`;
    // let url = "";
    // if (currentParams) {
    //     url = `/?${currentParams}&page=${page}`
    //     hasFilterApplied = true;
    // } else {
    //     url = `/?page=${page}`;
    // }

    console.log(currentParams)
    console.log("Loading more posts with URL:", url);  // Debug

    document.getElementById("loader").style.display = "block";
    document.getElementById("loader").innerHTML = "Loading more posts...";

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
    if (page > 2) {
        page = 2
    }
    e.preventDefault();

    let formData = new FormData(this);
    let params = new URLSearchParams(formData).toString();
    currentParams = params;
    // Convert form data into URL format -> q=django&category=2
    fetch("/filter-posts/?" + params + "&page=", {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(res => res.json())
        .then(data => {
            document.getElementById("post-container").innerHTML = data.html;
            hasNext = toString(data.has_next);
            // page++;
            // // When filter runs, loader is usually already hidden
            // document.getElementById("loader").style.display = "none";  // Optional
        });
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