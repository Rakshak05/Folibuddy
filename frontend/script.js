async function uploadResume() {
    const fileInput = document.getElementById("resume");
    const output = document.getElementById("output");

    if (!fileInput.files.length) {
        output.innerText = "Please select a PDF resume.";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    output.innerText = "Uploading and parsing resume...";

    try {
        const response = await fetch("http://127.0.0.1:8000/upload-resume", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        output.innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        output.innerText = "Error uploading resume.";
    }
}