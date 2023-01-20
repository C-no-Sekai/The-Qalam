window.onload = () => {
    let username = sessionStorage.getItem('username');
    if (username === null) {
        window.location.href = "index.html"
    }
    let response = fetch("http://127.0.0.1:8000/fillForms", {
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json'},
            'body': JSON.stringify({login: username})
    })
}
let go_back = () => {
    window.location.href = "activities.html"
}
