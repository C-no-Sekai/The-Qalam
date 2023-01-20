window.onload = () => {
    sessionStorage.clear();
}
let validate = async function() {
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;
    const data = {
        login: login,
        password: password
    }
    let response = await fetch("http://127.0.0.1:8000/validate",
    {
        'method': 'POST',
        'headers': {
        'Content-Type': 'application/json'},
        'body': JSON.stringify(data)
    });
    response = await response.json();
    console.log(response);
    if (response.result === "success") {
        sessionStorage.setItem('username', data.login);
        window.location.href = "activities.html"
        document.getElementById("custom_message").textContent = "Welcome!! "+response.name
    } else {
        const error = document.getElementById('incorrect_pass');
        document.getElementById('password').value = "";
        error.textContent = "Entered Username or Password is Incorrect";
        error.style.display = "block";
    }
}

let register = () => {

    const login = document.getElementById('login'); 
    const password = document.getElementById('password');
    const remember = document.getElementById('checkbox');
    const data = {
        login: login.value,
        password: password.value
    }
    password.value = "";
    const wait = document.getElementById('incorrect_pass');
    wait.textContent = "Request Received! Your Account will be created after Verification";
    wait.style.display = "block";
}