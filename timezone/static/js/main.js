document.addEventListener("DOMContentLoaded", function () {
    // Hide loader
    const loader = document.getElementById("page-loader");
    if (loader) {
        setTimeout(() => loader.classList.add("hidden"), 250);
    }

    // Back to top button
    const backToTop = document.getElementById("backToTop");
    if (backToTop) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 300) {
                backToTop.classList.add("show");
            } else {
                backToTop.classList.remove("show");
            }
        });
        backToTop.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }

    // Auto-hide toasts
    document.querySelectorAll(".toast").forEach(function (toastEl) {
        setTimeout(() => {
            toastEl.classList.remove("show");
        }, 5000);
    });

    // Bootstrap form validation styling for the buy modal
    const buyModal = document.getElementById("buyModal");
    if (buyModal) {
        const form = buyModal.querySelector("form");
        form.addEventListener("submit", function () {
            const submitBtn = form.querySelector("button[type=submit]");
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Placing order...';
        });
    }
});
