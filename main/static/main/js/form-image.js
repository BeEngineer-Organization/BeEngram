!function () {
    const imageInputs = document.querySelectorAll("input[type='file'][data-form-image]");
    for (let i = 0, len = imageInputs.length; i < len; ++i) {
        const e = imageInputs[i];
        e.addEventListener("change", function () {
            const file = this.files[0];
            const label = this.nextElementSibling;
            const img = label.querySelector("img");
            if (file && img) {
                img.src = URL.createObjectURL(file);
            }
        });
    }
}();
