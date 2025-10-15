// admin.js
document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:8000';
    
    // Selectores del DOM
    const tableBody = document.getElementById('product-table-body');
    const addProductBtn = document.getElementById('add-product-btn');
    const modal = document.getElementById('product-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('product-form');
    const cancelBtn = document.getElementById('cancel-btn');
    const productIdInput = document.getElementById('product-id');
    const productNameInput = document.getElementById('product-name');
    const productDescInput = document.getElementById('product-description');
    const productCatInput = document.getElementById('product-category');
    const productPriceInput = document.getElementById('product-price');

    // Cargar y mostrar productos en la tabla
    const loadProducts = async () => {
        try {
            const response = await fetch(`${API_URL}/products/`);
            const products = await response.json();
            
            tableBody.innerHTML = ''; // Limpiar tabla
            products.forEach(product => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${product.id}</td>
                    <td>${product.name}</td>
                    <td>${product.category}</td>
                    <td>$${product.price.toLocaleString('es-AR')}</td>
                    <td>
                        <button class="btn btn-secondary edit-btn" data-id="${product.id}">Editar</button>
                        <button class="btn btn-danger delete-btn" data-id="${product.id}">Eliminar</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            console.error('Error al cargar productos:', error);
        }
    };

    // Abrir el modal (para crear o editar)
    const openModal = (product = null) => {
        form.reset();
        if (product) {
            // Modo Edición
            modalTitle.textContent = 'Editar Producto';
            productIdInput.value = product.id;
            productNameInput.value = product.name;
            productDescInput.value = product.description;
            productCatInput.value = product.category;
            productPriceInput.value = product.price;
        } else {
            // Modo Creación
            modalTitle.textContent = 'Agregar Producto';
            productIdInput.value = '';
        }
        modal.style.display = 'flex';
    };

    // Cerrar el modal
    const closeModal = () => {
        modal.style.display = 'none';
    };

    // Guardar (Crear o Actualizar) un producto
    const saveProduct = async (event) => {
        event.preventDefault();

        const id = productIdInput.value;
        const productData = {
            name: productNameInput.value,
            description: productDescInput.value,
            category: productCatInput.value,
            price: parseFloat(productPriceInput.value)
        };
        
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_URL}/products/${id}` : `${API_URL}/products/`;
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData)
            });

            if (!response.ok) {
                throw new Error('Error al guardar el producto.');
            }
            
            closeModal();
            loadProducts(); // Recargar la tabla
        } catch (error) {
            console.error(error);
        }
    };

    // Eliminar un producto
    const deleteProduct = async (id) => {
        if (!confirm('¿Estás seguro de que quieres eliminar este producto?')) {
            return;
        }

        try {
            const response = await fetch(`${API_URL}/products/${id}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Error al eliminar el producto.');
            }

            loadProducts(); // Recargar la tabla
        } catch (error) {
            console.error(error);
        }
    };
    // admin.js
document.addEventListener('DOMContentLoaded', () => {
    // ... (código anterior) ...
    const mpTokenInput = document.getElementById('mp-token');
    const saveTokenBtn = document.getElementById('save-token-btn');

    // Cargar el token actual (si existe)
    const loadToken = async () => {
        try {
            const response = await fetch(`${API_URL}/settings/mp_access_token`);
            const data = await response.json();
            if (data.value) {
                mpTokenInput.value = data.value;
            }
        } catch (error) { console.error('No se pudo cargar el token.'); }
    };

    // Guardar el token
    const saveToken = async () => {
        const token = mpTokenInput.value;
        if (!token) {
            alert('El token no puede estar vacío.');
            return;
        }
        try {
            await fetch(`${API_URL}/settings/mp_access_token`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: token })
            });
            alert('¡Token de Mercado Pago guardado con éxito!');
        } catch (error) {
            alert('Error al guardar el token.');
        }
    };

    // Event Listeners
    saveTokenBtn.addEventListener('click', saveToken);
    
    // Carga inicial
    loadProducts();
    loadToken(); // Cargar token al iniciar
});
    
    // Event Listeners
    addProductBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    form.addEventListener('submit', saveProduct);

   // admin.js

// ... (código anterior)

    tableBody.addEventListener('click', async (event) => {
        const target = event.target;
        // Busca el botón más cercano que tenga un data-id
        const button = target.closest('button[data-id]');
        if (!button) return;

        const id = button.dataset.id;

        if (button.classList.contains('edit-btn')) {
            try {
                // 1. Llama a la API para obtener los datos más recientes del producto
                const response = await fetch(`${API_URL}/products/${id}`);
                if (!response.ok) throw new Error('Producto no encontrado.');
                const product = await response.json();
                
                // 2. Abre el modal con los datos cargados
                openModal(product);
            } catch (error) {
                console.error("Error al cargar producto para editar:", error);
                alert("No se pudo cargar la información del producto.");
            }
        } else if (button.classList.contains('delete-btn')) {
            deleteProduct(id);
        }
    });

// ... (resto del código)
    // Carga inicial
    loadProducts();
});