// Client-side JavaScript for Pseudo Booqable

document.addEventListener('DOMContentLoaded', () => {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('app-sidebar');
    const sidebarBackdrop = document.getElementById('sidebar-backdrop');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('-translate-x-full');
            if (sidebarBackdrop) {
                sidebarBackdrop.classList.toggle('hidden');
            }
        });
    }

    if (sidebarBackdrop && sidebar) {
        sidebarBackdrop.addEventListener('click', () => {
            sidebar.classList.add('-translate-x-full');
            sidebarBackdrop.classList.add('hidden');
        });
    }

    // Auto-dismiss alerts after 6 seconds
    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease-out';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // ─── Confirmation Modal ─────────────────────────────────────────
    const confirmModal = document.getElementById('confirm-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');
    let pendingForm = null;

    function showConfirmModal(title, message, form) {
        if (!confirmModal) return;
        pendingForm = form;
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        confirmModal.classList.remove('hidden');
        confirmModal.classList.add('flex');
    }

    function hideConfirmModal() {
        if (!confirmModal) return;
        confirmModal.classList.add('hidden');
        confirmModal.classList.remove('flex');
        pendingForm = null;
    }

    // Wire up all buttons/forms with data-confirm attribute
    document.querySelectorAll('[data-confirm]').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const title = trigger.getAttribute('data-confirm-title') || 'Are you sure?';
            const message = trigger.getAttribute('data-confirm') || 'This action cannot be undone.';

            // If the trigger is inside a form, use that form
            const form = trigger.closest('form');
            if (form) {
                showConfirmModal(title, message, form);
            }
        });
    });

    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener('click', () => {
            if (pendingForm) {
                pendingForm.submit();
            }
            hideConfirmModal();
        });
    }

    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', hideConfirmModal);
    }

    // Close modal on backdrop click
    if (confirmModal) {
        confirmModal.addEventListener('click', (e) => {
            if (e.target === confirmModal) hideConfirmModal();
        });
    }

    // ─── Image Upload Preview ───────────────────────────────────────
    const imageInput = document.getElementById('image-upload-input');
    const imagePreview = document.getElementById('image-upload-preview');
    const imagePreviewImg = document.getElementById('image-preview-img');

    if (imageInput && imagePreview && imagePreviewImg) {
        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    imagePreviewImg.src = ev.target.result;
                    imagePreview.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
    }
});

