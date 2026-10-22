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

// Open the author contribution explanation when reached from its local link.
function revealAuthorContext() {
  if (location.hash === "#author-contribution") document.querySelector("#author-contribution").open = true;
}
window.addEventListener("hashchange", revealAuthorContext);
revealAuthorContext();
