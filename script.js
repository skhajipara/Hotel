document.addEventListener('DOMContentLoaded', () => {

    // --- HOME PAGE SPECIFIC LOGIC ('Kathiyawad.html') ---
    

        // Header Login/Logout Button Logic
        const headerControls = document.getElementById('header-controls');
        const currentUser = JSON.parse(sessionStorage.getItem('currentUser'));
        if (currentUser) {
            headerControls.innerHTML = `
                <span id="welcome-user">Welcome, ${currentUser.name}!</span>
                <button id="logout-btn">Logout</button>
            `;
            const logoutBtn = document.getElementById('logout-btn');
            logoutBtn.addEventListener('click', () => {
                sessionStorage.removeItem('currentUser');
                window.location.href = 'login.html';
            });
        } else {
            headerControls.innerHTML = '<a href="login.html">Login</a>';
        }
    

    // --- USER AUTHENTICATION FORMS ---
    // Handle Login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('Email').value;
            const password = document.getElementById('Password').value;
            const users = JSON.parse(localStorage.getItem('users')) || [];
            const user = users.find(u => u.email === email && u.password === password);
            if (user) {
                sessionStorage.setItem('currentUser', JSON.stringify(user));
                const message = encodeURIComponent('✅ Login successful!');
                window.location.href = `Kathiyawad.html?message=${message}`;
            } else {
                // We show a simple alert here because the user is not leaving the page
                alert('❌ Incorrect email or password.');
            }
        });
    }
    
    // (Other forms like signup, password recovery, etc. remain the same)
    
    // --- BOOKING AND ORDERS LOGIC ---
    const checkLogin = () => {
        const currentUser = sessionStorage.getItem('currentUser');
        if (!currentUser) {
            window.location.href = 'login.html';
            return null;
        }
        return JSON.parse(currentUser);
    };

    // Handle Table Booking Form
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!checkLogin()) return;
            const message = encodeURIComponent('✅ Table booked successfully!');
            window.location.href = `Kathiyawad.html?message=${message}`;
        });
    }

    // Handle other forms similarly...
    const roomForm = document.getElementById('room-booking-form');
    if (roomForm) {
        roomForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!checkLogin()) return;
            const message = encodeURIComponent('✅ Room booked successfully!');
            window.location.href = `Kathiyawad.html?message=${message}`;
        });
    }
    
    const orderForm = document.getElementById('order-form');
    if (orderForm) {
        orderForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!checkLogin()) return;
            const message = encodeURIComponent('✅ Your order has been placed!');
            window.location.href = `Kathiyawad.html?message=${message}`;
        });
    }

    const deliveryForm = document.getElementById('delivery-form');
    if (deliveryForm) {
        deliveryForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!checkLogin()) return;
            const message = encodeURIComponent('✅ Your delivery order is confirmed!');
            window.location.href = `Kathiyawad.html?message=${message}`;
        });
    }
    
    // (Ensure you have the form handling for signup, forget password etc. from the first JS response if you need them)
});