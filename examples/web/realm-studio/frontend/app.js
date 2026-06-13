async function fetchState() {
  const status = document.getElementById("status");
  const pre = document.getElementById("snapshot");
  status.textContent = "Fetching…";
  try {
    const res = await fetch("/api/state");
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    pre.textContent = JSON.stringify(data, null, 2);
    status.textContent = `OK — turn ${data.session_turn}, active ${data.active_agent_id}`;
  } catch (err) {
    pre.textContent = String(err);
    status.textContent = "Error";
  }
}

document.getElementById("refresh").addEventListener("click", fetchState);
fetchState();
