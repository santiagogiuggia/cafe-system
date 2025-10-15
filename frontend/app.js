// app.js
document.addEventListener('DOMContentLoaded', () => {
    // --- URL de nuestra API Backend ---
    const API_URL = 'http://127.0.0.1:8000';

    // --- ESTADO DE LA APLICACIÓN ---
    let menuData = []; // Ahora empieza vacío y se llenará desde la API
    let currentOrder = [];
    let activeCategory = 'Todos';
    let orderCounter = 125;
    let currentTotal = 0;
    let selectedPaymentMethod = null;

    // --- SELECTORES DEL DOM ---
    // (Esta sección no cambia)
    const categoryNav = document.getElementById('category-nav');
    const productGrid = document.getElementById('product-grid');
    const orderList = document.getElementById('order-list');
    const subtotalPriceEl = document.getElementById('subtotal-price');
    const totalPriceEl = document.getElementById('total-price');
    const checkoutBtn = document.getElementById('checkout-btn');
    const clearOrderBtn = document.getElementById('clear-order-btn');
    const orderNumberEl = document.getElementById('order-number');
    const productModal = document.getElementById('product-modal');
    const closeProductModalBtn = document.getElementById('close-modal-btn');
    const checkoutModal = document.getElementById('checkout-modal');
    const closeCheckoutModalBtn = document.getElementById('close-checkout-modal-btn');
    const modalCheckoutTotal = document.getElementById('modal-checkout-total');
    const paymentMethodsContainer = document.querySelector('.payment-methods');
    const cashPaymentDetails = document.getElementById('cash-payment-details');
    const amountReceivedInput = document.getElementById('amount-received');
    const changeDueEl = document.getElementById('change-due');
    const confirmPaymentBtn = document.getElementById('confirm-payment-btn');

    // --- FUNCIÓN PARA CARGAR DATOS DESDE LA API ---
    async function fetchMenuData() {
        try {
            const response = await fetch(`${API_URL}/products/`);
            if (!response.ok) {
                throw new Error('No se pudo conectar a la API.');
            }
            const data = await response.json();
            // ¡Guardamos los productos de la API en nuestro estado!
            menuData = data;
        } catch (error) {
            console.error("Error al cargar el menú:", error);
            // Mostrar un mensaje de error en la interfaz
            productGrid.innerHTML = `<p class="error-message">Error al cargar el menú. Asegúrate de que el servidor esté funcionando.</p>`;
        }
    }


    // --- FUNCIONES DE RENDERIZADO ---
    // (Estas funciones no cambian, pero ahora usarán `menuData` cargado de la API)
    function renderCategories() {
        if (menuData.length === 0) return;
        const categories = ['Todos', ...new Set(menuData.map(p => p.category))];
        categoryNav.innerHTML = categories.map(cat =>
            `<button class="${cat === activeCategory ? 'active' : ''}" data-category="${cat}">${cat}</button>`
        ).join('');
    }

    function renderProducts() {
        if (menuData.length === 0) return;
        const filteredProducts = activeCategory === 'Todos' ? menuData : menuData.filter(p => p.category === activeCategory);
        
        // ¡ACTUALIZADO! Para manejar productos con y sin opciones.
        productGrid.innerHTML = filteredProducts.map(product => `
            <div class="product-card" data-id="${product.id}">
                <h3>${product.name}</h3>
                <p>$${product.price.toLocaleString('es-AR')}</p>
            </div>`).join('');
    }

    function renderOrder() {
        // (Sin cambios)
        if (currentOrder.length === 0) {
            orderList.innerHTML = '<li class="empty-state">Tu comanda está vacía.</li>';
        } else {
            orderList.innerHTML = currentOrder.map((item, index) => `
                <li class="order-item">
                    <div class="item-main">
                        <span>${item.quantity}x ${item.name}</span>
                        <span>$${item.totalPrice.toLocaleString('es-AR')}</span>
                    </div>
                    ${item.details ? `<div class="item-details">${item.details}</div>` : ''}
                </li>`).join('');
        }
        updateSummary();
    }

    function updateSummary() {
        // (Sin cambios)
        currentTotal = currentOrder.reduce((sum, item) => sum + item.totalPrice, 0);
        subtotalPriceEl.textContent = `$ ${currentTotal.toLocaleString('es-AR')}`;
        totalPriceEl.textContent = `$ ${currentTotal.toLocaleString('es-AR')}`;
        checkoutBtn.disabled = currentOrder.length === 0;
    }


    // --- LÓGICA DE MODALES ---
    // (openProductModal y openCheckoutModal no tienen cambios significativos, se quedan igual)
    function openProductModal(product) {
        // Esta función ahora es más simple porque asumimos que los productos con opciones
        // se manejarán de otra forma o que todos tienen un precio base.
        // Por ahora, solo agrega el producto base.
        const modalProductName = document.getElementById('modal-product-name');
        modalProductName.textContent = product.name;
        // Lógica para agregar al pedido...
    }
    
    // (El resto de las funciones de modales y lógica de negocio no cambian)
    function resetCheckoutModal() {
        selectedPaymentMethod = null;
        document.querySelectorAll('.payment-method-btn').forEach(btn => btn.classList.remove('active'));
        cashPaymentDetails.style.display = 'none';
        amountReceivedInput.value = '';
        changeDueEl.textContent = '$ 0';
        confirmPaymentBtn.disabled = true;
    }

    function finalizeSale() {
        console.log('--- VENTA FINALIZADA ---');
        console.log(`Nº de Comanda: ${orderCounter}`);
        console.log(`Método de Pago: ${selectedPaymentMethod}`);
        console.log('Items:', currentOrder);
        console.log(`TOTAL: $${currentTotal}`);
        alert(`Venta #${orderCounter} finalizada con éxito por $${currentTotal.toLocaleString('es-AR')}.`);
        currentOrder = [];
        orderCounter++;
        orderNumberEl.textContent = `#${orderCounter}`;
        renderOrder();
        checkoutModal.style.display = 'none';
    }
   // app.js

// ... (todo el código anterior de app.js hasta los event listeners) ...

// --- Selectores del DOM (añadir los nuevos) ---
const mpQrModal = document.getElementById('mp-qr-modal');
const qrCodeContainer = document.getElementById('qr-code-container');
const qrTotalAmount = document.getElementById('qr-total-amount');
const closeQrModalBtn = document.getElementById('close-qr-modal-btn');


// --- NUEVA FUNCIÓN PARA MERCADO PAGO ---
async function handleMercadoPagoPayment() {
    checkoutModal.style.display = 'none'; // Ocultar modal de selección de pago
    mpQrModal.style.display = 'flex'; // Mostrar modal del QR
    qrTotalAmount.textContent = `$ ${currentTotal.toLocaleString('es-AR')}`;
    qrCodeContainer.innerHTML = 'Generando QR...';

    try {
        const response = await fetch(`${API_URL}/create_payment_order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                total_amount: currentTotal,
                order_id: orderCounter
            })
        });

        if (!response.ok) {
            throw new Error('No se pudo generar el código QR.');
        }

        const data = await response.json();
        
        // Limpiar contenedor y generar nuevo QR
        qrCodeContainer.innerHTML = '';
        new QRCode(qrCodeContainer, {
            text: data.qr_data,
            width: 256,
            height: 256,
        });

        // Aquí iría la lógica para escuchar la notificación de pago completado (Webhook)
        // Por ahora, simularemos que se cierra manualmente
        
    } catch (error) {
        console.error("Error con Mercado Pago:", error);
        qrCodeContainer.innerHTML = `<p class="error-message">Error al generar QR. Intente de nuevo.</p>`;
    }
}


// --- MODIFICAR EL EVENT LISTENER DEL CHECKOUT ---
paymentMethodsContainer.addEventListener('click', e => {
    if (e.target.classList.contains('payment-method-btn')) {
        document.querySelectorAll('.payment-method-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        selectedPaymentMethod = e.target.dataset.method;
        
        cashPaymentDetails.style.display = selectedPaymentMethod === 'Efectivo' ? 'block' : 'none';
        
        // Si no es MP, el botón de confirmar está habilitado. Si es MP, se maneja aparte.
        confirmPaymentBtn.style.display = selectedPaymentMethod === 'Mercado Pago' ? 'none' : 'block';
        if (selectedPaymentMethod === 'Mercado Pago') {
            handleMercadoPagoPayment();
        } else {
             confirmPaymentBtn.disabled = false;
        }
    }
});

closeQrModalBtn.addEventListener('click', () => {
    mpQrModal.style.display = 'none';
});

// ... (resto del código de app.js) 

    // --- EVENT LISTENERS ---
    // (La mayoría de los listeners no cambian)
    categoryNav.addEventListener('click', e => {
        if (e.target.tagName === 'BUTTON') {
            activeCategory = e.target.dataset.category;
            renderCategories();
            renderProducts();
        }
    });

    productGrid.addEventListener('click', e => {
        const card = e.target.closest('.product-card');
        if (!card) return;
        const productId = parseInt(card.dataset.id, 10);
        const product = menuData.find(p => p.id === productId);

        // Lógica simplificada: agregar directamente el producto a la orden
        // En el futuro, aquí se podría abrir un modal si el producto tiene opciones
        currentOrder.push({
            id: product.id, name: product.name, quantity: 1,
            unitPrice: product.price, totalPrice: product.price, details: ''
        });
        renderOrder();
    });
    
    // (El resto de los listeners se mantienen igual)
    clearOrderBtn.addEventListener('click', () => {
        if (confirm('¿Estás seguro de que quieres vaciar la comanda?')) {
            currentOrder = [];
            renderOrder();
        }
    });
    closeProductModalBtn.addEventListener('click', () => productModal.style.display = 'none');
    productModal.addEventListener('click', e => { if (e.target === productModal) productModal.style.display = 'none'; });
    closeCheckoutModalBtn.addEventListener('click', () => checkoutModal.style.display = 'none');
    checkoutModal.addEventListener('click', e => { if (e.target === checkoutModal) checkoutModal.style.display = 'none'; });
    document.getElementById('increase-qty').addEventListener('click', () => {
        let qty = document.getElementById('modal-quantity');
        qty.textContent = parseInt(qty.textContent) + 1;
    });
    document.getElementById('decrease-qty').addEventListener('click', () => {
        let qty = document.getElementById('modal-quantity');
        if (parseInt(qty.textContent) > 1) {
            qty.textContent = parseInt(qty.textContent) - 1;
        }
    });
    checkoutBtn.addEventListener('click', () => {
        modalCheckoutTotal.textContent = `$ ${currentTotal.toLocaleString('es-AR')}`;
        resetCheckoutModal();
        checkoutModal.style.display = 'flex';
    });
    paymentMethodsContainer.addEventListener('click', e => {
        if (e.target.classList.contains('payment-method-btn')) {
            document.querySelectorAll('.payment-method-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            selectedPaymentMethod = e.target.dataset.method;
            cashPaymentDetails.style.display = selectedPaymentMethod === 'Efectivo' ? 'block' : 'none';
            confirmPaymentBtn.disabled = false;
        }
    });
    amountReceivedInput.addEventListener('input', e => {
        const received = parseFloat(e.target.value) || 0;
        const change = received - currentTotal;
        changeDueEl.textContent = `$ ${Math.max(0, change).toLocaleString('es-AR')}`;
    });
    confirmPaymentBtn.addEventListener('click', finalizeSale);

    // --- INICIALIZACIÓN ---
    async function init() {
        orderNumberEl.textContent = `#${orderCounter}`;
        await fetchMenuData(); // Espera a que los datos se carguen
        renderCategories();    // Luego renderiza todo
        renderProducts();
        renderOrder();
    }

    init();
});
