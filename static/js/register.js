const registerForm = document.getElementById("form-register");
const fullNameInput = document.getElementById("full-name");
const emailInput = document.getElementById("email");
const phoneNumberInput = document.getElementById("phone-number");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirm-password");
const privacyPolicyInput = document.getElementById("privacy-policy");
const passwordError = document.getElementById("password-error");
const confirmPasswordError = document.getElementById("confirm-password-error");
const privacyPolicyError = document.getElementById("privacy-checkbox-error");
const showPasswordInput = document.getElementById("show-passwords");


function passwordsMatch(password, confirmPassword) {

    if (password === confirmPassword) {
        return true;
    }

    return false;
};


function passwordIsLongEnough(password) {
    if (password.length >= 12) {
        return true;
    }

    return false;
};


showPasswordInput.addEventListener("change", function () {

    if (showPasswordInput.checked) {
        passwordInput.type = "text";
        confirmPasswordInput.type = "text";
    } else {
        passwordInput.type = "password";
        confirmPasswordInput.type = "password";
    }
});


registerForm.addEventListener("submit", function (event) {
    
    event.preventDefault();

    passwordError.textContent = "";
    confirmPasswordError.textContent = "";
    privacyPolicyError.textContent = "";


    let formIsValid = true;


    const fullName = fullNameInput.value;
    const email = emailInput.value;
    const phoneNumber = phoneNumberInput.value;
    const password = passwordInput.value;
    const passwordLengthValid = passwordIsLongEnough(password);
    const confirmPassword = confirmPasswordInput.value;
    const privacyPolicy = privacyPolicyInput.checked;


    if (passwordLengthValid === false) {
        
        passwordError.textContent =
            "Password must contain at least 12 characters";
        formIsValid = false;
    };


    const passwordValid = passwordsMatch(
        password,
        confirmPassword
    );


    if (passwordValid === false) {
        confirmPasswordError.textContent = "Password does not match";
        formIsValid = false;
    };


    if (privacyPolicy === false) {
        
        privacyPolicyError.textContent = "You must acknowledge the privacy policy";
        formIsValid = false;
    };


    if (formIsValid === false) {
        return;
    };

    registerForm.submit();
    console.log("registration data passed frontend screening!")

});