// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract VotingContract is Ownable, ReentrancyGuard {
    // Estructura para una pregunta de encuesta
    struct Question {
        string questionText;
        string[] choices;
        mapping(uint => uint) votes; // choice_index => vote_count
        bool isActive;
        uint totalVotes;
    }
    
    // Mapeo de preguntas
    mapping(uint => Question) public questions;
    uint public questionCounter;
    
    // Mapeo para evitar votos duplicados por dirección y pregunta
    mapping(address => mapping(uint => bool)) public hasVoted;
    
    // Eventos
    event QuestionCreated(uint indexed questionId, string questionText);
    event VoteCast(uint indexed questionId, uint indexed choiceIndex, address indexed voter);
    
    constructor() Ownable(msg.sender) {
        questionCounter = 0;
    }
    
    /**
     * @dev Crear una nueva pregunta (solo el owner)
     * @param _questionText El texto de la pregunta
     * @param _choices Array con las opciones de respuesta
     */
    function createQuestion(
        string memory _questionText, 
        string[] memory _choices
    ) public onlyOwner {
        require(_choices.length >= 2, "Debe haber al menos 2 opciones");
        require(_choices.length <= 10, "Maximo 10 opciones permitidas");
        
        uint questionId = questionCounter++;
        Question storage newQuestion = questions[questionId];
        newQuestion.questionText = _questionText;
        newQuestion.choices = _choices;
        newQuestion.isActive = true;
        newQuestion.totalVotes = 0;
        
        emit QuestionCreated(questionId, _questionText);
    }
    
    /**
     * @dev Votar en una pregunta
     * @param _questionId ID de la pregunta
     * @param _choiceIndex Índice de la opción elegida
     */
    function vote(uint _questionId, uint _choiceIndex) public nonReentrant {
        require(_questionId < questionCounter, "Pregunta no existe");
        require(questions[_questionId].isActive, "Pregunta no activa");
        require(_choiceIndex < questions[_questionId].choices.length, "Opcion invalida");
        require(!hasVoted[msg.sender][_questionId], "Ya votaste en esta pregunta");
        
        // Registrar el voto
        questions[_questionId].votes[_choiceIndex]++;
        questions[_questionId].totalVotes++;
        hasVoted[msg.sender][_questionId] = true;
        
        emit VoteCast(_questionId, _choiceIndex, msg.sender);
    }
    
    /**
     * @dev Obtener información de una pregunta
     */
    function getQuestion(uint _questionId) public view returns (
        string memory questionText,
        string[] memory choices,
        bool isActive,
        uint totalVotes
    ) {
        require(_questionId < questionCounter, "Pregunta no existe");
        Question storage q = questions[_questionId];
        return (q.questionText, q.choices, q.isActive, q.totalVotes);
    }
    
    /**
     * @dev Obtener votos de una opción específica
     */
    function getVotes(uint _questionId, uint _choiceIndex) public view returns (uint) {
        require(_questionId < questionCounter, "Pregunta no existe");
        require(_choiceIndex < questions[_questionId].choices.length, "Opcion invalida");
        return questions[_questionId].votes[_choiceIndex];
    }
    
    /**
     * @dev Activar/desactivar una pregunta (solo owner)
     */
    function setQuestionActive(uint _questionId, bool _isActive) public onlyOwner {
        require(_questionId < questionCounter, "Pregunta no existe");
        questions[_questionId].isActive = _isActive;
    }
    
    /**
     * @dev Verificar si una dirección ya votó en una pregunta
     */
    function hasUserVoted(address _user, uint _questionId) public view returns (bool) {
        return hasVoted[_user][_questionId];
    }
}