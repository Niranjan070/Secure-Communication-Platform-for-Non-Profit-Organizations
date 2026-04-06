document.addEventListener("DOMContentLoaded", () => {
    const fileInput = document.querySelector("[data-file-input]");
    const fileNameLabel = document.getElementById("selected-file-name");

    if (fileInput && fileNameLabel) {
        fileInput.addEventListener("change", () => {
            const selected = fileInput.files && fileInput.files[0];
            fileNameLabel.textContent = selected ? selected.name : "No file selected yet.";
        });
    }
});
