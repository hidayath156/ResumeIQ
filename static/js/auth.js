const authTabs = document.querySelectorAll('.auth-tabs button');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const msg = document.getElementById('authMsg');

authTabs.forEach(button => {
    button.onclick = () => {
        authTabs.forEach(tab => tab.classList.remove('active'));

        button.classList.add('active');

        loginForm.classList.toggle(
            'hidden',
            button.dataset.auth !== 'login'
        );

        registerForm.classList.toggle(
            'hidden',
            button.dataset.auth !== 'register'
        );

        msg.textContent = '';
    };
});

loginForm.onsubmit = async e => {
    e.preventDefault();
    msg.textContent = '';

    try {
        await api('/api/login', {
            method: 'POST',
            body: JSON.stringify(
                Object.fromEntries(new FormData(loginForm))
            )
        });

        location = '/dashboard';
    } catch (x) {
        msg.textContent = x.message;
    }
};

registerForm.onsubmit = async e => {
    e.preventDefault();
    msg.textContent = '';

    const d = Object.fromEntries(
        new FormData(registerForm)
    );

    const email = /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/.test(
        d.email
    );

    const pass = d.password;

    const ok =
        pass.length >= 8 &&
        /[A-Z]/.test(pass) &&
        /[a-z]/.test(pass) &&
        /\d/.test(pass) &&
        /[^A-Za-z0-9]/.test(pass);

    if (!email) {
        msg.textContent =
            'Enter a valid email address such as name@example.com.';
        return;
    }

    if (!ok) {
        msg.textContent =
            'Password must be at least 8 characters and include uppercase, lowercase, number and special character.';
        return;
    }

    if (pass !== d.confirm_password) {
        msg.textContent = 'Passwords do not match.';
        return;
    }

    try {
        await api('/api/register', {
            method: 'POST',
            body: JSON.stringify(d)
        });

        location = '/dashboard';
    } catch (x) {
        msg.textContent = x.message;
    }
};