    let testCases = [];
    let filteredTestCases = [];
document.addEventListener("DOMContentLoaded", function () {


    fetch('/static/data/output_tc.json')
        .then(response => response.json())
        .then(data => {
            try {
                if (typeof data === 'string') {
                    data = JSON.parse(data); // ✅ Parse manually if string
                }

                if (Array.isArray(data)) {
                    testCases = data;
                    filteredTestCases = [...testCases];
                    console.log("✅ Cas de test chargés :", testCases);

                    updateStats();
                    renderTable();
                } else {
                    console.error("❌ Le JSON n'est pas un tableau :", data);
                }
            } catch (e) {
                console.error("❌ Erreur de parsing JSON :", e);
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors du chargement du JSON :', error);
        });



         const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.addEventListener('input', function (e) {
                    const searchTerm = e.target.value.toLowerCase();
                    filteredTestCases = testCases.filter(testCase =>
                        testCase.fields.summary.toLowerCase().includes(searchTerm) ||
                        testCase.fields.description.toLowerCase().includes(searchTerm) ||
                        testCase.xray_test_repository_folder.toLowerCase().includes(searchTerm) ||
                        testCase.steps.some(step =>
                            step.action.toLowerCase().includes(searchTerm) ||
                            step.result.toLowerCase().includes(searchTerm)
                        )
                    );
                    renderTable();
                });
                }


                 const importBtn = document.getElementById('importBtn');
                 if (importBtn) {
                     importBtn.addEventListener('click', () => {
                         fetch('/import-xray', {
                             method: 'POST'
                         })
                         .then(response => {
                             if (response.redirected) {
                                 window.location.href = response.url;
                             } else {
                                 return response.text();
                             }
                         })
                         .then(data => {
                             if (data) {
                                 document.body.innerHTML = data;
                             }
                         })
                         .catch(error => {
                             console.error('Erreur lors de l’importation vers Xray:', error);
                             alert('Erreur lors de l’importation vers Xray.');
                         });
                     });
                 } else {
                     console.error('Le bouton #importBtn n’a pas été trouvé dans le DOM.');
                 }


});


    // Modal functionality
    document.querySelector('.close').onclick = closeModal;
    window.onclick = function(event) {
        if (event.target == document.getElementById('editModal')) {
            closeModal();
        }
    }

    // Form submission
    document.getElementById('editForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveTest();
    });

    // Make functions available globally
    window.editTest = editTest;
    window.deleteTest = deleteTest;
    window.addStep = addStep;
    window.removeStep = removeStep;

    function closeModal() {
        document.getElementById('editModal').style.display = 'none';
    }

    function updateStats() {

        const totalTests = testCases.length;
        const totalSteps = testCases.reduce((sum, tc) => sum + tc.steps.length, 0);
        const avgSteps = totalTests ? Math.round(totalSteps / totalTests * 10) / 10 : 0;

        document.getElementById('totalTests').textContent = totalTests;
        document.getElementById('totalSteps').textContent = totalSteps;
        document.getElementById('avgSteps').textContent = avgSteps;
    }

    function renderTable() {
        const tbody = document.getElementById('testTableBody');
        const noData = document.getElementById('noData');
        const table = document.getElementById('testTable');

        if (filteredTestCases.length === 0) {
            table.style.display = 'none';
            noData.style.display = 'block';
            return;
        }

        table.style.display = 'table';
        noData.style.display = 'none';
        noData.style.display = 'none';

        tbody.innerHTML = filteredTestCases.map((testCase, index) => `
            <tr>
                <td><strong>${index + 1}</strong></td>
                <td>
                    <div class="test-summary">${testCase.fields.summary}</div>
                </td>
                <td>
                    <div class="test-description" title="${testCase.fields.description}">
                        ${testCase.fields.description}
                    </div>
                </td>
                <td>
                    <div class="meta-item">${testCase.fields.project.key}</div>
                </td>
                <td>
                    <div class="meta-item">${testCase.fields.fixVersions && testCase.fields.fixVersions[0] ? testCase.fields.fixVersions[0].name : 'N/A'}</div>
                </td>
                <td>
                    <div class="test-steps">
                        ${testCase.steps.map((step, stepIndex) => `
                            <div class="step-item">
                                <div class="step-action">
                                    <strong>${stepIndex + 1}.</strong> ${step.action.substring(0, 80)}${step.action.length > 80 ? '...' : ''}
                                </div>
                                <div class="step-result">
                                    → ${step.result.substring(0, 60)}${step.result.length > 60 ? '...' : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </td>
                <td>
                    <div class="folder-path" title="${testCase.fields.xray_test_repository_folder}">
                        ${testCase.xray_test_repository_folder.length > 30 ?
                          testCase.xray_test_repository_folder.substring(0, 30) + '...' :
                          testCase.xray_test_repository_folder}
                    </div>
                </td>
                <td class="actions-cell">
                    <div class="action-buttons-cell">
                        <button class="btn btn-warning btn-small" onclick="editTest(${index})" title="Modifier">
                            ✏️ Modifier
                        </button>
                        <button class="btn btn-danger btn-small" onclick="deleteTest(${index})" title="Supprimer">
                            🗑️ Supprimer
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    function editTest(index) {
        currentEditIndex = index;
        const testCase = filteredTestCases[index];

        document.getElementById('modalTitle').textContent = 'Modifier le cas de test';
        document.getElementById('editSummary').value = testCase.fields.summary;
        document.getElementById('editDescription').value = testCase.fields.description;
        document.getElementById('editVersion').value = testCase.fields.fixVersions && testCase.fields.fixVersions[0] ? testCase.fields.fixVersions[0].name : '';
        document.getElementById('editFolder').value = testCase.xray_test_repository_folder;

        renderSteps(testCase.steps);
        document.getElementById('editModal').style.display = 'block';
    }

        function addNewTest() {
            currentEditIndex = 0;
            const testCase = filteredTestCases[0];

            document.getElementById('modalTitle').textContent = 'Ajouter le cas de test';
            document.getElementById('editSummary').value = "";
            document.getElementById('editDescription').value = "";
            document.getElementById('editVersion').value = testCase.fields.fixVersions && testCase.fields.fixVersions[0] ? testCase.fields.fixVersions[0].name : '';
            document.getElementById('editFolder').value = testCase.xray_test_repository_folder;

            renderSteps([]);
            document.getElementById('editModal').style.display = 'block';
        }


    function renderSteps(steps) {
        const stepsList = document.getElementById('stepsList');
        stepsList.innerHTML = steps.map((step, index) => `
            <div class="form-group" data-step-index="${index}">
                <label>Étape ${index + 1}:</label>
                <input type="text" placeholder="Action" value="${step.action}" class="step-action-input">
                <textarea placeholder="Résultat attendu" class="step-result-input">${step.result}</textarea>
                <button type="button" class="btn btn-danger btn-small" onclick="removeStep(${index})">
                    🗑️ Supprimer
                </button>
            </div>
        `).join('');
    }

    function addStep() {
        const stepsList = document.getElementById('stepsList');
        const stepIndex = stepsList.children.length;

        const stepDiv = document.createElement('div');
        stepDiv.className = 'form-group';
        stepDiv.setAttribute('data-step-index', stepIndex);
        stepDiv.innerHTML = `
            <label>Étape ${stepIndex + 1}:</label>
            <input type="text" placeholder="Action" class="step-action-input">
            <textarea placeholder="Résultat attendu" class="step-result-input"></textarea>
            <button type="button" class="btn btn-danger btn-small" onclick="removeStep(${stepIndex})">
                🗑️ Supprimer
            </button>
        `;

        stepsList.appendChild(stepDiv);
    }

    function removeStep(index) {
        const stepsList = document.getElementById('stepsList');
        const stepElement = stepsList.querySelector(`[data-step-index="${index}"]`);
        if (stepElement) {
            stepElement.remove();
            // Re-index remaining steps
            Array.from(stepsList.children).forEach((step, newIndex) => {
                step.setAttribute('data-step-index', newIndex);
                step.querySelector('label').textContent = `Étape ${newIndex + 1}:`;
                step.querySelector('button').setAttribute('onclick', `removeStep(${newIndex})`);
            });
        }
    }

    function saveTest() {
        const summary = document.getElementById('editSummary').value;
        const description = document.getElementById('editDescription').value;
        const version = document.getElementById('editVersion').value;
        const folder = document.getElementById('editFolder').value;

        if (!summary.trim()) {
            alert('Le résumé est obligatoire!');
            return;
        }

        // Collect steps
        const stepInputs = document.querySelectorAll('#stepsList .form-group');
        const steps = Array.from(stepInputs).map(stepDiv => {
            const action = stepDiv.querySelector('.step-action-input').value;
            const result = stepDiv.querySelector('.step-result-input').value;
            return {
                action: action,
                data: "",
                result: result
            };
        }).filter(step => step.action.trim() || step.result.trim());

        if (currentEditIndex >= 0) {
            // Update existing test
            const originalIndex = testCases.findIndex(tc => tc === filteredTestCases[currentEditIndex]);
            if (originalIndex >= 0) {
                testCases[originalIndex] = {
                    ...testCases[originalIndex],
                    fields: {
                        ...testCases[originalIndex].fields,
                        summary: summary,
                        description: description,
                        fixVersions: [{ name: version }]
                    },
                    steps: steps,
                    xray_test_repository_folder: folder
                };

                filteredTestCases[currentEditIndex] = testCases[originalIndex];
            }
        } else {
            // Add new test
            const newTest = {
                "testtype": "Manual",
                "fields": {
                    "project": {
                        "key": "CDT"
                    },
                    "fixVersions": [{
                        "name": version
                    }],
                    "summary": summary,
                    "description": description
                },
                "steps": steps,
                "xray_test_repository_folder": folder
            };

            testCases.push(newTest);
            filteredTestCases = [...testCases];
        }

         fetch('/save_tests', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(testCases)
            })
            .then(response => response.json())
            .then(result => {
                if (result.message) {
                         updateStats();
                            renderTable();
                            closeModal();

                            alert(currentEditIndex >= 0 ?
                                '✅ Cas de test modifié avec succès!' :
                                '✅ Nouveau cas de test créé avec succès!');
                } else {
                    alert('❌ Erreur: ' + result.error);
                }
            })
            .catch(error => {
                console.error('❌ Erreur réseau :', error);
                alert('❌ Erreur réseau');
            });


    }

    function deleteTest(index) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce cas de test ?')) {
            const originalIndex = testCases.findIndex(tc => tc === filteredTestCases[index]);
            if (originalIndex >= 0) {
                testCases.splice(originalIndex, 1);
                filteredTestCases.splice(index, 1);
//                updateStats();
                renderTable();
                alert('✅ Cas de test supprimé avec succès!');
            }
        }
    }

//document.getElementById('importBtn').addEventListener('click', () => {
//    fetch('/import-xray', {
//        method: 'POST'
//    })
//    .then(response => {
//        if (response.redirected) {
//            // Si le backend redirige, on suit la redirection
//            window.location.href = response.url;
//        } else {
//            return response.text();  // Si erreur, afficher le HTML reçu
//        }
//    })
//    .then(data => {
//        if (data) {
//            document.body.innerHTML = data;  // Affiche la page d’erreur par exemple
//        }
//    })
//    .catch(error => {
//        console.error('Erreur lors de l’importation vers Xray:', error);
//        alert('Erreur lors de l’importation vers Xray.');
//    });
//});


