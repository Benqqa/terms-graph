function addRelatedTerm(relatedTerm = '', relationType = '') {
    const container = document.getElementById('relatedTermsContainer');
    const termGroup = document.createElement('div');
    termGroup.className = 'related-term-group mb-2';
    
    termGroup.innerHTML = `
        <div class="row">
            <div class="col-5">
                <input type="text" class="form-control form-control-sm related-term" 
                       placeholder="Связанный термин" value="${relatedTerm}">
            </div>
            <div class="col-5">
                <input type="text" class="form-control form-control-sm relation-type" 
                       placeholder="Тип связи" value="${relationType}">
            </div>
            <div class="col-2">
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeRelatedTerm(this)">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(termGroup);
}

function removeRelatedTerm(button) {
    button.closest('.related-term-group').remove();
}

function getRelatedTermsData() {
    const groups = document.querySelectorAll('.related-term-group');
    const relatedTerms = [];
    const relations = {};
    
    groups.forEach(group => {
        const term = group.querySelector('.related-term').value.trim();
        const type = group.querySelector('.relation-type').value.trim();
        
        if (term) {
            relatedTerms.push(term);
            if (type) {
                relations[term] = type;
            }
        }
    });
    
    return { relatedTerms, relations };
}

function editTerm(termId) {
    const term = Array.from(document.querySelectorAll('tr')).find(
        row => row.querySelector('td')?.textContent === termId
    );
    if (!term) return;

    // Очищаем контейнер связанных терминов
    document.getElementById('relatedTermsContainer').innerHTML = '';
    
    // Заполняем форму данными
    document.getElementById('editTermId').value = termId;
    document.getElementById('editName').value = term.children[1].textContent.trim();
    document.getElementById('editDefinition').value = term.children[2].textContent.trim();
    document.getElementById('editSource').value = term.children[4].textContent.trim();

    // Добавляем поля для связанных терминов
    const relatedTerms = Array.from(term.children[3].querySelectorAll('.badge'))
        .map(badge => badge.textContent.trim());
    
    // Получаем данные о связях из атрибутов
    const relations = {};
    term.children[3].querySelectorAll('.badge').forEach(badge => {
        const relatedTerm = badge.textContent.trim();
        const relationType = badge.getAttribute('data-relation-type') || '';
        relations[relatedTerm] = relationType;
    });
    
    relatedTerms.forEach(relatedTerm => {
        addRelatedTerm(relatedTerm, relations[relatedTerm] || '');
    });

    new bootstrap.Modal(document.getElementById('editModal')).show();
}

function saveEdit() {
    const termId = document.getElementById('editTermId').value;
    const { relatedTerms, relations } = getRelatedTermsData();
    
    const data = {
        name: document.getElementById('editName').value,
        definition: document.getElementById('editDefinition').value,
        related_terms: relatedTerms,
        relations: relations,
        source: document.getElementById('editSource').value
    };

    fetch(`/api/terms/${termId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при обновлении термина');
    });
}

function deleteTerm(termId) {
    if (confirm('Вы уверены, что хотите удалить этот термин?')) {
        fetch(`/api/terms/${termId}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Произошла ошибка при удалении термина');
        });
    }
}

function showAddTermModal() {
    // Очищаем форму
    document.getElementById('addForm').reset();
    document.getElementById('addRelatedTermsContainer').innerHTML = '';
    
    // Показываем модальное окно
    new bootstrap.Modal(document.getElementById('addModal')).show();
}

function addRelatedTermToNew() {
    const container = document.getElementById('addRelatedTermsContainer');
    const termGroup = document.createElement('div');
    termGroup.className = 'related-term-group mb-2';
    
    termGroup.innerHTML = `
        <div class="row">
            <div class="col-5">
                <input type="text" class="form-control form-control-sm related-term" 
                       placeholder="Связанный термин">
            </div>
            <div class="col-5">
                <input type="text" class="form-control form-control-sm relation-type" 
                       placeholder="Тип связи">
            </div>
            <div class="col-2">
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeRelatedTerm(this)">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(termGroup);
}

function saveNewTerm() {
    const container = document.getElementById('addRelatedTermsContainer');
    const groups = container.querySelectorAll('.related-term-group');
    const relatedTerms = [];
    const relations = {};
    
    groups.forEach(group => {
        const term = group.querySelector('.related-term').value.trim();
        const type = group.querySelector('.relation-type').value.trim();
        
        if (term) {
            relatedTerms.push(term);
            if (type) {
                relations[term] = type;
            }
        }
    });
    
    const data = {
        name: document.getElementById('addName').value,
        definition: document.getElementById('addDefinition').value,
        related_terms: relatedTerms,
        relations: relations,
        source: document.getElementById('addSource').value
    };

    fetch('/api/terms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при создании термина');
    });
} 