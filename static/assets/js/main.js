
customElements.define('my-message',
    class extends HTMLElement {
        constructor() {
            // 必须调用 super();
            super();
            const template = document.getElementById('my-message');
            const templateContent = template.content;

            const shadowRoot = this.attachShadow({ mode: 'open' }).appendChild(
                templateContent.cloneNode(true)
            );
        }
    }
);

function timestamp2string(timestamp) {
    // 时间戳转字符串
    let date = new Date(timestamp);
    let yyyy = date.getFullYear();
    let MM = date.getMonth() + 1;
    if (MM < 10) MM = "0" + MM;
    let dd = date.getDate();
    if (dd < 10) dd = "0" + dd;
    let HH = date.getHours();
    if (HH < 10) HH = "0" + HH;
    let mm = date.getMinutes();
    if (mm < 10) mm = "0" + mm;
    let ss = date.getSeconds();
    if (ss < 10) ss = "0" + ss;
    return yyyy + "-" + MM + "-" + dd + " " + HH + ":" + mm + ":" + ss;
}

function setPublishButtonIsDoing(status) {
    // 设置PublishButton按钮状态
    if (status) {
        document.getElementById("publishButton").disabled = true;
        document.getElementById("publishButton").innerHTML = "发布中...";
    } else {
        document.getElementById("publishButton").disabled = false;
        document.getElementById("publishButton").innerHTML = "发布";
    }
}

function publish() {
    // 发布新留言

    content = document.getElementById("newMessageTextarea").value;
    author = document.getElementById("authorInput").value;

    if (content.trim() == "") {
        alert("必须输入内容！");
        return;
    }

    if (author.trim() == "") {
        alert("必须输入作者！");
        return;
    }

    setPublishButtonIsDoing(true);

    fetch("api/messages", {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json'
        }),
        body: JSON.stringify({"author": author, "content": content}),
    })
    .then(response => response.json())
    .then(result => {
        setPublishButtonIsDoing(false);
        if (result.status == "success") {
            alert("留言成功！");
            location.reload();
        } else {
            alert("留言失败，请刷新页面后重试！");
        }
    })
    .catch (error => {
        setPublishButtonIsDoing(false);
        alert("发生错误，请刷新页面后重试！");
    });
}


function setMessagesIsShow(status) {
    if (status) {
        document.getElementById("passwordDiv").style.display = "none";
        document.getElementById("messagesDiv").style.display = "";
    } else {
        document.getElementById("passwordDiv").style.display = "";
        document.getElementById("messagesDiv").style.display = "none";
    }
}

function showMessages(data) {

    let messagesDiv = document.getElementById("messagesDiv");

    for (item of data["items"]) {
        messagesDiv.innerHTML += "<my-message class='w-3/4 sm:w-1/2 mb-4'>\n\
        <p style='word-wrap:break-word;word-break:break-all;white-space:pre-wrap;' slot='my-text'>" + item["content"] + "</p>\n\
        <span slot='my-floor'>" + "#" + item["id"] + "</span>\n\
        <span slot='my-time'>" + item["author"] + " " + timestamp2string(item["time"]*1000) + "</span>\n\
        </my-message>"
    }
}


function getMessages() {
    /*sendJson("get", "/api/messages", undefined, showMessages);*/
    fetch("api/messages") // GET
    .then(response => response.json())
    .then(result => {
        if (result.status == "success") {
            setMessagesIsShow(true);
            showMessages(result);
        } else {
            setMessagesIsShow(false);
        }
    })
    .catch (error => {
        setMessagesIsShow(false);
        alert("发生错误，请刷新页面后重试！");
    });
}


function sendJson(method, url, postData, callback) {
    // 自己把post json封装了一下
    // 已弃用
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-type', 'application/json');

    // 监听返回值
    xhr.onreadystatechange = function () {
        if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
            let data = JSON.parse(xhr.responseText);     // 获取返回的数据
            callback(data, xhr.status);
        } else if (xhr.readyState == 4 && xhr.status != 200) {
            callback(null, xhr.status);
        }
    }
    xhr.send(JSON.stringify(postData));
}

function enter() {
    // 按了进入按钮
    let passwordInput = document.getElementById("passwordInput");
    let passwordButton = document.getElementById("passwordButton");

    passwordButton.disabled = true;
    fetch("api/token", {
        method: 'POST',
        headers: new Headers({'Content-Type': 'application/json'}),
        body: JSON.stringify({ "password": passwordInput.value }),
    })
    .then(response => response.json())
    .then(result => {
        passwordButton.disabled = false;
        if (result.status == "success") {
            getMessages();
        } else {
            alert("密码错误！");
        }
    })
    .catch (error => {
        passwordButton.disabled = false;
        alert("发生错误，请刷新页面后重试！");
    });
    /*
    let callback = function (data, code) {
        if (code != 200) {
            alert("密码错误！");
        } else {
            getMessages();
        }
    }
    sendJson("post", "/api/token", { "password": elem.value }, callback);
    */
}

function bodyLoad() {
    // 窗口加载时
    getMessages();
}
