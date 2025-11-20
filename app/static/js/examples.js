// examples.js - общие функции для всех страниц

/**
 * 1. Копирование формулы FOL в буфер обмена.
 */
function setupCopyButton() {
    // 1. Ищем заголовок, к которому прикрепим кнопку
    const folTitle = document.querySelector('.fol-title');
    // 2. Ищем элемент с текстом формулы, который нужно скопировать
    const folTextElement = document.querySelector('.fol-formula-text');

    if (folTextElement && folTitle) {
        // Создаем кнопку "Копировать"
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Копировать';
        copyButton.classList.add('copy-btn');

        // Вставляем кнопку рядом с заголовком FOL
        // Заголовок <h3> теперь будет содержать и текст, и кнопку
        folTitle.appendChild(copyButton);

        copyButton.addEventListener('click', () => {
            const folText = folTextElement.textContent.trim();

            navigator.clipboard.writeText(folText)
                .then(() => {
                    // Краткая обратная связь
                    copyButton.textContent = 'Скопировано!';
                    copyButton.disabled = true;
                    setTimeout(() => {
                        copyButton.textContent = 'Копировать';
                        copyButton.disabled = false;
                    }, 1500);
                })
                .catch(err => {
                    console.error('Ошибка копирования:', err);
                    alert('Не удалось скопировать текст.');
                });
        });
    }
}

/**
 * 2. Вставка примера предложения в поле ввода.
 * @param {string} sentence - Предложение для вставки.
 */
function insertExample(sentence) {
    const inputField = document.getElementById('sentence');
    if (inputField) {
        inputField.value = sentence;
        // Фокусируемся на поле и подсвечиваем его
        inputField.focus();
    }
}

/**
 * 3. Настройка обработчиков событий для кнопок-примеров.
 */
function setupExampleButtons() {
    const exampleButtons = document.querySelectorAll('.example-btn');
    exampleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const exampleText = button.getAttribute('data-example');
            insertExample(exampleText);
        });
    });
}

/**
 * 4. Универсальная функция для вставки примеров из .example-item
 */
function setupExampleItems() {
    const examples = document.querySelectorAll('.example-item');
    const inputField = document.getElementById('sentence');
    
    examples.forEach(ex => {
        ex.addEventListener('click', () => {
            const text = ex.getAttribute('data-text');
            if (inputField) {
                inputField.value = text;
                inputField.focus();
            }
        });
    });
}

/**
 * 5. Универсальная функция для копирования текста по data-target
 */
function setupUniversalCopyButtons() {
    const copyButtons = document.querySelectorAll('.copy-btn[data-target]');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const text = targetElement.textContent.trim();

            navigator.clipboard.writeText(text)
                .then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Скопировано!';
                    this.disabled = true;
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.disabled = false;
                    }, 1500);
                })
                .catch(err => {
                    console.error('Ошибка копирования:', err);
                    alert('Не удалось скопировать текст.');
                });
        });
    });
}

/**
 * 6. Логика табов для страницы с примерами
 */
function setupExampleTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');
    const examples = document.querySelectorAll('.example-item');
    const inputField = document.getElementById('sentence');
    const form = document.getElementById('fol-form');

    // Если нет табов на странице - выходим
    if (tabs.length === 0) return;

    // Ключ для хранения активного таба в localStorage
    const STORAGE_KEY = 'activeTabId';

    // --- 1. Логика переключения табов и СОХРАНЕНИЯ состояния ---
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-target');

            // 1.1 Сохранение состояния в localStorage
            localStorage.setItem(STORAGE_KEY, targetId);

            // 1.2 Стандартная логика переключения
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // --- 2. Логика клика по примеру ---
    examples.forEach(ex => {
        ex.addEventListener('click', () => {
            const text = ex.getAttribute('data-text');
            if (inputField) {
                inputField.value = text;
            }

            // Здесь мы не сохраняем состояние, так как клик по примеру 
            // должен происходить только после выбора активного таба.

            if (form) {
                form.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }

            if (inputField) {
                inputField.focus();
            }
        });
    });

    // --- 3. Инициализация (ВОССТАНОВЛЕНИЕ состояния) ---
    const storedTabId = localStorage.getItem(STORAGE_KEY);

    if (storedTabId) {
        // Находим кнопку и контент по сохраненному ID
        const activeTab = document.querySelector(`.tab-btn[data-target="${storedTabId}"]`);
        const activeContent = document.getElementById(storedTabId);

        // Если оба элемента найдены, активируем их
        if (activeTab && activeContent) {
            // Сначала сбрасываем все (на случай, если Jinja2 не сработал или таб был активен по умолчанию)
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            activeTab.classList.add('active');
            activeContent.classList.add('active');
        } else {
            // Если сохраненный ID неверен или не существует, активируем первый таб
            tabs[0].classList.add('active');
            contents[0].classList.add('active');
        }
    } else {
        // Если ничего не сохранено, активируем первый таб по умолчанию
        tabs[0].classList.add('active');
        contents[0].classList.add('active');
    }
}

/**
 * 7. Логика выбора нейросети ДО формы
 */
function setupNeuralSelection() {
    const neuralTabs = document.querySelectorAll('.neural-selection .tab-btn');
    const neuralContents = document.querySelectorAll('.neural-results-container .tab-content');

    // Если нет выбора нейросети на странице - выходим
    if (neuralTabs.length === 0) return;

    // Ключ для хранения выбранной нейросети
    const NEURAL_SELECTION_KEY = 'selectedNeuralNetwork';

    // Логика выбора нейросети
    neuralTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-target');

            // Сохранение выбора в localStorage
            localStorage.setItem(NEURAL_SELECTION_KEY, targetId);

            // Переключение активного состояния
            neuralTabs.forEach(t => t.classList.remove('active'));
            neuralContents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // Инициализация выбора нейросети
    const storedNeuralId = localStorage.getItem(NEURAL_SELECTION_KEY);

    if (storedNeuralId) {
        const activeNeuralTab = document.querySelector(`.neural-selection .tab-btn[data-target="${storedNeuralId}"]`);
        const activeNeuralContent = document.getElementById(storedNeuralId);

        if (activeNeuralTab && activeNeuralContent) {
            neuralTabs.forEach(t => t.classList.remove('active'));
            neuralContents.forEach(c => c.classList.remove('active'));

            activeNeuralTab.classList.add('active');
            activeNeuralContent.classList.add('active');
        } else {
            // Если сохраненный выбор невалиден, активируем первый
            neuralTabs[0].classList.add('active');
            neuralContents[0].classList.add('active');
        }
    } else {
        // По умолчанию активируем первую нейросеть
        neuralTabs[0].classList.add('active');
        neuralContents[0].classList.add('active');
    }
}

// Обнови вызов в конце файла:
document.addEventListener('DOMContentLoaded', () => {
    setupCopyButton();
    setupExampleButtons();
    setupExampleItems();
    setupUniversalCopyButtons();
    setupExampleTabs();
    setupNeuralSelection();
});