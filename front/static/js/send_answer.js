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

$(document).ready(function() {
    $('.answer-form').submit(function(e) {
        e.preventDefault();
        const question_id = $('.question').attr('data-id')
        const answer_text = $('#id_text').val();

        $.ajax({
            url: `/send_answer/${question_id}/`,
            type: 'POST',
            data: {
                text: answer_text,
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            success: function(response) {
                $('#id_text').val('');
            }
        });
    });
});