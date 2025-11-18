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

// Запускаем все функции после полной загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    setupCopyButton();
    setupExampleButtons();
});

document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');
    const examples = document.querySelectorAll('.example-item');
    const inputField = document.getElementById('sentence');
    const form = document.getElementById('fol-form');

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
});