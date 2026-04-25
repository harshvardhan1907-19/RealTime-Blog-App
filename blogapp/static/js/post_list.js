let page = 1;
let loading = false;
let currentParams = "";
let hasNext = true;
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

    document.getElementById("loader").style.display = "block";

    fetch(`/filter-posts/?${currentParams}&page=${page}`)
        .then(res => res.json())
        .then(data => {
            // let parser = new DOMParser();
            // let doc = parser.parseFromString(data, "text/html");
            // doc = a temporary HTML page (in memory), created by JavaScript to hold the response HTML from the server. We can use it to extract the new posts and hasNext value.

            // let newPosts = doc.querySelector("#post-container").innerHTML;
            // let newHasNext = doc.querySelector("#has-next").value;
            document.getElementById("post-container").innerHTML += data.html;
            hasNext = data.has_next;
            page++;
            loading = false;
            document.getElementById("loader").style.display = "none";

            if (!hasNext) {
                document.getElementById("loader").innerHTML = "No more posts";
            } else {
                document.getElementById("loader").innerHTML = "Loading...";
            }
            // setTimeout(() => {
            //     // document.getElementById("post-container").innerHTML += data.html;

            //     // page++;
            //     // loading = false;
            // }, 500)
        });
}

// setInterval(() => {
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
// }, 300);

document.getElementById("filter-form").addEventListener("submit", function (e) {
    e.preventDefault();

    let formData = new FormData(this);
    let params = new URLSearchParams(formData).toString();
    currentParams = params;
    // Convert form data into URL format -> q=django&category=2
    page = 1;
    hasNext = true;
    fetch("/filter-posts/?" + params + "&page=" + page)
    .then(res => res.json())
    .then(data => {
        document.getElementById("post-container").innerHTML = data.html;
        hasNext = data.has_next;
        page++;
    });
});

// Get CSRF token
function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        .split('=')[1];
}