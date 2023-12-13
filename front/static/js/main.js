function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function get_request(url, formData) {
    return new Request(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    });
}

function send_request(request, text, item) {
    fetch(request)
        .then((response) => response.json())
        .then((data) => {
            text.innerHTML = `likes: ${data.likes}`;
            let [span_like, span_dislike] = item.children[1].children;
            if (data.result == 0) {
                span_like.style = "visibility: hidden;";
                span_dislike.style = "visibility: hidden;";
            } else if (data.result == 1) {
                span_like.style = "";
                span_dislike.style = "visibility: hidden;";
            } else {
                span_like.style = "visibility: hidden;";
                span_dislike.style = "";
            }
        })
}

const like_items = document.getElementsByClassName('question-likes');

for (let item of like_items) {
    const [ text, like, dislike ] = item.children[0].children;

    like.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('question_id', like.dataset.id);
        formData.append('mark', 1);

        const request = get_request('/question_like/', formData);
        send_request(request, text, item)
    })

    dislike.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('question_id', like.dataset.id);
        formData.append('mark', -1);

        const request = get_request('/question_like/', formData);
        send_request(request, text, item)
    })
}

const answer_items = document.getElementsByClassName('answer-likes');

for (let item of answer_items) {
    const [ text, like, dislike ] = item.children[0].children;

    like.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('answer_id', like.dataset.id);
        formData.append('mark', 1);

        const request = get_request('/answer_like/', formData);
        send_request(request, text, item)
    })

    dislike.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('answer_id', like.dataset.id);
        formData.append('mark', -1);

        const request = get_request('/answer_like/', formData);
        send_request(request, text, item)
    })
}

const answer_switches = document.getElementsByClassName('form-check-input');

for (let switcher of answer_switches) {
    switcher.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('answer_id', switcher.dataset.id);

        const request = get_request('/answer_right/', formData);
        fetch(request)
    })
}