document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "comic-form"
            );

        const button =
            document.getElementById(
                "submit-btn"
            );

        const loading =
            document.getElementById(
                "loading"
            );


        if (!form) {
            return;
        }


        form.addEventListener(
            "submit",
            () => {

                if (button) {
                    button.disabled = true;

                    button.textContent =
                        "Creating comic...";
                }


                if (loading) {
                    loading.classList.remove(
                        "hidden"
                    );
                }

            }
        );

    }
);