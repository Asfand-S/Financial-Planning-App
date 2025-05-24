const saveButton = document.getElementById('save-button');
const saveSuccessMessage = document.getElementById('save-success-message');
let formChanged = false;
let groupCount = 0;
let individualCount = 0;
let savingsCount = 0;
let propertyCount = 0;
let vehicleCount = 0;
let boatCount = 0;

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

// Loads form HTML into the container and binds event listeners afterward
async function loadFormIntoContainer(formFile, containerId) {
    const response = await fetch(formFile);
    const html = await response.text();
    const container = document.getElementById(containerId);
    container.innerHTML = html;

    // Re-bind add buttons if present in the loaded form
    bindDynamicFormEvents(container);
}

// Binds add-income, add-expense, and add-loan buttons from a loaded form
function bindDynamicFormEvents(container) {
    const groupBtn = container.querySelector('#add-group');
    const individualBtn = container.querySelector('#add-individual');
    const savingsBtn = container.querySelector('#add-savings');
    const propertyBtn = container.querySelector('#add-property');
    const vehicleBtn = container.querySelector('#add-vehicle');
    const boatBtn = container.querySelector('#add-boat');

    if (groupBtn) groupBtn.addEventListener('click', addGroup);
    if (individualBtn) individualBtn.addEventListener('click', addIndividual);
    if (savingsBtn) savingsBtn.addEventListener('click', addSavings);
    if (propertyBtn) propertyBtn.addEventListener('click', addProperty);
    if (vehicleBtn) vehicleBtn.addEventListener('click', addVehicle);
    if (boatBtn) boatBtn.addEventListener('click', addBoat);
}

function addGroup() {
    const template = document.getElementById('group-template');
    const clone = template.content.cloneNode(true);

    // Update the label number
    const label = clone.getElementById("group_insurance_label");
    label.textContent = `Ασφάλεια Ομαδική ${groupCount + 1}:`;

    // Update radio button names uniquely
    const radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.name = `group_insurance_${groupCount}`;  // unique name
    });

    document.getElementById('group-container').appendChild(clone);
    groupCount++;
}

function addIndividual() {
    const template = document.getElementById('individual-template');
    const clone = template.content.cloneNode(true);

    // Update the label number
    const label = clone.getElementById("individual_insurance_label");
    label.textContent = `Ασφάλεια Ατομική ${individualCount + 1}:`;

    // Update radio button names uniquely
    const radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.name = `individual_insurance_${individualCount}`;  // unique name
    });

    document.getElementById('individual-container').appendChild(clone);
    individualCount++;
}

function addSavings() {
    const template = document.getElementById('savings-template');
    const clone = template.content.cloneNode(true);

    // Update the label number
    const label = clone.getElementById("savings_insurance_label");
    label.textContent = `Ασφάλεια Αποταμιευτική ${savingsCount + 1}:`;

    // Update radio button names uniquely
    const radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.name = `savings_insurance_${savingsCount}`;  // unique name
    });

    document.getElementById('savings-container').appendChild(clone);
    savingsCount++;
}

function addProperty() {
    const template = document.getElementById('property-template');
    const clone = template.content.cloneNode(true);

    // Update the label number
    const label = clone.getElementById("property_insurance_label");
    label.textContent = `Ασφάλεια Περιουσίας ${propertyCount + 1}:`;

    // Update radio button names uniquely
    const radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.name = `property_insurance_${propertyCount}`;  // unique name
    });

    document.getElementById('property-container').appendChild(clone);
    propertyCount++;
}

function addVehicle() {
    const template = document.getElementById('vehicle-template');
    const clone = template.content.cloneNode(true);
    // Update the label number
    const label = clone.getElementById("vehicle_insurance_label");
    label.textContent = `Ασφάλεια Οχήματος ${vehicleCount + 1}:`;

    // Update radio button names uniquely
    const radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.name = `vehicle_insurance_${vehicleCount}`;  // unique name
    });

    document.getElementById("vehicle-container").appendChild(clone);
    vehicleCount++;
}

function addBoat() {
    const template = document.getElementById('boat-template');
    const clone = template.content.cloneNode(true);

    // Update the label number
    const label = clone.getElementById("boat_insurance_label");
    label.textContent = `Ασφάλεια Σκαφών ${boatCount + 1}:`;

    // Update radio button names uniquely
    const radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
        radio.name = `boat_insurance_${boatCount}`;  // unique name
    });

    document.getElementById('boat-container').appendChild(clone);
    boatCount++;
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
    await loadFormIntoContainer('/static/forms/insurance-groups.html', 'group-form-container');
    await loadFormIntoContainer('/static/forms/insurance-individuals.html', 'individual-form-container');
    await loadFormIntoContainer('/static/forms/insurance-savings.html', 'savings-form-container');
    await loadFormIntoContainer('/static/forms/insurance-properties.html', 'property-form-container');
    await loadFormIntoContainer('/static/forms/insurance-vehicles.html', 'vehicle-form-container');
    await loadFormIntoContainer('/static/forms/insurance-boats.html', 'boat-form-container');

    // Setup tab button listeners
    document.getElementById('group-button')?.addEventListener('click', () => showFormAndNotes('group'));
    document.getElementById('individual-button')?.addEventListener('click', () => showFormAndNotes('individual'));
    document.getElementById('savings-button')?.addEventListener('click', () => showFormAndNotes('savings'));
    document.getElementById('property-button')?.addEventListener('click', () => showFormAndNotes('property'));
    document.getElementById('vehicle-button')?.addEventListener('click', () => showFormAndNotes('vehicle'));
    document.getElementById('boat-button')?.addEventListener('click', () => showFormAndNotes('boat'));

    // Show the income form by default
    addGroup();
    addIndividual();
    addSavings();
    addProperty();
    addVehicle();
    addBoat();
    showFormAndNotes('group');

    // Mark unsaved when user types or changes input
    document.getElementById('insurance-form').addEventListener('input', markFormChanged);
    document.getElementById('insurance-form').addEventListener('change', markFormChanged);
});

// Form submit handling
document.getElementById("insurance-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (hasEmptyFields("#insurance-form")) {
        showToast('Ορισμένα πεδία δεν έχουν συμπληρωθεί.');
        return;
    }

    const formData = new FormData(this);

    const insuranceRadios = document.querySelectorAll('#group-container input[type="radio"]:checked');
    insuranceRadios.forEach(radio => { formData.append("group_insurance[]", radio.value); });

    const individualRadios = document.querySelectorAll('#individual-container input[type="radio"]:checked');
    individualRadios.forEach(radio => { formData.append("individual_insurance[]", radio.value); });

    const savingsRadios = document.querySelectorAll('#savings-container input[type="radio"]:checked');
    savingsRadios.forEach(radio => { formData.append("savings_insurance[]", radio.value); });

    const propertyRadios = document.querySelectorAll('#property-container input[type="radio"]:checked');
    propertyRadios.forEach(radio => { formData.append("property_insurance[]", radio.value); });

    const vehicleRadios = document.querySelectorAll('#vehicle-container input[type="radio"]:checked');
    vehicleRadios.forEach(radio => { formData.append("vehicle_insurance[]", radio.value); });

    const boatRadios = document.querySelectorAll('#boat-container input[type="radio"]:checked');
    boatRadios.forEach(radio => { formData.append("boat_insurance[]", radio.value); });

    try {
        const response = await fetch("/save_insurances", {
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
