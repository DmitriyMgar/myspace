// Matrix Rain Animation and Effects

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация матричного дождя
    initMatrixRain();
    
    // Инициализация глитч-эффектов
    initGlitchEffects();
    
    // Инициализация эффекта печатающегося текста
    initTypewriterEffects();
    
    // Инициализация эффекта сканирования
    initScanEffect();
    
    // Инициализация анимированных границ
    initMatrixBorders();
});

// Матричный дождь
function initMatrixRain() {
    // Создаем canvas для матричного дождя
    const canvas = document.createElement('canvas');
    canvas.classList.add('matrix-rain');
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    // Устанавливаем размеры canvas
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Обработчик изменения размера окна
    window.addEventListener('resize', function() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
    
    // Символы для матричного дождя (включая кириллицу)
    const matrixChars = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ';
    
    // Капли дождя
    let drops = [];
    
    // Инициализация капель
    function initDrops() {
        drops = [];
        const columns = Math.floor(canvas.width / 30); // Увеличиваем расстояние между каплями
        
        for (let i = 0; i < columns; i++) {
            // Добавляем каплю только с 60% вероятностью для создания более разреженного эффекта
            if (Math.random() < 0.6) {
                drops.push({
                    x: i * 30,
                    y: Math.random() * -100,
                    speed: Math.random() * 1.5 + 0.8, // Немного снижаем скорость
                    length: Math.floor(Math.random() * 10) + 5 // Уменьшаем длину капель
                });
            }
        }
    }
    
    initDrops();
    
    // Функция отрисовки
    function draw() {
        // Полупрозрачный черный фон для создания эффекта следа (более темный)
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Настройки для символов
        ctx.font = '15px monospace';
        
        // Отрисовка каждой капли
        for (let i = 0; i < drops.length; i++) {
            const drop = drops[i];
            
            // Отрисовка символов в капле
            for (let j = 0; j < drop.length; j++) {
                // Первый символ ярче (голова капли), но затемненный
                if (j === 0) {
                    ctx.fillStyle = 'rgba(0, 180, 0, 0.7)'; // Затемненный зеленый
                } else {
                    // Остальные символы тускнеют с расстоянием и более прозрачные
                    const alpha = (1 - j / drop.length) * 0.5; // Уменьшаем прозрачность на 50%
                    ctx.fillStyle = `rgba(0, 180, 0, ${alpha})`;
                }
                
                // Случайный символ
                const char = matrixChars[Math.floor(Math.random() * matrixChars.length)];
                
                // Позиция символа
                const y = drop.y - j * 20;
                
                // Отрисовка символа
                if (y > 0 && y < canvas.height) {
                    ctx.fillText(char, drop.x, y);
                }
            }
            
            // Перемещение капли
            drop.y += drop.speed;
            
            // Если капля вышла за пределы экрана, создаем новую
            if (drop.y - drop.length * 20 > canvas.height) {
                drop.y = Math.random() * -100;
                drop.speed = Math.random() * 2 + 1;
                drop.length = Math.floor(Math.random() * 15) + 5;
            }
        }
        
        // Следующий кадр
        requestAnimationFrame(draw);
    }
    
    // Запуск анимации
    draw();
}

// Глитч-эффекты
function initGlitchEffects() {
    const glitchElements = document.querySelectorAll('.glitch-effect');
    
    glitchElements.forEach(element => {
        // Создаем обертку для глитч-эффекта
        const wrapper = document.createElement('div');
        wrapper.classList.add('glitch-wrapper');
        
        // Клонируем элемент для создания слоев глитча
        const original = element.cloneNode(true);
        const layer1 = element.cloneNode(true);
        const layer2 = element.cloneNode(true);
        
        // Добавляем классы для слоев
        layer1.classList.add('glitch-layer', 'glitch-layer-1');
        layer2.classList.add('glitch-layer', 'glitch-layer-2');
        
        // Заменяем оригинальный элемент оберткой с слоями
        element.parentNode.replaceChild(wrapper, element);
        wrapper.appendChild(original);
        wrapper.appendChild(layer1);
        wrapper.appendChild(layer2);
        
        // Запускаем глитч через случайные интервалы
        setInterval(() => {
            if (Math.random() > 0.95) {
                startGlitch(wrapper);
            }
        }, 500);
    });
    
    function startGlitch(wrapper) {
        const layers = wrapper.querySelectorAll('.glitch-layer');
        
        layers.forEach(layer => {
            // Случайные смещения для глитча
            const xOffset = (Math.random() - 0.5) * 10;
            const yOffset = (Math.random() - 0.5) * 10;
            
            // Применяем смещения
            layer.style.transform = `translate(${xOffset}px, ${yOffset}px)`;
            
            // Случайные искажения цвета
            if (Math.random() > 0.7) {
                layer.style.filter = `hue-rotate(${Math.random() * 360}deg)`;
            } else {
                layer.style.filter = '';
            }
        });
        
        // Возвращаем в нормальное состояние через короткое время
        setTimeout(() => {
            layers.forEach(layer => {
                layer.style.transform = '';
                layer.style.filter = '';
            });
        }, 100 + Math.random() * 200);
    }
}

// Эффект печатающегося текста
function initTypewriterEffects() {
    const typewriterElements = document.querySelectorAll('.typewriter-effect');
    
    typewriterElements.forEach(element => {
        const text = element.textContent;
        element.textContent = '';
        
        // Сохраняем оригинальный текст
        element.setAttribute('data-text', text);
        
        // Запускаем анимацию печати
        typeText(element, text);
    });
    
    function typeText(element, text, index = 0) {
        if (index < text.length) {
            element.textContent += text[index];
            
            // Случайная задержка для более реалистичного эффекта печати
            const delay = Math.random() * 50 + 50;
            
            setTimeout(() => {
                typeText(element, text, index + 1);
            }, delay);
        } else {
            // Когда текст напечатан, добавляем мигающий курсор
            element.classList.add('typewriter-cursor');
            
            // Через некоторое время можно повторить эффект
            setTimeout(() => {
                // Удаляем текст
                deleteText(element, text);
            }, 3000);
        }
    }
    
    function deleteText(element, text, index = text.length) {
        if (index > 0) {
            element.textContent = text.substring(0, index - 1);
            
            // Задержка для удаления
            const delay = Math.random() * 30 + 30;
            
            setTimeout(() => {
                deleteText(element, text, index - 1);
            }, delay);
        } else {
            // Когда текст удален, начинаем печатать снова
            setTimeout(() => {
                typeText(element, text);
            }, 1000);
        }
    }
}

// Эффект сканирования
function initScanEffect() {
    const scanElements = document.querySelectorAll('.scan-effect');
    
    scanElements.forEach(element => {
        // Создаем линию сканирования
        const scanLine = document.createElement('div');
        scanLine.classList.add('scan-line');
        
        // Добавляем позиционирование для родительского элемента
        if (getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
        }
        
        // Добавляем линию сканирования в элемент
        element.appendChild(scanLine);
        
        // Запускаем анимацию сканирования
        animateScan(scanLine);
    });
    
    function animateScan(scanLine) {
        // Начальная позиция
        let position = -100;
        
        function animate() {
            position += 2;
            
            // Перемещаем линию сканирования
            scanLine.style.top = position + '%';
            
            // Если линия вышла за пределы, начинаем заново
            if (position > 100) {
                position = -100;
            }
            
            // Следующий кадр
            requestAnimationFrame(animate);
        }
        
        animate();
    }
}

// Анимированные границы
function initMatrixBorders() {
    const borderElements = document.querySelectorAll('.matrix-border');
    
    borderElements.forEach(element => {
        // Создаем анимированные границы
        const topBorder = document.createElement('div');
        const rightBorder = document.createElement('div');
        const bottomBorder = document.createElement('div');
        const leftBorder = document.createElement('div');
        
        // Добавляем классы
        topBorder.classList.add('matrix-border-line', 'matrix-border-top');
        rightBorder.classList.add('matrix-border-line', 'matrix-border-right');
        bottomBorder.classList.add('matrix-border-line', 'matrix-border-bottom');
        leftBorder.classList.add('matrix-border-line', 'matrix-border-left');
        
        // Добавляем позиционирование для родительского элемента
        if (getComputedStyle(element).position === 'static') {
            element.style.position = 'relative';
        }
        
        // Добавляем границы в элемент
        element.appendChild(topBorder);
        element.appendChild(rightBorder);
        element.appendChild(bottomBorder);
        element.appendChild(leftBorder);
        
        // Запускаем анимацию границ
        animateBorders(element);
    });
    
    function animateBorders(element) {
        const borders = element.querySelectorAll('.matrix-border-line');
        
        // Последовательная анимация границ
        let index = 0;
        
        function animateNext() {
            // Сбрасываем предыдущую анимацию
            borders.forEach(border => {
                border.style.animation = 'none';
            });
            
            // Запускаем анимацию для текущей границы
            const border = borders[index];
            
            // Разные анимации для разных границ
            if (border.classList.contains('matrix-border-top')) {
                border.style.animation = 'matrix-border-horizontal 1s linear';
            } else if (border.classList.contains('matrix-border-right')) {
                border.style.animation = 'matrix-border-vertical 1s linear';
            } else if (border.classList.contains('matrix-border-bottom')) {
                border.style.animation = 'matrix-border-horizontal 1s linear reverse';
            } else {
                border.style.animation = 'matrix-border-vertical 1s linear reverse';
            }
            
            // Переход к следующей границе
            index = (index + 1) % borders.length;
            
            // Задержка перед следующей анимацией
            setTimeout(animateNext, 1000);
        }
        
        // Запуск анимации
        animateNext();
    }
} 