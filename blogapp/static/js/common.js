setTimeout(function () {
    let alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        let bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 3000);

function openImageModal(imageUrl, username = null) {
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");

    if (imageUrl) {
        //if image exists, show image
        modalImage.src = imageUrl;
        modalImage.style.display = "block";
    } else {
        // if not image shoe default avatar
        modalImage.style.display = "none";

        const modalBody = document.querySelector(".image-modal-body");
        const existingDefault = document.querySelector(".modal-default-avatar");

        if (!existingDefault) {
            const defaultDiv = document.createElement("div");
            defaultDiv.className = 'modal-default-avatar';
            defaultDiv.innerHTML = `<div style="width: 200px; height: 200px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 80px; color: white;">
                    ${username ? username.charAt(0).toUpperCase() : '?'}
                </div>
                <p style="color: white; margin-top: 1rem;">No profile picture set</p>`;

            modalBody.appendChild(defaultDiv)
        }
    }
    modal.style.display = "flex";
}

function closeImageModal() {
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    const defaultAvatar = document.querySelector(".modal-default-avatar");

    if (defaultAvatar) {
        defaultAvatar.remove();
    }

    modalImage.src = "";
    modal.style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("imageModal");
    const closeBtn = document.getElementById("closeModalBtn");
    const modalCloseBtn = document.getElementById("modalCloseBtn");

    if (closeBtn) {
        closeBtn.addEventListener("click", closeImageModal);
    }

    if (modalCloseBtn) {
        modalCloseBtn.addEventListener("click", closeImageModal);
    }

    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeImageModal();
            }
        });
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
            closeImageModal();
        }
    });
});