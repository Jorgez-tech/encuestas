// JavaScript para la aplicación de encuestas
document.addEventListener('DOMContentLoaded', function () {
    // Agregar efectos de hover a las tarjetas de encuestas
    const pollCards = document.querySelectorAll('.poll-card');

    pollCards.forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.borderColor = '#667eea';
        });

        card.addEventListener('mouseleave', function () {
            this.style.borderColor = '#e9ecef';
        });
    });

    // Agregar animación a los botones de voto (solo efectos visuales)
    const voteButtons = document.querySelectorAll('.vote-button');

    voteButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            // No prevenir el comportamiento por defecto para permitir navegación

            // Crear efecto de ripple
            const ripple = document.createElement('span');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255,255,255,0.6)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.left = e.offsetX + 'px';
            ripple.style.top = e.offsetY + 'px';
            ripple.style.width = '20px';
            ripple.style.height = '20px';

            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);

            // Permitir que el enlace funcione normalmente
            // No usar alert ni preventDefault
        });
    });

    // Agregar estilo CSS para la animación del ripple
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Animación de entrada para las tarjetas
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    pollCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});