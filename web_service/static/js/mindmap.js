function initMindmap(terms) {
    console.log('Terms data:', terms);  // Для отладки
    
    // Подготовка данных для графа
    const elements = {
        nodes: [],
        edges: []
    };
    
    // Создаем узлы
    const nodeMap = new Map();
    
    // Сначала добавляем все основные термины
    terms.forEach(term => {
        if (!term || !term.id || !term.name) {
            console.error('Invalid term data:', term);
            return;
        }
        const normalizedName = term.name.toLowerCase();
        elements.nodes.push({
            data: {
                id: term.id.toString(),
                label: term.name,
                normalizedName: normalizedName,
                definition: term.definition || '',
                source: term.source || '',
                type: 'main',
                created: term.created_at || '',
                updated: term.updated_at || ''
            }
        });
        nodeMap.set(normalizedName, {
            id: term.id.toString(),
            originalName: term.name,
            type: 'main'
        });
    });
    
    // Затем добавляем связанные термины, только если они еще не существуют
    terms.forEach(term => {
        if (Array.isArray(term.related_terms)) {
            term.related_terms.forEach(related => {
                if (!related) return;
                const relatedLower = related.toLowerCase();
                
                // Проверяем, существует ли уже термин с таким именем (независимо от регистра)
                if (!nodeMap.has(relatedLower)) {
                    const relatedId = `related_${relatedLower}`; // Используем нормализованное имя для ID
                    elements.nodes.push({
                        data: {
                            id: relatedId,
                            label: related,
                            normalizedName: relatedLower,
                            type: 'related'
                        }
                    });
                    nodeMap.set(relatedLower, {
                        id: relatedId,
                        originalName: related,
                        type: 'related'
                    });
                }
            });
        }
    });
    
    // Создаем связи, используя нормализованные имена
    terms.forEach(term => {
        if (Array.isArray(term.related_terms)) {
            term.related_terms.forEach(related => {
                if (!related) return;
                const normalizedRelated = related.toLowerCase();
                const targetNode = nodeMap.get(normalizedRelated);
                
                if (!targetNode) {
                    console.warn(`Missing related term: ${related} for ${term.name}`);
                    return;
                }
                
                // Используем оригинальное имя для метки связи
                const relationLabel = term.relations[related] || term.relations[targetNode.originalName] || 'связан с';
                
                elements.edges.push({
                    data: {
                        source: term.id.toString(),
                        target: targetNode.id,
                        label: relationLabel
                    }
                });
            });
        }
    });

    // Инициализация Cytoscape
    const cy = cytoscape({
        container: document.getElementById('mindmap'),
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-wrap': 'wrap',
                    'text-max-width': '100px',
                    'font-size': '12px',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': '#4CAF50',
                    'width': '120px',
                    'height': '40px',
                    'shape': 'roundrectangle'
                }
            },
            {
                selector: 'node[type="related"]',
                style: {
                    'background-color': '#2196F3'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#666',
                    'target-arrow-color': '#666',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10
                }
            }
        ],
        layout: {
            name: 'cola',
            nodeSpacing: 100,
            edgeLengthVal: 200,
            animate: true,
            randomize: false,
            maxSimulationTime: 1500
        }
    });

    // Применяем layout после инициализации
    const layout = cy.layout({
        name: 'preset',  // Сначала используем preset layout
        fit: true,
        padding: 50
    });
    layout.run();

    // Затем применяем cola layout
    setTimeout(() => {
        const colaLayout = cy.layout({
            name: 'cola',
            fit: true,
            padding: 50,
            nodeSpacing: function(node){ return 40; },
            edgeLength: function(edge){ return 80; },
            infinite: true
        });
        colaLayout.run();
    }, 100);

    // Обработчик клика по узлу
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        const data = node.data();
        
        let html = `<h6>${data.label}</h6>`;
        if (data.definition) {
            html += `<p>${data.definition}</p>`;
        }
        if (data.source) {
            html += `<p><small class="text-muted">Источник: ${data.source}</small></p>`;
        }
        if (data.created) {
            html += `
                <p class="text-muted mb-0"><small>
                    Создан: ${data.created}<br>
                    Обновлен: ${data.updated}
                </small></p>
            `;
        }
        
        document.getElementById('term-info').innerHTML = html;
    });

    // Масштабирование графа при загрузке
    cy.fit(50);
} 