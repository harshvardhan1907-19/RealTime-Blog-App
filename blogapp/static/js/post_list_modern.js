let loading = false;
let currentParams = "";
let page = 2;
let hasNext = document.getElementById("hasNext")?.value === "true";
let scrollTimeout;

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