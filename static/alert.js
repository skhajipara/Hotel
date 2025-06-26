document.addEventListener("DOMContentLoaded", () => {
    const message = document.body.dataset.flashMessage;
    if (message) {
        alert(message);
    }
})