// document.addEventListener('DOMContentLoaded', function() {
//     function setFocusOnTable() {
//         document.getElementById('pagination').scrollIntoView();
//     }


//     setFocusOnTable();

//     var paginationLinks = document.querySelectorAll('.pagination .page-link');
//     paginationLinks.forEach(function(link) {
//         link.addEventListener('click', function(event) {
        
//             event.preventDefault();
            
         
//             var url = this.getAttribute('href');
            
         
//             fetch(url)
//                 .then(response => response.text())
//                 .then(html => {
                    
//                     document.body.innerHTML = html;
            
//                     setFocusOnTable();
//                 })
//                 .catch(error => console.error('Error:', error));
//         });
//     });
// });

function addTableEventHandlers() {
    const table = document.getElementById("search-table");
    if (!table) return; 
    const headers = table.getElementsByTagName("th");
    
    
    for (let i = 0; i < headers.length; i++) {
        headers[i].removeEventListener("click", sortTable);
    }

    
    for (let i = 0; i < headers.length; i++) {
        headers[i].addEventListener("click", sortTable);
    }
}

function sortTable(event) {
    const header = event.target;
    const columnIndex = header.cellIndex;
    const table = document.getElementById("search-table");
    const rows = Array.from(table.querySelectorAll("tbody tr"));
    
   
    let sortOrder = 1;
    if (header.classList.contains("ascending")) {
        header.classList.remove("ascending");
        header.classList.add("descending");
        sortOrder = -1;
    } else {
        header.classList.remove("descending");
        header.classList.add("ascending");
    }
    
   
    rows.sort((a, b) => {
        const valueA = a.cells[columnIndex].textContent;
        const valueB = b.cells[columnIndex].textContent;
        if (isNaN(valueA) || isNaN(valueB)) {
            return valueA.localeCompare(valueB) * sortOrder;
        } else {
            return (parseFloat(valueA) - parseFloat(valueB)) * sortOrder;
        }
    });
    
    
    rows.forEach((row) => {
        table.tBodies[0].appendChild(row);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    addTableEventHandlers();
});


document.addEventListener("DOMContentLoaded", function() {
    const pagination = document.getElementById("pagination");
    if (pagination) {
        pagination.addEventListener("click", function() {
            addTableEventHandlers();
        });
    } else {
        console.error("Element with id 'pagination' not found.");
    }
});


