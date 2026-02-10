const ICON_DOWN = `
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`;
const ICON_UP = `
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M6 15l6-6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>`;

function setupOne(article) {
    const body = article.querySelector(".post-body");
    const btn = article.querySelector(".post-toggle");
    if (!body || !btn) return;

    const lines = parseInt(body.dataset.lines || "4", 10);

    // 设置折叠行数（CSS 变量）
    body.style.setProperty("--clamp-lines", lines);

    // 先确保折叠态用于测量
    body.classList.add("is-collapsed");

    // 判断是否真的溢出（被截断）
    const isOverflowing = body.scrollHeight > body.clientHeight + 1;

    if (!isOverflowing) {
        // 短文章：直接全文展示，不需要按钮
        body.classList.remove("is-collapsed");
        btn.hidden = true;
        return;
    }

    // 长文章：显示按钮，并绑定切换逻辑
    btn.hidden = false;
    btn.innerHTML = ICON_DOWN;

    btn.addEventListener("click", () => {
        const collapsed = body.classList.toggle("is-collapsed");
        btn.setAttribute("aria-expanded", String(!collapsed));
        btn.setAttribute("aria-label", collapsed ? "展开全文" : "收起");
        btn.innerHTML = collapsed ? ICON_DOWN : ICON_UP;
    });
}

function init() {
    document.querySelectorAll("article").forEach(setupOne);
}

// 等页面布局稳定后再测量（更准）
window.addEventListener("load", init);