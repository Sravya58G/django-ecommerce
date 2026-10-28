document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".remove").forEach(button => {
    button.addEventListener("click", event => {
      if (!confirm("Remove this item?")) event.preventDefault();
    });
  });
});
