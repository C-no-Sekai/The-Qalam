let validate = async function() {

    const login = document.getElementById('login');
    const password = document.getElementById('password');
    const remember = document.getElementById('checkbox');

    const data = {
        login: login.value,
        password: password.value
    }

    // Clear password
    password.value = "";

    // Verify Entered Details via API
    // let response = await fetch("http://127.0.0.1:8000/",
    // {
    //     'method': 'POST',
    //     'mode': 'no-cors',
    //     // 'headers': {
    //     //     'Accept': 'appliction.json',
    //     //     'Content-Type': 'application/json',
    //     //     // 'login': login.value,
    //     //     // 'password': password.value
    //     // },
    //     'body': JSON.stringify(data)
    // })
    // console.log(response)

    // Assume API response received will have name and result
    response = true;

    if (response) {
        // move to next screen
        window.location.href = "activities.html"
        document.getElementById("custom_message").textContent = "Welcome!! {NAME}"
    } else {
        // Display incorrect pass message
        const error = document.getElementById('incorrect_pass');
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

    // Clear password
    password.value = "";

    // Initiaite register request

    // Display wait message
    const wait = document.getElementById('incorrect_pass');
    wait.textContent = "Request Received! Your Account will be created after Verification";
    wait.style.display = "block";
}