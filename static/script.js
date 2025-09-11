console.log("Loaded script.js v2");

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    // Add chat message bubble
    function addMessage(sender, text) {
        const div = document.createElement("div");
        div.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        div.innerHTML = text.replace(/\n/g, "<br>");
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Add product grid
    function addProducts(products) {
        if (!products || products.length === 0) return;

        const grid = document.createElement("div");
        grid.classList.add("product-grid");

        products.forEach(p => {
            const card = document.createElement("div");
            card.classList.add("product-card");
            card.innerHTML = `
                <div class="product-source">${p.source}</div>
                <img src="${p.thumbnail || '/static/placeholder.png'}" alt="${p.title}">
                <div class="product-title">${p.title}</div>
                <div class="product-price">${p.price}</div>
                <a href="${p.link}" target="_blank" class="product-link">View</a>
            `;
            grid.appendChild(card);
        });

        chatBox.appendChild(grid);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Add loading spinner
    function addSpinner() {
        const spinner = document.createElement("div");
        spinner.classList.add("spinner", "bot-message");
        spinner.innerHTML = `
            <div class="bounce1"></div>
            <div class="bounce2"></div>
            <div class="bounce3"></div>
        `;
        chatBox.appendChild(spinner);
        chatBox.scrollTop = chatBox.scrollHeight;
        return spinner;
    }

    // Form submit handler
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        addMessage("user", text);
        input.value = "";

        // show spinner
        const spinner = addSpinner();

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ user_message: text })
            });

            // remove spinner
            spinner.remove();

            if (!res.ok) {
                const err = await res.text();
                addMessage("bot", `Error ${res.status}: ${err}`);
                return;
            }

            const data = await res.json();
            addMessage("bot", data.bot_message);
            addProducts(data.products);
        } catch (err) {
            spinner.remove();
            addMessage("bot", "⚠️ Could not reach server.");
            console.error(err);
        }
    });
});

