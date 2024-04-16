function confirmarEliminar(producto_id) {
    if (confirm('¿Estás seguro que deseas eliminar este producto?')) {
        var form = document.getElementById('eliminar-form');
        form.action = '/eliminar_producto/' + producto_id;
        form.style.display = 'block';
        form.submit();
    }
}
