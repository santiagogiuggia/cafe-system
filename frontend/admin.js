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
    
    // Event Listeners
    addProductBtn.addEventListener('click', () => openModal());
    cancelBtn.addEventListener('click', closeModal);
    form.addEventListener('submit', saveProduct);

    tableBody.addEventListener('click', async (event) => {
        const target = event.target;
        const id = target.dataset.id;

        if (target.classList.contains('edit-btn')) {
            // Cargar datos del producto y abrir modal
            const response = await fetch(`${API_URL}/products/${id}`);
            const product = await response.json();
            openModal(product);
        } else if (target.classList.contains('delete-btn')) {
            deleteProduct(id);
        }
    });

    // Carga inicial
    loadProducts();
});