// ===== Short helper =====
const $ = id => document.getElementById(id);

const msgInput = $('msgInput');
const sendBtn = $('sendBtn');
const clearBtn = $('clearBtn');
const regenBtn = $('regenBtn');
const senderSelect = $('senderSelect');
const messages = $('messages');
const copyBundle = $('copyBundle');

const showKeysBtn = $('showKeysBtn');
const hideKeysBtn = $('hideKeysBtn');
const keysView = $('keysView');
const drawerKeys = $('drawerKeys');
const bundleView = $('bundleView');

let lastBundle = null;

// Render message bubble in WA style
function renderMessage(text, who, encrypted) {
  const wrapper = document.createElement('div');

  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (who === 'me' ? 'me' : 'them');
  bubble.textContent = text;

  const encDiv = document.createElement('div');
  encDiv.className = 'enc-data';
  encDiv.textContent = encrypted;

  wrapper.appendChild(bubble);
  wrapper.appendChild(encDiv);

  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
}

// Escape HTML to avoid issues
function escapeHtml(str) {
  return str.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

// Copy encrypted bundle
copyBundle.addEventListener('click', () => {
  if(!lastBundle){
    alert("No bundle to copy");
    return;
  }
  navigator.clipboard.writeText(lastBundle);
  copyBundle.textContent = "Copied!";
  setTimeout(() => copyBundle.textContent = "Copy", 1500);
});

// Send message handler
sendBtn.addEventListener('click', async () => {

  const sender = senderSelect.value;  // alice or bob
  const text = msgInput.value.trim();

  if(!text) return alert("Type a message to send.");

  // Show outgoing message immediately (unencrypted)
  renderMessage(text, "me", "(encrypting...)");

  msgInput.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Sending...";

  const payload = {
    sender: sender,       // who sends
    plaintext: text       // message text
  };

  try {
    const res = await fetch('/api/send', {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });

    if(!res.ok){
      const errText = await res.text();
      throw new Error(errText);
    }

    const j = await res.json();
    const enc = j.bundle || "(no bundle)";
    const decoded = j.decrypted || "(no decrypted text)";

    lastBundle = enc;
    bundleView.textContent = enc;

    // Show incoming message bubble (decrypted)
    renderMessage(decoded, "them", enc);

  } catch(err){
    alert("Error: " + err.message);
    console.error(err);
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
  }
});

// Clear textarea
clearBtn.addEventListener('click', () => {
  msgInput.value = "";
});

// Regenerate RSA keys
regenBtn.addEventListener('click', async () => {
  if(!confirm("Regenerate keypairs on server?")) return;

  regenBtn.disabled = true;
  regenBtn.textContent = "Regenerating...";

  try {
    const res = await fetch('/api/regenerate-keys', { method:"POST" });
    if(!res.ok) throw new Error(await res.text());
    alert("Keys regenerated successfully!");
    keysView.textContent = "(keys regenerated)";
  } catch(err){
    alert("Error: " + err.message);
  } finally {
    regenBtn.disabled = false;
    regenBtn.textContent = "Regenerate keys";
  }
});

// Show keys
showKeysBtn.addEventListener('click', async () => {
  showKeysBtn.style.display = "none";
  hideKeysBtn.style.display = "inline-block";
  drawerKeys.style.display = "block";
  keysView.textContent = "Loading...";

  try {
    const res = await fetch('/api/keys');
    if(!res.ok) throw new Error(await res.text());
    const j = await res.json();

    let out = "";
    out += "Alice Public Key:\n" + (j.alice_pub || "") + "\n\n";
    out += "Alice Private Key:\n" + (j.alice_priv || "") + "\n\n";
    out += "Bob Public Key:\n" + (j.bob_pub || "") + "\n\n";
    out += "Bob Private Key:\n" + (j.bob_priv || "");

    keysView.textContent = out;

  } catch(err){
    keysView.textContent = "Error: " + err.message;
  }
});

// Hide keys
hideKeysBtn.addEventListener('click', () => {
  hideKeysBtn.style.display = "none";
  showKeysBtn.style.display = "inline-block";
  drawerKeys.style.display = "none";
  keysView.textContent = "";
});

// Ctrl+Enter sends message
msgInput.addEventListener('keydown', e => {
  if(e.key === "Enter" && (e.ctrlKey || e.metaKey)){
    sendBtn.click();
  }
});
