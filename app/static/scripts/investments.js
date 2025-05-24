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

function addInvestment() {
    const template = document.getElementById('investmentTemplate');
    const clone = template.content.cloneNode(true);
    document.getElementById('investmentsContainer').appendChild(clone);
    markFormChanged()
}

// Attach the event listener after the DOM has loaded
document.addEventListener('DOMContentLoaded', () => {
    const addButton = document.getElementById('addInvestmentButton');
    if (addButton) {
        addButton.addEventListener('click', addInvestment);
    }

    // Mark unsaved when user types or changes input
    document.getElementById('investment-form').addEventListener('input', markFormChanged);
    document.getElementById('investment-form').addEventListener('change', markFormChanged);
});

// Form submit handling
document.getElementById("investment-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (hasEmptyFields("#investment-form")) {
        showToast('Ορισμένα πεδία δεν έχουν συμπληρωθεί.');
        return;
    }

    const formData = new FormData(this);

    try {
        const response = await fetch("/save_investment", {
            method: "POST",
            body: formData
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
