function startLogging() {
    eel.start_logging()(function (msg) {
        document.getElementById("status")?.innerText = "Status: " + msg;
        console.log(msg);
    });
}

function stopLogging() {
    eel.stop_logging()(function (msg) {
        document.getElementById("status")?.innerText = "Status: " + msg;
        console.log(msg);
    });
}

// Optional: function to show logs in keylogger.html
function fetchLogs() {
    // This function assumes you've exposed something like eel.get_logs() in Python
    // You'd have to implement it in main.py
    eel.get_logs()(function (logs) {
        const logList = document.getElementById("log-list");
        logList.innerHTML = "";
        logs.forEach(log => {
            const li = document.createElement("li");
            li.textContent = log;
            logList.appendChild(li);
        });
    });
}
