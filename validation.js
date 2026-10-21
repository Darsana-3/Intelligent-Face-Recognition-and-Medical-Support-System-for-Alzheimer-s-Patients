// ===== Alzheimer Care System - Form Validation =====
// Generic, reusable client-side validation that:
//   1. Blocks submission (without clearing any typed values) until fixed.
//   2. Shows inline Bootstrap-style error messages under each field.
//   3. Validates confirm-password live, as soon as the user types it.
//   4. Restricts phone numbers to exactly 10 digits.
//   5. Enforces a strong password policy.
//   6. Restricts registration emails to well-known providers (gmail, google,
//      yahoo, outlook, hotmail, etc.) when the form opts in via
//      data-restrict-email-domain="1".
(function () {
    'use strict';

    var ALLOWED_EMAIL_DOMAINS = [
        'gmail.com', 'googlemail.com', 'google.com',
        'yahoo.com', 'yahoo.co.in', 'ymail.com',
        'outlook.com', 'hotmail.com', 'live.com', 'msn.com'
    ];

    var PHONE_REGEX = /^[0-9]{10}$/;
    // At least 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special character.
    var PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

    function getOrCreateFeedback(field) {
        var next = field.nextElementSibling;
        if (next && next.classList && next.classList.contains('js-field-feedback')) {
            return next;
        }
        var div = document.createElement('div');
        div.className = 'invalid-feedback js-field-feedback';
        div.style.display = 'none';
        field.insertAdjacentElement('afterend', div);
        return div;
    }

    function setError(field, message) {
        var feedback = getOrCreateFeedback(field);
        if (message) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            feedback.textContent = message;
            feedback.style.display = 'block';
        } else {
            field.classList.remove('is-invalid');
            if (field.value) field.classList.add('is-valid');
            feedback.textContent = '';
            feedback.style.display = 'none';
        }
        return !message;
    }

    function validatePhoneField(field) {
        var value = field.value.trim();
        if (!value && !field.required) return true;
        if (!PHONE_REGEX.test(value)) {
            return setError(field, 'Phone number must be exactly 10 digits.');
        }
        return setError(field, '');
    }

    function validateEmailDomainField(field) {
        var value = field.value.trim().toLowerCase();
        if (!value) return true;
        var atIndex = value.lastIndexOf('@');
        if (atIndex === -1) return true; // let type="email" / required handle basic format
        var domain = value.slice(atIndex + 1);
        if (ALLOWED_EMAIL_DOMAINS.indexOf(domain) === -1) {
            return setError(field, 'Please use a Google (Gmail), Yahoo, Outlook/Hotmail or similar email address.');
        }
        return setError(field, '');
    }

    // ----- Live username availability check (checks while typing, not on submit) -----
    var usernameCheckTimer = null;
    var usernameCheckToken = 0;

    function checkUsernameField(field, role) {
        var value = field.value.trim();
        if (!value) {
            return setError(field, '');
        }
        clearTimeout(usernameCheckTimer);
        var thisToken = ++usernameCheckToken;
        // small delay so we don't fire a request on every keystroke
        usernameCheckTimer = setTimeout(function () {
            fetch('/check-username/?username=' + encodeURIComponent(value) + '&role=' + encodeURIComponent(role || 'patient'))
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    if (thisToken !== usernameCheckToken) return; // a newer request has already fired
                    if (data.available === false) {
                        setError(field, 'This username is already taken. Please choose another.');
                    } else if (data.available === true) {
                        setError(field, '');
                    }
                })
                .catch(function () { /* fail silently - server-side check on submit still applies */ });
        }, 400);
    }

    function validatePasswordField(field) {
        var value = field.value;
        if (!value && !field.required) return true;
        if (!PASSWORD_REGEX.test(value)) {
            return setError(field, 'Password must be 8+ characters and include uppercase, lowercase, a number, and a special character.');
        }
        return setError(field, '');
    }

    function validateConfirmField(confirmField, passwordField) {
        if (!confirmField.value) {
            // Nothing typed yet - don't nag until the user starts typing.
            return setError(confirmField, '');
        }
        if (confirmField.value !== passwordField.value) {
            return setError(confirmField, 'Passwords do not match.');
        }
        return setError(confirmField, '');
    }

    function enhanceForm(form) {
        var phoneField = form.querySelector('input[name="phone"]');
        var emailField = form.querySelector('input[name="email"]');
        var passwordField = form.querySelector('input[name="password"]');
        var confirmField = form.querySelector('input[name="confirm_password"]');
        var usernameField = form.querySelector('input[name="username"]');
        var restrictEmailDomain = form.getAttribute('data-restrict-email-domain') === '1';
        var checkUsername = form.getAttribute('data-check-username') === '1';
        var checkUsernameRole = form.getAttribute('data-check-username-role') || 'patient';

        if (usernameField && checkUsername) {
            usernameField.addEventListener('input', function () { checkUsernameField(this, checkUsernameRole); });
            usernameField.addEventListener('blur', function () { checkUsernameField(this, checkUsernameRole); });
        }

        if (phoneField) {
            phoneField.setAttribute('maxlength', '10');
            phoneField.addEventListener('input', function () {
                this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10);
                validatePhoneField(this);
            });
            phoneField.addEventListener('blur', function () { validatePhoneField(this); });
        }

        if (emailField && restrictEmailDomain) {
            emailField.addEventListener('input', function () { validateEmailDomainField(this); });
            emailField.addEventListener('blur', function () { validateEmailDomainField(this); });
        }

        if (passwordField) {
            passwordField.addEventListener('input', function () {
                validatePasswordField(this);
                if (confirmField) validateConfirmField(confirmField, passwordField);
            });
            passwordField.addEventListener('blur', function () { validatePasswordField(this); });
        }

        if (confirmField && passwordField) {
            // Live check - fires as soon as the user types into confirm password,
            // not only on form submit.
            confirmField.addEventListener('input', function () {
                validateConfirmField(this, passwordField);
            });
            confirmField.addEventListener('blur', function () {
                validateConfirmField(this, passwordField);
            });
        }

        form.addEventListener('submit', function (e) {
            var valid = true;

            if (phoneField && !validatePhoneField(phoneField)) valid = false;
            if (emailField && restrictEmailDomain && !validateEmailDomainField(emailField)) valid = false;
            if (passwordField && passwordField.value && !validatePasswordField(passwordField)) valid = false;
            if (confirmField && passwordField && !validateConfirmField(confirmField, passwordField)) valid = false;
            if (usernameField && checkUsername && usernameField.classList.contains('is-invalid')) valid = false;

            if (!valid) {
                e.preventDefault();
                e.stopPropagation();
                // Scroll to first invalid field so the user sees exactly what to fix.
                var firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
                if (window.showToast) {
                    window.showToast('Please fix the highlighted fields before submitting.', 'danger');
                }
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var forms = document.querySelectorAll('form.js-validate');
        forms.forEach(enhanceForm);
    });
})();
