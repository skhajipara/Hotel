document.addEventListener("DOMContentLoaded", () => {
    const message = document.body.dataset.flashMessage;
    
    // Check if a message exists and isn't empty or "None"
    if (message && message.trim() !== "" && message.trim() !== "None") {
        showToast(message);
    }
});

function showToast(message) {
    // 1. Create the notification element
    const toast = document.createElement("div");
    toast.innerHTML = message;
    
    // 2. Style it (you can move this to style.css if you prefer)
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #095B19; /* Matching your S.K. Hotels green */
        color: white;
        padding: 16px 24px;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        z-index: 9999;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-size: 15px;
        font-weight: 500;
        opacity: 0;
        transform: translateY(-20px);
        transition: opacity 0.4s ease, transform 0.4s ease;
    `;
    
    document.body.appendChild(toast);
    
    // 3. Trigger the slide-in animation
    setTimeout(() => {
        toast.style.opacity = "1";
        toast.style.transform = "translateY(0)";
    }, 10);
    
    // 4. Fade out and remove after 3.5 seconds
    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-20px)";
        setTimeout(() => toast.remove(), 400); // Wait for animation to finish before removing
    }, 3500);
}