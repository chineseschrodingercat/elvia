"use strict";

const menuToggle = document.querySelector(".menu-toggle");
const navigation = document.querySelector("#main-navigation");
function closeMenu(returnFocus = false) {
  navigation.classList.remove("is-open");
  menuToggle.setAttribute("aria-expanded", "false");
  if (returnFocus) menuToggle.focus();
}
menuToggle.addEventListener("click", () => {
  const open = menuToggle.getAttribute("aria-expanded") !== "true";
  navigation.classList.toggle("is-open", open);
  menuToggle.setAttribute("aria-expanded", String(open));
});
navigation.querySelectorAll("a").forEach(link => link.addEventListener("click", () => closeMenu()));
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") closeMenu(true);
});
document.addEventListener("click", event => {
  if (!event.target.closest(".site-header")) closeMenu();
});
window.matchMedia("(min-width: 761px)").addEventListener("change", event => {
  if (event.matches) closeMenu();
});

// Open a linked question while leaving account and reading anchors unchanged.
function revealQuestion() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const question = document.getElementById(id);
  if (question?.matches(".faq details")) question.open = true;
}
window.addEventListener("hashchange", revealQuestion);
revealQuestion();
