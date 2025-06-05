// Основной JavaScript файл для Киберблога

document.addEventListener('DOMContentLoaded', function() {
    
    // Инициализация Bootstrap компонентов
    initBootstrapComponents();
    
    // Инициализация эффектов киберпанк-стиля
    initCyberpunkEffects();
    
    // Обработчики для форм
    setupFormHandlers();
    
    // Обработчики для комментариев
    setupCommentHandlers();
    
    // Переключатель темной темы
    setupThemeToggle();
    
    // Анимации при прокрутке
    setupScrollAnimations();
    
    // Обработчики для мобильной навигации
    setupMobileNavigation();
    
    // Инициализация счетчика просмотров
    initViewCounter();
});

// Инициализация Bootstrap компонентов
function initBootstrapComponents() {
    // Тултипы
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Поповеры
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Тосты
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
}

// Инициализация эффектов киберпанк-стиля
function initCyberpunkEffects() {
    // Эффект глитча для текста
    const glitchTexts = document.querySelectorAll('.glitch-text');
    glitchTexts.forEach(text => {
        const textContent = text.textContent;
        text.setAttribute('data-text', textContent);
    });
    
    // Эффект печатающегося текста
    const typewriterTexts = document.querySelectorAll('.typewriter-text');
    typewriterTexts.forEach(text => {
        const textContent = text.textContent;
        text.textContent = '';
        let i = 0;
        const typeSpeed = 50; // скорость печати в мс
        
        function typeWriter() {
            if (i < textContent.length) {
                text.textContent += textContent.charAt(i);
                i++;
                setTimeout(typeWriter, typeSpeed);
            }
        }
        
        typeWriter();
    });
    
    // Добавление эффекта шума
    if (!document.querySelector('.noise-overlay')) {
        const noiseOverlay = document.createElement('div');
        noiseOverlay.classList.add('noise-overlay');
        document.body.appendChild(noiseOverlay);
    }
    
    // Анимация для линий с подсветкой
    const glowLines = document.querySelectorAll('.glow-line');
    glowLines.forEach(line => {
        // Уже имеет анимацию через CSS
    });
}

// Обработчики для форм
function setupFormHandlers() {
    // Валидация форм
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Обработка загрузки файлов
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', (e) => {
            const fileName = e.target.files[0].name;
            const nextSibling = e.target.nextElementSibling;
            nextSibling.innerText = fileName;
        });
    });
    
    // Предварительный просмотр изображений
    const imageInputs = document.querySelectorAll('.image-preview-input');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            const previewId = this.dataset.previewTarget;
            const previewElement = document.getElementById(previewId);
            
            if (previewElement && this.files && this.files[0]) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    previewElement.src = e.target.result;
                    previewElement.style.display = 'block';
                }
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
}

// Обработчики для комментариев
function setupCommentHandlers() {
    // Ответ на комментарий
    const replyButtons = document.querySelectorAll('.comment-reply-btn');
    replyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const commentAuthor = this.dataset.commentAuthor;
            const replyForm = document.getElementById('comment-form');
            
            // Прокрутка к форме комментария
            replyForm.scrollIntoView({ behavior: 'smooth' });
            
            // Установка ID родительского комментария
            document.getElementById('parent_id').value = commentId;
            
            // Обновление текста формы
            const replyTo = document.getElementById('reply-to');
            if (replyTo) {
                replyTo.textContent = `Ответ для ${commentAuthor}`;
                replyTo.style.display = 'block';
            }
            
            // Добавление кнопки отмены
            const cancelReply = document.getElementById('cancel-reply');
            if (cancelReply) {
                cancelReply.style.display = 'inline-block';
            }
            
            // Фокус на поле ввода
            document.getElementById('comment-content').focus();
        });
    });
    
    // Отмена ответа на комментарий
    const cancelReplyButton = document.getElementById('cancel-reply');
    if (cancelReplyButton) {
        cancelReplyButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Сброс ID родительского комментария
            document.getElementById('parent_id').value = '';
            
            // Скрытие текста "Ответ для..."
            const replyTo = document.getElementById('reply-to');
            if (replyTo) {
                replyTo.style.display = 'none';
            }
            
            // Скрытие кнопки отмены
            this.style.display = 'none';
        });
    }
    
    // Реакции на комментарии
    const reactionButtons = document.querySelectorAll('.reaction-btn');
    reactionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            const reactionType = this.dataset.reactionType;
            
            // Отправка AJAX-запроса для сохранения реакции
            fetch('/blog/reaction', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    post_id: postId,
                    reaction_type: reactionType
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Обновление счетчика реакций
                    const countElement = this.querySelector('.reaction-count');
                    if (countElement) {
                        countElement.textContent = data.count;
                    }
                    
                    // Переключение активного состояния
                    if (data.active) {
                        this.classList.add('active');
                    } else {
                        this.classList.remove('active');
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка при сохранении реакции:', error);
            });
        });
    });
}

// Получение CSRF-токена из cookie
function getCsrfToken() {
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    
    return '';
}

// Переключатель тем
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const matrixStylesheet = document.getElementById('matrix-stylesheet');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = localStorage.getItem('theme') || 'dark-theme';
            
            // Циклическое переключение между темами: dark-theme -> light-theme -> matrix-theme -> dark-theme
            if (currentTheme === 'dark-theme') {
                // Переключение на светлую тему
                document.documentElement.classList.remove('dark-theme');
                document.documentElement.classList.remove('matrix-theme');
                document.documentElement.classList.add('light-theme');
                localStorage.setItem('theme', 'light-theme');
                themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
                
                // Удаление матричных эффектов
                removeMatrixEffects();
            } 
            else if (currentTheme === 'light-theme') {
                // Переключение на матричную тему
                document.documentElement.classList.remove('light-theme');
                document.documentElement.classList.remove('dark-theme');
                document.documentElement.classList.add('matrix-theme');
                localStorage.setItem('theme', 'matrix-theme');
                themeToggle.innerHTML = '<i class="fas fa-lightbulb"></i>';
                
                // Инициализация матричных эффектов
                setTimeout(() => {
                    initMatrixEffects();
                }, 100);
            }
            else {
                // Переключение на темную тему
                document.documentElement.classList.remove('light-theme');
                document.documentElement.classList.remove('matrix-theme');
                document.documentElement.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark-theme');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
                
                // Удаление матричных эффектов
                removeMatrixEffects();
            }
        });
        
        // Установка начальной темы
        const savedTheme = localStorage.getItem('theme') || 'dark-theme';
        document.documentElement.classList.add(savedTheme);
        
        if (savedTheme === 'light-theme') {
            themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        } 
        else if (savedTheme === 'matrix-theme') {
            themeToggle.innerHTML = '<i class="fas fa-lightbulb"></i>';
            // Инициализация матричных эффектов
            setTimeout(() => {
                initMatrixEffects();
            }, 100);
        }
        else {
            themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        }
    }
}

// Инициализация матричных эффектов
function initMatrixEffects() {
    // Проверка, загружен ли скрипт с матричными эффектами
    if (typeof initMatrixRain === 'function') {
        initMatrixRain();
    }
    
    // Добавление классов для эффектов
    document.querySelectorAll('.navbar-brand, h1, h2, h3').forEach(el => {
        el.classList.add('glitch-effect');
    });
    
    document.querySelectorAll('.card, .post-card').forEach(el => {
        el.classList.add('matrix-border');
    });
    
    document.querySelectorAll('.btn-cyber-primary').forEach(el => {
        el.classList.add('matrix-pulse');
    });
    
    document.querySelectorAll('.lead, .post-excerpt').forEach(el => {
        el.classList.add('typewriter-effect');
    });
}

// Удаление матричных эффектов
function removeMatrixEffects() {
    // Удаление canvas с матричным дождем
    const matrixCanvas = document.querySelector('.matrix-rain');
    if (matrixCanvas) {
        matrixCanvas.remove();
    }
    
    // Удаление классов эффектов
    document.querySelectorAll('.glitch-effect').forEach(el => {
        el.classList.remove('glitch-effect');
    });
    
    document.querySelectorAll('.matrix-border').forEach(el => {
        el.classList.remove('matrix-border');
        
        // Удаление анимированных границ
        el.querySelectorAll('.matrix-border-line').forEach(line => {
            line.remove();
        });
    });
    
    document.querySelectorAll('.matrix-pulse').forEach(el => {
        el.classList.remove('matrix-pulse');
    });
    
    document.querySelectorAll('.typewriter-effect').forEach(el => {
        el.classList.remove('typewriter-effect');
    });
}

// Анимации при прокрутке
function setupScrollAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });
    
    fadeElements.forEach(element => {
        observer.observe(element);
    });
}

// Обработчики для мобильной навигации
function setupMobileNavigation() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
}

// Инициализация счетчика просмотров
function initViewCounter() {
    const postElement = document.querySelector('.post-full');
    if (postElement) {
        const postId = postElement.dataset.postId;
        if (postId) {
            // Проверка, просматривал ли пользователь эту статью
            const viewedPosts = JSON.parse(localStorage.getItem('viewedPosts') || '[]');
            
            if (!viewedPosts.includes(postId)) {
                // Отправка AJAX-запроса для увеличения счетчика просмотров
                fetch(`/blog/view/${postId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Добавление ID статьи в просмотренные
                        viewedPosts.push(postId);
                        localStorage.setItem('viewedPosts', JSON.stringify(viewedPosts));
                        
                        // Обновление счетчика просмотров на странице
                        const viewCountElement = document.querySelector('.post-views-count');
                        if (viewCountElement) {
                            viewCountElement.textContent = data.view_count;
                        }
                    }
                })
                .catch(error => {
                    console.error('Ошибка при увеличении счетчика просмотров:', error);
                });
            }
        }
    }
}

// Функция для копирования текста в буфер обмена
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        const msg = successful ? 'успешно скопирован' : 'не удалось скопировать';
        console.log(`Текст ${msg}`);
    } catch (err) {
        console.error('Ошибка при копировании текста:', err);
    }
    
    document.body.removeChild(textarea);
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.classList.add('notification', `notification-${type}`);
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-message">${message}</div>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Показ уведомления с анимацией
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
    
    // Обработчик для кнопки закрытия
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    });
}

// Функция для плавной прокрутки к элементу
function scrollToElement(elementId, offset = 0) {
    const element = document.getElementById(elementId);
    if (element) {
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - offset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
} 