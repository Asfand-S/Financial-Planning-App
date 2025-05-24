let editId = null;

function openAddModal() {
    editId = null;
    document.getElementById('modalTitle').innerText = 'Προσθήκη Πελάτη';
    document.getElementById('name').value = '';
    document.getElementById('email').value = '';
    document.getElementById('phone').value = '';
    document.getElementById('modal').classList.remove('hidden');
}

function openEditModal(id, name, email, phone) {
    editId = id;
    document.getElementById('modalTitle').innerText = 'Επεξεργασία Πελάτη';
    document.getElementById('name').value = name;
    document.getElementById('email').value = email;
    document.getElementById('phone').value = phone;
    document.getElementById('modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}

async function saveClient() {
    const payload = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
    };

    const url = editId ? `/edit_client/${editId}` : '/add_client';
    await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    window.location.reload();
}

function confirmDelete(id) {
    if (confirm("Are you sure you want to delete this client?")) {
        fetch(`/delete_client/${id}`, { method: 'POST' })
            .then(() => window.location.reload());
    }
}

document.getElementById('searchBox').addEventListener('input', function () {
    const query = this.value.toLowerCase();
    document.querySelectorAll('#clientTable tr').forEach(row => {
        const name = row.dataset.name;
        if (name) {
            row.style.display = name.includes(query) ? '' : 'none';
        }
    });
});

function openClientForm(clientId) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/open-client';

    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'client_id';
    input.value = clientId;

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}