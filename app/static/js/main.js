// app/static/js/main.js

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Application chargée');
    
    // Activer tous les tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Activer tous les popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Confirmation avant suppression
    document.querySelectorAll('.delete-confirm').forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-fermeture des alertes après 5 secondes
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(alert => {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        });
    }, 5000);
    
    // Formatage des prix
    document.querySelectorAll('.price').forEach(el => {
        let price = parseFloat(el.textContent);
        if (!isNaN(price)) {
            el.textContent = price.toLocaleString('fr-FR') + ' FCFA';
        }
    });
});

// Fonction pour formater les nombres
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
}

// Fonction pour les notifications toast (si utilisées)
function showToast(message, type = 'info') {
    // À implémenter si besoin
    console.log(`Toast: ${message} (${type})`);
}