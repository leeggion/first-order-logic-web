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