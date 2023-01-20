window.onload = () => {get_terms()}
let get_terms = () => {
    // Get term List from API
    // let response = fetch("http://127.0.0.1:8000/",
    // {
    //     'method': 'GET',
    //     'headers': {
    //     'Content-Type': 'application/json'},
    // });
    // terms = response.json();
    let terms = ['Fall 2021', 'Spring 2021', 'Fall 2022', 'Spring 2022', 'Fall 2023', 'Spring 2023'];
    const display_list = document.getElementById('terms');
    new_html = "";
    terms.forEach(element => {
        new_html += `<li class="d-inline mx-auto py-3"><input class="terms_radio" type="radio" name="radAnswer" onclick="update_table()"/>${element}</li>`;
    });
    display_list.innerHTML = new_html;
}

let update_table = () => {
    const btns = document.getElementsByClassName('terms_radio');
    for (let index=0; index < btns.length; index++) {
        if (btns[index].checked) {
            // Use this to get results of table from API
            console.log(btns[index].nextSibling.textContent)

            btns[index].addEventListener('click', ()=>{});
        } else {
            btns[index].addEventListener('click', update_table);
        }
    }
    // Results From API fetched, now draw table
    results = fetch("http://example.com/", {
        'method': 'POST',
        'headers': {
        'Content-Type': 'application/json'},
    })

    results = [
        {
            code: 'HUMA-1200',
            quiz: 12.5,
            assignment: 12.5,
            lab: 10,
            project: 10,
            oht: 30,
            final: 20,
            aggregate: 25,
            students: 10,
            predicted: 'B',
            drop: 35.5,
            rise: 12.5,
            actual: 'B',
        },
        {
            code: 'HUMA-1300',
            quiz: 12.5,
            assignment: 12.5,
            lab: 10,
            project: 10,
            oht: 30,
            final: 20,
            aggregate: 25,
            students: 10,
            predicted: 'B',
            drop: 35.5,
            rise: 12.5,
            actual: 'B',
        }
    ]

    new_html = ""
    results.forEach(subject => {
        new_html += `
        <tr>
        <td>${subject.code}</td>
        <td>${subject.quiz}</td>
        <td>${subject.assignment}</td>
        <td>${subject.lab}</td>
        <td>${subject.project}</td>
        <td>${subject.oht}</td>
        <td>${subject.final}</td>
        <td>${subject.aggregate}</td>
        <td>${subject.students}</td>
        <td>${subject.predicted}</td>
        <td>${subject.drop}</td>
        <td>${subject.rise}</td>
        <td>${subject.actual}</td>
        <td><button class='edit_btn btn btn-danger' onclick='edit_record(this)' id=${subject.code}>Edit</button></td>
        </tr>

        `
    })
    const my_table = document.getElementById('table_body');
    my_table.innerHTML = new_html;
}
let save_record = (btn) => {
    let sum = 0;
    const fields = document.getElementsByClassName('editable-field');
    for (let i = 0; i < fields.length; i++) {
        sum += parseFloat(fields[i].value);
    }
    if (sum !== 100) {
        alert("The sum of the fields must be equal to 100!");
        return
    } 
    
    btn.setAttribute('class', 'edit_btn btn btn-danger')
    const btns_ = document.getElementsByClassName('edit_btn');
    for (let index=0; index < btns_.length; index++) btns_[index].setAttribute('onclick', 'edit_record(this)');
    
    btn.textContent = 'Edit';

    const final = document.getElementById('final1');
    const oht = document.getElementById('oht1');
    const project = document.getElementById('project1');
    const lab = document.getElementById('lab1');
    const assign = document.getElementById('assign1');
    const quiz = document.getElementById('quiz1');

    const aggregate = final.parentElement.nextElementSibling;
    const predicted = aggregate.nextElementSibling.nextElementSibling;
    const drop = predicted.nextElementSibling;
    const rise = drop.nextElementSibling;

    // Send the data to API
    final_score = final.value;
    oht_score = oht.value;
    project_score = project.value;
    lab_score = lab.value;
    assign_score = assign.value;
    quiz_score = quiz.value;
    
    const btns = document.getElementsByClassName('terms_radio');
    let index=0
    for (; index < btns.length; index++) {
        if (btns[index].checked) {
            break;
        }
    }
    term = btns[index].nextSibling.textContent
    subject = quiz.parentElement.previousElementSibling.textContent
    // New set of data received from server have to send values for term and subject name for recal
    // Will be in the form of keypairs again
    response = {quiz:quiz_score, assign:assign_score, lab:lab_score, project:project_score,
    oht:oht_score, final:final_score, aggregate:10, predicted:12, drop:23, rise:24};
    
    final.parentElement.innerHTML=response.final;
    oht.parentElement.innerHTML=response.oht;
    project.parentElement.innerHTML = response.project;
    assign.parentElement.innerHTML = response.assign;
    quiz.parentElement.innerHTML = response.quiz;
    lab.parentElement.innerHTML = response.lab;
    predicted.innerHTML = response.predicted;
    aggregate.innerHTML = response.aggregate;
    drop.innerHTML = response.drop;
    rise.innerHTML = response.rise;
}


let edit_record = (btn) => {
    btn.textContent = "Save";

    // Disable the other editors
    const btns = document.getElementsByClassName('edit_btn')
    for (let index=0; index < btns.length; index++) {
        btns[index].setAttribute('onclick', '');
    }
 
    // Start Save Listener
    btn.setAttribute('onclick', 'save_record(this)');
    btn.setAttribute('class', 'save_btn btn btn-success');

    const temp = btn.parentNode.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling.previousElementSibling;

    const final = temp.previousElementSibling;
    const oht = final.previousElementSibling;
    const project = oht.previousElementSibling;
    const lab = project.previousElementSibling;
    const assign = lab.previousElementSibling;
    const quiz = assign.previousElementSibling;
    
    oht.innerHTML = `<input type='number' id='oht1' value=${oht.textContent} style="width: 4vw;" \>`
    project.innerHTML = `<input type='number' id='project1' value=${project.textContent} style="width: 4vw;" \>`
    lab.innerHTML = `<input type='number' id='lab1' value=${lab.textContent} style="width: 4vw;" \>`
    final.innerHTML = `<input type='number' id='final1' value=${final.textContent} style="width: 4vw;" \>`
    assign.innerHTML = `<input type='number' id='assign1' value=${assign.textContent} style="width:4vw;" \>`
    quiz.innerHTML = `<input type='number' id='quiz1' value=${quiz.textContent} style="width: 4vw;" \>`

}
