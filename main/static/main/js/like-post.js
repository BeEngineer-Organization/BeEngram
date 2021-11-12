!function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const likeIcons = document.getElementsByClassName("like");
    const csrftoken = getCookie('csrftoken');
    for (let i = 0, l = likeIcons.length; i < l; ++i) {
        const icon = likeIcons[i];
        icon.addEventListener("click", function () {
            const postPk = icon.getAttribute("data-pk");
            url = `/like/${postPk}`;
            const xhr = new XMLHttpRequest();
            xhr.open("POST", url, true);
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.onload = function (e) {
                if (xhr.readyState === 4) {
                    result = JSON.parse(xhr.responseText)
                  if (xhr.status === 200 && result["result"] === "success") {
                    icon.classList.toggle("like--active");
                  }
                }
              };
            xhr.send();
        });
    }
}();
