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

    // ─── Order Form: Dynamic Item Repeater & Date Validation ─────────
    const itemsContainer = document.getElementById('order-items-container');
    const addItemBtn = document.getElementById('add-item-btn');

    function updateRemoveButtons() {
        if (!itemsContainer) return;
        const rows = itemsContainer.querySelectorAll('.order-item-row');
        rows.forEach(row => {
            const removeBtn = row.querySelector('.remove-item-btn');
            if (removeBtn) {
                removeBtn.style.display = rows.length > 1 ? 'inline-flex' : 'none';
            }
        });
    }

    function reindexRows() {
        if (!itemsContainer) return;
        const rows = itemsContainer.querySelectorAll('.order-item-row');
        rows.forEach((row, index) => {
            row.querySelectorAll('select, input, label').forEach(el => {
                ['name', 'id', 'for'].forEach(attr => {
                    if (el.hasAttribute(attr)) {
                        const val = el.getAttribute(attr);
                        el.setAttribute(attr, val.replace(/items-\d+-/, `items-${index}-`));
                    }
                });
            });
        });
        updateRemoveButtons();
    }

    if (itemsContainer) {
        itemsContainer.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-item-btn');
            if (removeBtn) {
                const row = removeBtn.closest('.order-item-row');
                const rows = itemsContainer.querySelectorAll('.order-item-row');
                if (rows.length > 1 && row) {
                    row.remove();
                    reindexRows();
                }
            }
        });

        if (addItemBtn) {
            addItemBtn.addEventListener('click', () => {
                const rows = itemsContainer.querySelectorAll('.order-item-row');
                if (rows.length === 0) return;

                const firstRow = rows[0];
                const newRow = firstRow.cloneNode(true);
                const newIndex = rows.length;

                newRow.querySelectorAll('select, input').forEach(input => {
                    ['name', 'id'].forEach(attr => {
                        if (input.hasAttribute(attr)) {
                            const val = input.getAttribute(attr);
                            input.setAttribute(attr, val.replace(/items-\d+-/, `items-${newIndex}-`));
                        }
                    });

                    if (input.tagName === 'SELECT') {
                        input.selectedIndex = 0;
                    } else if (input.type === 'number') {
                        input.value = 1;
                    }
                });

                newRow.querySelectorAll('label').forEach(label => {
                    if (label.hasAttribute('for')) {
                        const val = label.getAttribute('for');
                        label.setAttribute('for', val.replace(/items-\d+-/, `items-${newIndex}-`));
                    }
                });

                itemsContainer.appendChild(newRow);
                updateRemoveButtons();
            });
        }

        updateRemoveButtons();
    }

    // Rental Date Validation & Availability Check
    const startDateInput = document.getElementById('rental_start');
    const endDateInput = document.getElementById('rental_end');

    if (startDateInput && endDateInput) {
        function validateDates() {
            if (startDateInput.value && endDateInput.value) {
                if (endDateInput.value < startDateInput.value) {
                    endDateInput.setCustomValidity('End date cannot be earlier than start date.');
                } else {
                    endDateInput.setCustomValidity('');
                }
            }
        }

        startDateInput.addEventListener('change', validateDates);
        endDateInput.addEventListener('change', validateDates);
    }

    // ─── Real-Time Product Availability Check ────────────────────────
    const orderForm = document.getElementById('order-form');
    if (orderForm && startDateInput && endDateInput && itemsContainer) {
        const orderId = orderForm.getAttribute('data-order-id');

        async function checkRowAvailability(row) {
            const productSelect = row.querySelector('.product-select') || row.querySelector('select[id*="product_id"]');
            const infoEl = row.querySelector('.availability-info');
            if (!productSelect || !infoEl) return;

            const productId = productSelect.value;
            const startVal = startDateInput.value;
            const endVal = endDateInput.value;

            if (!productId || !startVal || !endVal || endVal < startVal) {
                infoEl.classList.add('hidden');
                infoEl.textContent = '';
                return;
            }

            try {
                let url = `/api/availability?product_id=${productId}&start=${startVal}&end=${endVal}`;
                if (orderId) {
                    url += `&exclude_order_id=${orderId}`;
                }

                const response = await fetch(url);
                if (!response.ok) {
                    infoEl.classList.add('hidden');
                    return;
                }

                const data = await response.json();
                infoEl.classList.remove('hidden', 'text-emerald-600', 'text-rose-600', 'text-amber-600');

                if (data.available > 0) {
                    infoEl.classList.add('text-emerald-600');
                    infoEl.textContent = `✓ ${data.available} of ${data.total_stock} available`;
                } else {
                    infoEl.classList.add('text-rose-600');
                    infoEl.textContent = `✕ 0 of ${data.total_stock} available for dates (Fully Booked)`;
                }
            } catch (err) {
                console.error('Availability check failed:', err);
            }
        }

        function updateAllRowsAvailability() {
            const rows = itemsContainer.querySelectorAll('.order-item-row');
            rows.forEach(row => checkRowAvailability(row));
        }

        startDateInput.addEventListener('change', updateAllRowsAvailability);
        endDateInput.addEventListener('change', updateAllRowsAvailability);

        itemsContainer.addEventListener('change', (e) => {
            if (e.target.matches('.product-select') || e.target.matches('select[id*="product_id"]')) {
                const row = e.target.closest('.order-item-row');
                if (row) checkRowAvailability(row);
            }
        });

        // Trigger on load for pre-filled forms (e.g. edit mode)
        updateAllRowsAvailability();
    }
});


