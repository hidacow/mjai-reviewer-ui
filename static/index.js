function setRandomLobby() {
  var randomLobby = Math.floor(Math.random() * (9999 - 1000 + 1)) + 1000;
  document.getElementById("roomid").value = randomLobby;
}

function updateQuantity() {
  const bot1 = document.getElementById("bot1").value;
  // const bot2 = document.getElementById("bot2").value;
  var res = 1;
  if (bot1.length > 0) {
    res += 1;
  }
  // if (bot2.length > 0) {
  //   res += 1;
  // }
  document.getElementById("selected-quantity").textContent = `${res}`;
}

async function getAvailableBots() {
  const response = await fetch("/available-bots").then((r) => r.json());
  const available = response.available;
  const total = response.total;
  const label = document.getElementById("ab");
  if (available > 0) {
    label.innerHTML = `<span style="font-weight: bold; color: green">${available}</span> / ${total}`;
  } else {
    if (total <= 0) {
      label.innerHTML = `<span class="strong">N/A</span>`;
    } else {
      label.innerHTML = `<span class="strong">0</span> / ${total}`;
    }
  }
}

function onTurnstileReview() {
  document.getElementById("submitBtnReview").disabled = false;
}

function onTurnstileDispatch() {
  document.getElementById("submitBtnDispatch").disabled = false;
}

function onloadTurnstileCallback() {
  document.getElementById("submitBtnReview").disabled = true;
  document.getElementById("submitBtnDispatch").disabled = true;
}

function init() {
  getAvailableBots();
  setInterval(() => {
    if (!document.hidden) {
      getAvailableBots();
    }
  }, 30_000);
}

if (
  document.readyState === "interactive" ||
  document.readyState === "complete"
) {
  setTimeout(init, 1);
} else {
  document.addEventListener("DOMContentLoaded", init);
}
