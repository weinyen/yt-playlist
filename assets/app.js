(() => {
  const BATCH_SIZE = 60;

  const grid = document.getElementById("grid");
  const searchInput = document.getElementById("search");
  const sentinel = document.getElementById("sentinel");
  const emptyMessage = document.getElementById("empty-message");
  const visibleCountEl = document.getElementById("visible-count");
  const totalCountEl = document.getElementById("total-count");

  let allItems = [];
  let filtered = [];
  let renderedCount = 0;

  const playBadgeSvg = `
    <svg viewBox="0 0 68 48" xmlns="http://www.w3.org/2000/svg">
      <path d="M66.52 7.74c-.78-2.93-2.49-5.41-5.42-6.19C55.79.13 34 0 34 0S12.21.13 6.9 1.55
        c-2.93.78-4.64 3.26-5.42 6.19C.06 13.05 0 24 0 24s.06 10.95 1.48 16.26c.78 2.93 2.49 5.41
        5.42 6.19C12.21 47.87 34 48 34 48s21.79-.13 27.1-1.55c2.93-.78 4.64-3.26 5.42-6.19
        C67.94 34.95 68 24 68 24s-.06-10.95-1.48-16.26z" fill="#212121" fill-opacity=".8"/>
      <path d="M45 24 27 14v20" fill="#fff"/>
    </svg>`;

  function buildCard(item) {
    const a = document.createElement("a");
    a.className = "card";
    a.href = item.url;
    a.target = "_blank";
    a.rel = "noopener noreferrer";

    const thumbWrap = document.createElement("div");
    thumbWrap.className = "thumb-wrap";

    const img = document.createElement("img");
    img.src = `https://i.ytimg.com/vi/${item.id}/mqdefault.jpg`;
    img.alt = "";
    img.loading = "lazy";
    img.decoding = "async";
    thumbWrap.appendChild(img);

    const badge = document.createElement("div");
    badge.className = "play-badge";
    badge.innerHTML = playBadgeSvg;
    thumbWrap.appendChild(badge);

    const titleEl = document.createElement("div");
    const hasTitle = Boolean(item.title);
    titleEl.className = "card-title" + (hasTitle ? "" : " untitled");
    titleEl.textContent = hasTitle ? item.title : "(タイトル未取得の動画)";

    a.appendChild(thumbWrap);
    a.appendChild(titleEl);
    return a;
  }

  function renderNextBatch() {
    const end = Math.min(renderedCount + BATCH_SIZE, filtered.length);
    const fragment = document.createDocumentFragment();
    for (let i = renderedCount; i < end; i++) {
      fragment.appendChild(buildCard(filtered[i]));
    }
    grid.appendChild(fragment);
    renderedCount = end;
    visibleCountEl.textContent = filtered.length;
  }

  function resetAndRender(items) {
    filtered = items;
    grid.innerHTML = "";
    renderedCount = 0;
    emptyMessage.hidden = filtered.length !== 0;
    if (filtered.length > 0) {
      renderNextBatch();
    } else {
      visibleCountEl.textContent = 0;
    }
  }

  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && renderedCount < filtered.length) {
      renderNextBatch();
    }
  });
  observer.observe(sentinel);

  let searchTimer = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      const q = searchInput.value.trim().toLowerCase();
      if (!q) {
        resetAndRender(allItems);
        return;
      }
      resetAndRender(allItems.filter((item) => item.title && item.title.toLowerCase().includes(q)));
    }, 120);
  });

  fetch("data/playlist.json")
    .then((res) => res.json())
    .then((items) => {
      allItems = items;
      totalCountEl.textContent = allItems.length;
      resetAndRender(allItems);
    })
    .catch((err) => {
      emptyMessage.hidden = false;
      emptyMessage.textContent = "データの読み込みに失敗しました。";
      console.error(err);
    });
})();
