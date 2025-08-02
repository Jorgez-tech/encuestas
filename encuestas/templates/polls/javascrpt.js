// polls/static/polls/scripts.js
document.addEventListener('DOMContentLoaded', function() {
    const pollsContainer = document.getElementById('polls-container');

    // Simulación de datos de encuestas
    const polls = [
        {
            question: "¿Cuál es tu lenguaje de programación favorito?",
            choices: ["Python", "JavaScript", "Java", "C++"]
        },
        {
            question: "¿Cuál es tu sistema operativo preferido?",
            choices: ["Windows", "macOS", "Linux", "Otro"]
        }
    ];

    // Función para renderizar encuestas
    function renderPolls() {
        polls.forEach(poll => {
            const pollElement = document.createElement('div');
            pollElement.className = 'poll';

            const questionElement = document.createElement('h2');
            questionElement.textContent = poll.question;
            pollElement.appendChild(questionElement);

            poll.choices.forEach(choice => {
                const choiceElement = document.createElement('p');
                choiceElement.textContent = choice;
                pollElement.appendChild(choiceElement);
            });

            pollsContainer.appendChild(pollElement);
        });
    }

    // Renderizar encuestas al cargar la página
    renderPolls();
});