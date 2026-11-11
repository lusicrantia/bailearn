
const start = document.getElementById("start");
const stop = document.getElementById("stop");
const reset = document.getElementById("reset");
const timer = document.getElementById("timer");

let timeleft = 1500;
let interval = null;

const updateTimer = () => {
    const minutes = Math.floor(timeleft / 60);
    const seconds = timeleft % 60;

    timer.textContent =
        `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
};

const startTimer = () => {
    if (interval !== null) return;

    interval = setInterval(() => {
        if (timeleft > 0) {
            timeleft--;
            updateTimer();
        }

        if (timeleft === 0) {
            clearInterval(interval);
            interval = null;
            alert("TIME'S UP!");
        }
    }, 1000);
};

const stopTimer = () => {
    clearInterval(interval);
    interval = null;
};

const resetTimer = () => {
    clearInterval(interval);
    interval = null;

    timeleft = 1500;
    updateTimer();
};

start.addEventListener("click", startTimer);
stop.addEventListener("click", stopTimer);
reset.addEventListener("click", resetTimer);

updateTimer();
