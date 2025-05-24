const saveButton = document.getElementById('save-button');
const saveSuccessMessage = document.getElementById('save-success-message');
let formChanged = false;

function markSaved() {
    saveButton.disabled = true;
    saveButton.innerText = 'Αποθηκεύτηκε';
    saveSuccessMessage.style.display = 'block';
    formChanged = false;
}

function markFormChanged() {
    formChanged = true;
    if (saveButton.disabled) {
        saveButton.disabled = false;
        saveButton.innerText = 'Αποθήκευση';
        saveSuccessMessage.style.display = 'none';
    }
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = "fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-red-100 text-red-800 px-6 py-3 rounded-lg shadow-lg z-50 text-center border border-red-400";
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 3000); // toast auto disappears
}

function hasEmptyFields(form_name) {
    const form = document.querySelector(form_name);
    const fields = form.querySelectorAll('input, select');

    const radioGroupsChecked = new Set(); // to track processed radio groups
    for (let field of fields) {
        // Skip buttons and hidden/removed elements
        if (
            field.type === 'button' ||
            field.name === 'notes' // explicitly skip notes
        ) {
            continue;
        }
        console.log(field.type, field.name, field.value);

        // Handle radio groups
        if (field.type === 'radio') {
            if (!radioGroupsChecked.has(field.name)) {
                radioGroupsChecked.add(field.name);
                const radios = form.querySelectorAll(`input[type="radio"]`);
                const isChecked = Array.from(radios).some(r => r.checked);
                if (!isChecked) {
                    return true;
                }
            }
            continue; // Don't check .value for individual radio inputs
        }

        if (field.value.trim() === '') {
            return true;
        }
    }

    return false;
}

// Intercept all link clicks
document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function (e) {
        if (formChanged) {
            answer = confirm("Έχετε μη αποθηκευμένες αλλαγές, είστε βέβαιοι ότι θέλετε να συνεχίσετε;")
            if (answer) {
                a = 1;
            } else {
                e.preventDefault(); // stop immediate navigation
            }
        }
    });
});

// Loads form HTML into the specific container and binds event listeners afterward
async function loadFormIntoContainer(formFile, containerId) {
    const response = await fetch(formFile);
    const html = await response.text();
    const container = document.getElementById(containerId);
    container.innerHTML = html;

    // Re-bind dynamic buttons if present in the loaded form
    bindDynamicFormEvents(container);
}

// Binds dynamic add buttons from a loaded form
function bindDynamicFormEvents(container) {
    const personIncomeBtn = container.querySelector('#add-person-income');
    const spouseIncomeBtn = container.querySelector('#add-spouse-income');
    const personExpenseBtn = container.querySelector('#add-person-expense');
    const spouseExpenseBtn = container.querySelector('#add-spouse-expense');
    const loanBtn = container.querySelector('#add-loan');

    if (personIncomeBtn) personIncomeBtn.addEventListener('click', addPersonIncome);
    if (spouseIncomeBtn) spouseIncomeBtn.addEventListener('click', addSpouseIncome);
    if (personExpenseBtn) personExpenseBtn.addEventListener('click', addPersonExpense);
    if (spouseExpenseBtn) spouseExpenseBtn.addEventListener('click', addSpouseExpense);
    if (loanBtn) loanBtn.addEventListener('click', addLoan);
}

// Utility functions to clone templates
function addPersonIncome() {
    const template = document.getElementById('person-income-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('person-income-container').appendChild(clone);
}

function addSpouseIncome() {
    const template = document.getElementById('spouse-income-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('spouse-income-container').appendChild(clone);
}

function addPersonExpense() {
    const template = document.getElementById('person-expense-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('person-expense-container').appendChild(clone);
}

function addSpouseExpense() {
    const template = document.getElementById('spouse-expense-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('spouse-expense-container').appendChild(clone);
}

function addLoan() {
    const template = document.getElementById('loan-template');
    const clone = template.content.cloneNode(true);
    document.getElementById('loan-container').appendChild(clone);
}

// Handle tab switching
function showFormAndNotes(formName) {
    // Hide all form containers
    document.querySelectorAll('.form-section').forEach(container => container.classList.remove('active'));

    // Hide all notes
    document.querySelectorAll('.notes-section').forEach(textarea => textarea.classList.remove('active'));

    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(button => button.classList.remove('active'));

    // Show selected form container
    const formContainer = document.getElementById(`${formName}-form-container`);
    if (formContainer) {
        formContainer.classList.add('active');
    }

    // Show corresponding notes
    const notesField = document.getElementById(`${formName}-notes`);
    if (notesField) {
        notesField.classList.add('active');
    }

    // Highlight the correct tab button
    const button = document.getElementById(`${formName}-button`);
    if (button) {
        button.classList.add('active');
    }
}

// Attach the event listener after the DOM has loaded
document.addEventListener('DOMContentLoaded', async () => {
    // Preload all forms
    await loadFormIntoContainer('/static/forms/financial-incomes.html', 'income-form-container');
    await loadFormIntoContainer('/static/forms/financial-expenses.html', 'expense-form-container');
    await loadFormIntoContainer('/static/forms/financial-loans.html', 'loan-form-container');

    // Setup tab button listeners
    document.getElementById('income-button')?.addEventListener('click', () => showFormAndNotes('income'));
    document.getElementById('expense-button')?.addEventListener('click', () => showFormAndNotes('expense'));
    document.getElementById('loan-button')?.addEventListener('click', () => showFormAndNotes('loan'));

    // Show the income form by default
    showFormAndNotes('income');

    // Mark unsaved when user types or changes input
    document.getElementById('financial-form').addEventListener('input', markFormChanged);
    document.getElementById('financial-form').addEventListener('change', markFormChanged);
});

// Form submit handling
document.getElementById("financial-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (hasEmptyFields("#financial-form")) {
        showToast('Ορισμένα πεδία δεν έχουν συμπληρωθεί.');
        return;
    }

    const formData = new FormData(this);

    try {
        const response = await fetch("/save_financials", {
            method: "POST",
            body: formData,
        });

        const result = await response.json();
        if (result.success) {
            markSaved();
        } else {
            alert("Αποτυχία αποθήκευσης. Προσπαθήστε ξανά.");
        }
    } catch (error) {
        alert("Παρουσιάστηκε σφάλμα κατά την υποβολή.");
    }
});
