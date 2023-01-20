window.onload = () => {
    sessionStorage.clear();
}

async function register() {
    const login = document.getElementById('login');
    const password = document.getElementById('password');
    const section = document.getElementById('section');
    const data = {
        login: login.value,
        password: password.value,
        section: section.value
    }
    password.value = "";
    request = await fetch('http://127.0.0.1:8000/addUser', {
        'method': 'POST',
        'headers': {
        'Content-Type': 'application/json'},
        'body': JSON.stringify(data)});
    request = await request.json();
    if(request.result === "success") {
        const wait = document.getElementById('incorrect_pass');
        wait.textContent = "Request Received! Your Account will be created after Verification";
        wait.style.display = "block";
    } else {
        const error = document.getElementById('incorrect_pass');
        document.getElementById('password').value = "";
        error.textContent = "Entered Username or Password is Incorrect";
        error.style.display = "block";
    }
}