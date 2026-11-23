const dateElement = document.getElementById("today-date");

if (dateElement) {
    dateElement.textContent = new Intl.DateTimeFormat(undefined, {
        weekday: "long",
        month: "long",
        day: "numeric"
    }).format(new Date());
}

const searchInput = document.getElementById("entry-search");

if (searchInput) {
    const entries = Array.from(document.querySelectorAll(".searchable-entry"));
    const emptyMessage = document.querySelector(".search-empty");

    searchInput.addEventListener("input", () => {
        const searchTerm = searchInput.value.trim().toLocaleLowerCase();
        let visibleEntries = 0;

        entries.forEach((entry) => {
            const matches = entry.dataset.searchEntry.includes(searchTerm);
            entry.hidden = !matches;
            visibleEntries += Number(matches);
        });

        emptyMessage.hidden = visibleEntries !== 0 || entries.length === 0;
    });
}

const review = document.querySelector("[data-flashcard-review]");

if (review) {
    const cards = Array.from(review.querySelectorAll("[data-flashcard]"));
    const controls = review.querySelector(".flashcard-controls");
    const emptyMessage = review.querySelector(".review-empty");
    const progress = review.querySelector(".flashcard-progress");
    let activeIndex = 0;

    if (cards.length > 0) {
        controls.hidden = false;
        emptyMessage.hidden = true;

        const showCard = (index) => {
            activeIndex = (index + cards.length) % cards.length;

            cards.forEach((card, cardIndex) => {
                card.hidden = cardIndex !== activeIndex;
                const answer = card.querySelector(".flashcard-answer");
                const revealButton = card.querySelector(".reveal-answer");
                answer.hidden = true;
                revealButton.textContent = "Reveal answer";
            });

            progress.textContent = `${activeIndex + 1} of ${cards.length}`;
        };

        review.addEventListener("click", (event) => {
            const target = event.target;

            if (target.closest(".reveal-answer")) {
                const card = cards[activeIndex];
                const answer = card.querySelector(".flashcard-answer");
                const revealButton = card.querySelector(".reveal-answer");
                answer.hidden = !answer.hidden;
                revealButton.textContent = answer.hidden ? "Reveal answer" : "Hide answer";
            }

            if (target.closest("[data-previous-card]")) {
                showCard(activeIndex - 1);
            }

            if (target.closest("[data-next-card]")) {
                showCard(activeIndex + 1);
            }

            if (target.closest("[data-shuffle-cards]")) {
                for (let index = cards.length - 1; index > 0; index--) {
                    const randomIndex = Math.floor(Math.random() * (index + 1));
                    [cards[index], cards[randomIndex]] = [cards[randomIndex], cards[index]];
                }

                cards.forEach((card) => review.insertBefore(card, controls));
                showCard(0);
            }
        });

        showCard(0);
    } else {
        emptyMessage.hidden = false;
    }
}

const timerElement = document.getElementById("timer");

if (timerElement) {
    const startButton = document.getElementById("start");
    const breakButton = document.getElementById("start-break");
    const pauseButton = document.getElementById("stop");
    const resetButton = document.getElementById("reset");
    const statusElement = document.getElementById("timer-status");
    const sessionCountElement = document.getElementById("session-count");
    const progressElement = document.getElementById("timer-progress");
    const focusDuration = document.getElementById("focus-duration");
    const breakDuration = document.getElementById("break-duration");

    let remainingSeconds = Number(focusDuration.value);
    let sessionLength = remainingSeconds;
    let timerInterval = null;
    let completedSessions = 0;
    let activeMode = "focus";

    const updateTimerDisplay = () => {
        const minutes = Math.floor(remainingSeconds / 60);
        const seconds = remainingSeconds % 60;

        timerElement.textContent =
            `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
        progressElement.max = sessionLength;
        progressElement.value = sessionLength - remainingSeconds;
    };

    const stopTimer = () => {
        window.clearInterval(timerInterval);
        timerInterval = null;
    };

    const startSession = (mode) => {
        stopTimer();
        if (mode !== activeMode || remainingSeconds === 0) {
            activeMode = mode;
            sessionLength = Number(mode === "focus" ? focusDuration.value : breakDuration.value);
            remainingSeconds = sessionLength;
        }

        statusElement.textContent = activeMode === "focus" ? "Focus session" : "Break";
        updateTimerDisplay();

        timerInterval = window.setInterval(() => {
            remainingSeconds -= 1;
            updateTimerDisplay();

            if (remainingSeconds === 0) {
                stopTimer();

                if (activeMode === "focus") {
                    completedSessions += 1;
                    sessionCountElement.textContent =
                        `Focus sessions completed: ${completedSessions}`;
                    statusElement.textContent = "Focus session complete. Take a break when you are ready.";
                } else {
                    statusElement.textContent = "Break complete. Start a focus session when you are ready.";
                }
            }
        }, 1000);
    };

    const resetSession = () => {
        stopTimer();
        sessionLength = Number(activeMode === "focus" ? focusDuration.value : breakDuration.value);
        remainingSeconds = sessionLength;
        statusElement.textContent = activeMode === "focus" ? "Focus session" : "Break";
        updateTimerDisplay();
    };

    const pauseSession = () => {
        stopTimer();
        statusElement.textContent = "Paused";
    };

    startButton.addEventListener("click", () => startSession("focus"));
    breakButton.addEventListener("click", () => startSession("break"));
    pauseButton.addEventListener("click", pauseSession);
    resetButton.addEventListener("click", resetSession);

    focusDuration.addEventListener("change", () => {
        if (activeMode === "focus" && timerInterval === null) {
            resetSession();
        }
    });

    breakDuration.addEventListener("change", () => {
        if (activeMode === "break" && timerInterval === null) {
            resetSession();
        }
    });

    updateTimerDisplay();
}
