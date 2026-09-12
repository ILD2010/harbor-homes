// GET THE ORIGINAL DELETE ACCOUNT BUTTON FROM THE HTML

const deleteAccountButton = document.getElementById(
    "open-delete-confirmation"
);


// GET ANY DELETE-PASSWORD ERROR RETURNED BY FLASK

const deleteErrorData = document.getElementById(
    "delete-error-data"
);

const deleteAccountError = deleteErrorData.dataset.error;


// FUNCTION THAT CREATES THE DELETE ACCOUNT POPUP

function openDeleteModal(errorMessage = "") {

    // Create the modal overlay
    const modalOverlay = document.createElement("div");

    modalOverlay.classList.add("delete-modal");
    

    // Create everything inside the modal
    modalOverlay.innerHTML = `
        <div class="delete-modal-content">

            <h2>Delete your account?</h2>

            <p>
                This action cannot be undone. Enter your current
                password to confirm that you want to permanently
                delete your account.
            </p>


            <form method="POST">

                <input
                    type="hidden"
                    name="action"
                    value="delete_account"
                >


                <div class="form-field">

                    <label for="delete-password">
                        Current Password
                    </label>

                    <input
                        type="password"
                        id="delete-password"
                        name="delete_password"
                        autocomplete="current-password"
                    >


                    ${
                        errorMessage
                            ? `<p class="field-error">${errorMessage}</p>`
                            : ""
                    }

                </div>


                <div class="delete-modal-actions">

                    <button
                        type="button"
                        id="cancel-delete"
                        class="cancel-delete-button"
                    >
                        Cancel
                    </button>


                    <button
                        type="submit"
                        class="confirm-delete-button"
                    >
                        Permanently Delete Account
                    </button>

                </div>

            </form>

        </div>
    `;


    // ADD THE NEW MODAL TO THE PAGE

    document.body.appendChild(modalOverlay);


    // THE CANCEL BUTTON NOW EXISTS, SO WE CAN SELECT IT

    const cancelDeleteButton = document.getElementById(
        "cancel-delete"
    );


    // REMOVE THE ENTIRE MODAL WHEN CANCEL IS CLICKED

    cancelDeleteButton.addEventListener("click", () => {

        modalOverlay.remove();

    });

}


// OPEN THE MODAL WHEN THE ORIGINAL DELETE ACCOUNT BUTTON IS CLICKED

deleteAccountButton.addEventListener("click", () => {

    openDeleteModal();

});


// IF FLASK RETURNED A DELETE-PASSWORD ERROR,
// AUTOMATICALLY REOPEN THE MODAL AND DISPLAY IT

if (deleteAccountError) {

    openDeleteModal(deleteAccountError);

}