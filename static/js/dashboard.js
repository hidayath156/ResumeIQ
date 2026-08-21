async function newResume() {
    try {
        const d = await api('/api/resumes', {
            method: 'POST',
            body: '{}'
        });

        location = d.redirect;
    } catch (e) {
        alert(e.message);
    }
}

async function deleteResume(id) {
    if (!confirm('Delete this resume?')) {
        return;
    }

    try {
        await api(`/api/resumes/${id}/delete`, {
            method: 'POST',
            body: '{}'
        });

        location.reload();
    } catch (e) {
        alert(e.message);
    }
}