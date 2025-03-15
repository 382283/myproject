document.addEventListener("DOMContentLoaded", function() {
    const title = document.getElementById("fade-in-title");
    if (title) {
        title.style.opacity = "0";
        title.style.transform = "translateY(20px)";
        title.style.transition = "opacity 2s ease-in-out, transform 2s ease-in-out";

        setTimeout(() => {
            title.style.opacity = "1";
            title.style.transform = "translateY(0)";
        }, 100);
    }
});
