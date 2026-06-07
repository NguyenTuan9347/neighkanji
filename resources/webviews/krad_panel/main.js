function kradShow(kanji, neighbours) {
    const cards = document.getElementById('krad-cards');
    cards.innerHTML = '';

    neighbours.forEach(({ kanji: k, desc }, i) => {
        const card = document.createElement('div');
        card.className = 'krad-card';
        card.innerHTML = `
            <span class="krad-kanji">${k}</span>
            <div class="krad-divider"></div>
            <span class="krad-desc">${desc}</span>
        `;
        cards.appendChild(card);
    });
    document.getElementById('krad-panel').style.display = 'block';
}

function kradHide() {
    document.getElementById('krad-panel').style.display = 'none';
}

document.getElementById('krad-close-btn').addEventListener('click', kradHide);