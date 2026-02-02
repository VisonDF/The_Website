function updateFileName(input) {
  const label = document.getElementById("dataset-file-name");
  if (input.files && input.files.length > 0) {
    label.textContent = input.files[0].name;
  } else {
    label.textContent = "No file selected";
  }
}

function updatePreview() {
  if (!window.cmView) return;

  const preview = document.getElementById("description-preview");
  if (!preview) return;

  preview.innerHTML = window.cmView.state.doc.toString();
}

function togglePreview() {
  const preview = document.getElementById("description-preview");
  if (!preview) return;

  const isVisible = !preview.hasAttribute("hidden");

  if (isVisible) {
    preview.setAttribute("hidden", "");
  } else {
    updatePreview();
    preview.removeAttribute("hidden");
  }
}


