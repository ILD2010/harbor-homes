const loginForm = document.getElementById("form-login");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");

loginForm.addEventListener("submit", function (event) {

    event.preventDefault();

    const email = emailInput.value;
    const password = passwordInput.value;

    loginForm.submit();

});