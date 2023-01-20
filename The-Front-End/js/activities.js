let fill_forms = () => {
    // From this point launch the script and redirect to success page also add the name in whitelist to prevent abuse
    window.location.href = "form_success.html"
}
let aggregate = () => {
    // From this point launch aggregate receiver
    window.location.href = "aggregates.html"
}
window.onload=()=>{
    let username = sessionStorage.getItem('username');
    if (username === null) {
        window.location.href = "index.html"
    }
    document.getElementById('username_session').innerHTML = `<h3 class="username_session_name text-white">Welcome ${username}</h3>`;

}
