document.addEventListener('DOMContentLoaded', function() {
    function setFocusOnTable() {
        document.getElementById('pagination').scrollIntoView();
    }


    setFocusOnTable();

    var paginationLinks = document.querySelectorAll('.pagination .page-link');
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function(event) {
        
            event.preventDefault();
            
         
            var url = this.getAttribute('href');
            
         
            fetch(url)
                .then(response => response.text())
                .then(html => {
                    
                    document.body.innerHTML = html;
            
                    setFocusOnTable();
                })
                .catch(error => console.error('Error:', error));
        });
    });
});
