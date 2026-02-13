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


/*-----------------------------------------------*/ 
(function () {
  const BOX_ID = "post-box";
  const DURATION_MS = 220; // 要和 CSS 的 height transition 时长一致

  function isTargetBox(target) {
    return target && target.id === BOX_ID;
  }

  // 在 swap 前：锁定旧高度（px）
  document.addEventListener("htmx:beforeSwap", (evt) => {
    const target = evt.detail.target;
    if (!isTargetBox(target)) return;

    const oldH = target.getBoundingClientRect().height;
    target.dataset.oldHeight = String(oldH);

    // 锁定旧高度，确保 swap 后我们有“起点高度”可动画
    target.style.height = oldH + "px";
    target.classList.add("is-animating");
  });

  // swap 后：测新高度（auto），回到旧高度，再动画到新高度
  document.addEventListener("htmx:afterSwap", (evt) => {
    const target = evt.detail.target;
    if (!isTargetBox(target)) return;

    const oldH = parseFloat(target.dataset.oldHeight || "0") || 0;

    // 1) 先暂时取消过渡，把高度设为 auto，读取新内容的自然高度
    const prevTransition = target.style.transition;
    target.style.transition = "none";
    target.style.height = "auto";

    const newH = target.getBoundingClientRect().height;

    // 2) 立刻回到旧高度（作为动画起点）
    target.style.height = oldH + "px";

    // 强制重排：让浏览器“认账”旧高度（关键）
    target.getBoundingClientRect();

    // 3) 恢复过渡，然后动画到新高度
    target.style.transition = prevTransition;
    requestAnimationFrame(() => {
      target.style.height = newH + "px";
    });

    // 4) 动画结束后释放高度回 auto
    let done = false;
    const cleanup = () => {
      if (done) return;
      done = true;
      target.style.transition = prevTransition;
      target.style.height = "auto";
      target.classList.remove("is-animating");
      target.removeEventListener("transitionend", onEnd);
    };

    const onEnd = (e) => {
      if (e.propertyName !== "height") return;
      cleanup();
    };

    target.addEventListener("transitionend", onEnd);

    // 兜底：极小高度差可能不触发 transitionend
    setTimeout(cleanup, DURATION_MS + 80);
  });

  // 请求失败兜底：别卡在固定高度
  document.addEventListener("htmx:responseError", (evt) => {
    const target = evt.detail.target;
    if (!isTargetBox(target)) return;
    target.style.height = "auto";
    target.classList.remove("is-animating");
  });
})();