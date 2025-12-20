document.addEventListener('DOMContentLoaded', () => {

    // --- TRANSLATION SYSTEM ---
    const translations = {
        es: {
            nav_features: "Características",
            nav_how: "Cómo Funciona",
            nav_contact: "Contacto",
            hero_title: "Gestión de Calidad sin Fronteras",
            hero_subtitle: "La plataforma multilingüe que Alexandra Farms necesita para gestionar reclamos de forma eficiente, transparente y centralizada.",
            hero_cta: "Descubrir Más",
            features_title: "Una Solución Integral",
            feature1_title: "100% Multilingüe",
            feature1_desc: "Disponible en Español, Inglés y Ruso para atender a sus clientes en más de 30 países sin barreras de comunicación.",
            feature2_title: "Centralización Rápida",
            feature2_desc: "Capture y valide reclamos instantáneamente, eliminando la pérdida de información y acelerando la atención.",
            feature3_title: "Flujo Automatizado",
            feature3_desc: "Distribuya inteligentemente cada incidencia al área responsable, asegurando un proceso estandarizado y ágil.",
            feature4_title: "Inteligencia de Negocio",
            feature4_desc: "Identifique tendencias y áreas de mejora en su cadena de producción con datos precisos y en tiempo real.",
            how_title: "Optimice su Proceso en 4 Pasos",
            how_step1_title: "Reporte",
            how_step1_desc: "El cliente reporta la incidencia de forma estructurada, adjuntando evidencia digital.",
            how_step2_title: "Validación",
            how_step2_desc: "El departamento de Control de Calidad revisa y valida el reclamo de manera obligatoria.",
            how_step3_title: "Resolución",
            how_step3_desc: "El sistema distribuye el caso y el equipo responsable trabaja en una solución eficiente.",
            how_step4_title: "Trazabilidad",
            how_step4_desc: "La gerencia y el equipo comercial tienen visibilidad completa del estado del reclamo.",
            testimonial_text: "\"Esta plataforma ha transformado nuestra comunicación con clientes. La rapidez y transparencia en el manejo de incidencias han fortalecido nuestra confianza y relación con Alexandra Farms.\"",
            testimonial_author: "- Director de Calidad, Cliente Internacional",
            cta_title: "¿Listo para Liderar en Calidad y Servicio?",
            cta_subtitle: "Implemente la herramienta que optimizará sus procesos y satisfará a sus clientes.",
            cta_button: "Acceder a la Plataforma",
            footer_rights: "Todos los derechos reservados."
        },
        en: {
            nav_features: "Features",
            nav_how: "How It Works",
            nav_contact: "Contact",
            hero_title: "Borderless Quality Management",
            hero_subtitle: "The multilingual platform Alexandra Farms needs to manage claims efficiently, transparently, and centrally.",
            hero_cta: "Discover More",
            features_title: "An Integral Solution",
            feature1_title: "100% Multilingual",
            feature1_desc: "Available in Spanish, English, and Russian to serve your clients in over 30 countries without communication barriers.",
            feature2_title: "Rapid Centralization",
            feature2_desc: "Capture and validate claims instantly, eliminating information loss and speeding up attention.",
            feature3_title: "Automated Workflow",
            feature3_desc: "Intelligently distribute each incident to the responsible area, ensuring a standardized and agile process.",
            feature4_title: "Business Intelligence",
            feature4_desc: "Identify trends and areas for improvement in your production chain with accurate, real-time data.",
            how_title: "Optimize Your Process in 4 Steps",
            how_step1_title: "Report",
            how_step1_desc: "The client reports the incident in a structured way, attaching digital evidence.",
            how_step2_title: "Validation",
            how_step2_desc: "The Quality Control department reviews and validates the claim as a mandatory step.",
            how_step3_title: "Resolution",
            how_step3_desc: "The system distributes the case and the responsible team works on an efficient solution.",
            how_step4_title: "Traceability",
            how_step4_desc: "Management and the commercial team have full visibility of the claim's status.",
            testimonial_text: "\"This platform has transformed our communication with clients. The speed and transparency in handling incidents have strengthened our trust and relationship with Alexandra Farms.\"",
            testimonial_author: "- Quality Director, International Client",
            cta_title: "Ready to Lead in Quality and Service?",
            cta_subtitle: "Implement the tool that will optimize your processes and satisfy your clients.",
            cta_button: "Access Platform",
            footer_rights: "All rights reserved."
        },
        ru: {
            nav_features: "Особенности",
            nav_how: "Как это работает",
            nav_contact: "Контакт",
            hero_title: "Управление качеством без границ",
            hero_subtitle: "Многоязычная платформа, необходимая Alexandra Farms для эффективного, прозрачного и централизованного управления претензиями.",
            hero_cta: "Узнать больше",
            features_title: "Комплексное решение",
            feature1_title: "100% Многоязычность",
            feature1_desc: "Доступна на испанском, английском и русском языках для обслуживания ваших клиентов в более чем 30 странах без языковых барьеров.",
            feature2_title: "Быстрая централизация",
            feature2_desc: "Мгновенно фиксируйте и проверяйте претензии, устраняя потерю информации и ускоряя рассмотрение.",
            feature3_title: "Автоматизированный рабочий процесс",
            feature3_desc: "Интеллектуально распределяйте каждый инцидент в ответственное подразделение, обеспечивая стандартизированный и гибкий процесс.",
            feature4_title: "Бизнес-аналитика",
            feature4_desc: "Выявляйте тенденции и области для улучшения в вашей производственной цепочке с помощью точных данных в реальном времени.",
            how_title: "Оптимизируйте ваш процесс за 4 шага",
            how_step1_title: "Сообщение",
            how_step1_desc: "Клиент сообщает о инциденте структурированно, прилагая цифровые доказательства.",
            how_step2_title: "Проверка",
            how_step2_desc: "Отдел контроля качества проверяет и утверждает претензию в качестве обязательного шага.",
            how_step3_title: "Решение",
            how_step3_desc: "Система распределяет дело, а ответственная команда работает над эффективным решением.",
            how_step4_title: "Отслеживаемость",
            how_step4_desc: "Руководство и коммерческая команда имеют полную видимость статуса претензии.",
            testimonial_text: "\"Эта платформа преобразовала наше общение с клиентами. Скорость и прозрачность в решении инцидентов укрепили наше доверие и отношения с Alexandra Farms.\"",
            testimonial_author: "- Директор по качеству, Международный клиент",
            cta_title: "Готовы лидировать в качестве и сервисе?",
            cta_subtitle: "Внедрите инструмент, который оптимизирует ваши процессы и удовлетворит ваших клиентов.",
            cta_button: "Доступ к платформе",
            footer_rights: "Все права защищены."
        }
    };

    const langButtons = document.querySelectorAll('.language-switcher button');
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    
    // Function to set the language
    const setLanguage = (lang) => {
        if (!translations[lang]) return;

        // Update HTML lang attribute
        document.documentElement.lang = lang;

        // Update button states
        langButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.lang === lang) {
                btn.classList.add('active');
            }
        });

        // Update text content
        elementsToTranslate.forEach(element => {
            const key = element.dataset.translate;
            if (translations[lang][key]) {
                element.textContent = translations[lang][key];
            }
        });
        
        // Save preference to localStorage
        localStorage.setItem('selectedLanguage', lang);
    };

    // Add click event to language buttons
    langButtons.forEach(button => {
        button.addEventListener('click', () => {
            const lang = button.dataset.lang;
            setLanguage(lang);
        });
    });

    // Check for saved language preference or use browser's default
    const savedLanguage = localStorage.getItem('selectedLanguage');
    const browserLang = navigator.language.split('-')[0]; // e.g., 'es' from 'es-ES'
    
    // Default to Spanish if no preference and browser lang is not supported
    const initialLang = translations[savedLanguage] ? savedLanguage : (translations[browserLang] ? browserLang : 'es');
    
    setLanguage(initialLang);

});