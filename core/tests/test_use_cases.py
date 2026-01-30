"""
Tests unitarios para Use Cases de Clean Architecture

Estos tests validan la lógica de negocio pura sin dependencias de Django.
Utilizan implementaciones in-memory de los repositorios.
"""

from django.test import TestCase
from datetime import datetime
from core.domain.entities import Question, Choice, Vote
from core.use_cases.sync import SyncVotesUseCase
from core.use_cases.voting import GetQuestionResultsUseCase
from polls.adapters.blockchain import MockBlockchainGateway


class InMemoryQuestionRepository:
    """Repositorio de preguntas en memoria para testing"""
    
    def __init__(self):
        self.questions = {}
        self._next_id = 1
    
    def get_by_id(self, question_id: int):
        return self.questions.get(question_id)
    
    def get_by_blockchain_id(self, blockchain_id: int):
        for q in self.questions.values():
            if q.blockchain_id == blockchain_id:
                return q
        return None
    
    def save(self, question):
        if question.id is None:
            question.id = self._next_id
            self._next_id += 1
        self.questions[question.id] = question
        return question
    
    def get_pending_sync(self):
        return [q for q in self.questions.values() if not q.is_synced]


class InMemoryVoteRepository:
    """Repositorio de votos en memoria para testing"""
    
    def __init__(self):
        self.votes = []
    
    def exists(self, tx_hash: str, log_index: int):
        return any(
            v.transaction_hash == tx_hash and v.log_index == log_index 
            for v in self.votes
        )
    
    def save(self, vote):
        self.votes.append(vote)
        return vote
    
    def get_votes_for_question(self, question_id: int):
        return [v for v in self.votes if v.question_id == question_id]


class TestSyncVotesUseCase(TestCase):
    """Tests para el caso de uso de sincronización de votos"""
    
    def test_sync_votes_basic(self):
        """Test sincronización básica de votos desde blockchain"""
        # Arrange
        mock_gateway = MockBlockchainGateway()
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        # Crear pregunta
        question = Question(
            id=1,
            text="¿Cuál es tu color favorito?",
            pub_date=datetime.now(),
            choices=[
                Choice(id=1, text="Rojo"),
                Choice(id=2, text="Azul"),
            ],
            blockchain_id=10,
            is_synced=True
        )
        question_repo.save(question)
        
        # Agregar evento mock de votación
        mock_gateway.add_mock_vote_event(
            question_id=10,
            choice_index=0,
            voter="0xabc123def456"
        )
        
        use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
        
        # Act
        count = use_case.execute(from_block=0)
        
        # Assert
        assert count == 1, "Debe sincronizar 1 voto"
        assert len(vote_repo.votes) == 1, "Debe haber 1 voto en el repositorio"
        assert vote_repo.votes[0].voter_address == "0xabc123def456"
        assert vote_repo.votes[0].choice_index == 0
    
    def test_sync_votes_idempotency(self):
        """Test que la sincronización no duplica votos (idempotencia)"""
        # Arrange
        mock_gateway = MockBlockchainGateway()
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        question = Question(
            id=1, text="Test Question", pub_date=datetime.now(),
            blockchain_id=10, is_synced=True
        )
        question_repo.save(question)
        
        # Agregar el mismo evento con tx_hash específico
        mock_gateway.add_mock_vote_event(10, 0, "0xabc", tx_hash="0x123abc")
        
        use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
        
        # Act - ejecutar sincronización dos veces
        count1 = use_case.execute(from_block=0)
        count2 = use_case.execute(from_block=0)
        
        # Assert
        assert count1 == 1, "Primera sincronización debe encontrar 1 voto"
        assert count2 == 0, "Segunda sincronización no debe duplicar"
        assert len(vote_repo.votes) == 1, "Solo debe haber 1 voto"
    
    def test_sync_votes_missing_question(self):
        """Test que maneja correctamente preguntas no encontradas"""
        # Arrange
        mock_gateway = MockBlockchainGateway()
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        # NO agregar pregunta, solo agregar evento
        mock_gateway.add_mock_vote_event(999, 0, "0xabc")
        
        use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
        
        # Act
        count = use_case.execute(from_block=0)
        
        # Assert
        assert count == 0, "No debe crear votos sin pregunta asociada"
        assert len(vote_repo.votes) == 0, "No debe haber votos"
    
    def test_sync_votes_multiple_events(self):
        """Test sincronización de múltiples eventos"""
        # Arrange
        mock_gateway = MockBlockchainGateway()
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        question = Question(
            id=1, text="Test", pub_date=datetime.now(),
            blockchain_id=10, is_synced=True
        )
        question_repo.save(question)
        
        # Agregar 3 votos diferentes
        mock_gateway.add_mock_vote_event(10, 0, "0xaaa")
        mock_gateway.add_mock_vote_event(10, 1, "0xbbb")
        mock_gateway.add_mock_vote_event(10, 0, "0xccc")
        
        use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
        
        # Act
        count = use_case.execute(from_block=0)
        
        # Assert
        assert count == 3, "Debe sincronizar 3 votos"
        assert len(vote_repo.votes) == 3, "Debe haber 3 votos"
    
    def test_sync_votes_from_specific_block(self):
        """Test sincronización desde un bloque específico"""
        # Arrange
        mock_gateway = MockBlockchainGateway()
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        question = Question(
            id=1, text="Test", pub_date=datetime.now(),
            blockchain_id=10, is_synced=True
        )
        question_repo.save(question)
        
        # Agregar votos en diferentes bloques
        mock_gateway.add_mock_vote_event(10, 0, "0xaaa")  # bloque 1
        mock_gateway.add_mock_vote_event(10, 1, "0xbbb")  # bloque 2
        mock_gateway.add_mock_vote_event(10, 0, "0xccc")  # bloque 3
        
        use_case = SyncVotesUseCase(vote_repo, question_repo, mock_gateway)
        
        # Act - sincronizar solo desde bloque 2
        count = use_case.execute(from_block=2)
        
        # Assert
        assert count == 2, "Debe sincronizar solo votos desde bloque 2"


class TestGetQuestionResultsUseCase(TestCase):
    """Tests para el caso de uso de obtención de resultados"""
    
    def test_get_results_no_votes(self):
        """Test obtener resultados sin votos"""
        # Arrange
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        question = Question(
            id=1,
            text="¿Test?",
            pub_date=datetime.now(),
            choices=[
                Choice(id=1, text="Opción A"),
                Choice(id=2, text="Opción B"),
            ],
            blockchain_id=10,
            is_synced=True
        )
        question_repo.save(question)
        
        use_case = GetQuestionResultsUseCase(question_repo, vote_repo)
        
        # Act
        results = use_case.execute(1)
        
        # Assert
        assert results['total_votes'] == 0
        assert len(results['choices']) == 2
        assert results['choices'][0]['votes'] == 0
        assert results['choices'][1]['votes'] == 0
    
    def test_get_results_with_votes(self):
        """Test obtener resultados con votos"""
        # Arrange
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        
        question = Question(
            id=1,
            text="¿Test?",
            pub_date=datetime.now(),
            choices=[
                Choice(id=1, text="A"),
                Choice(id=2, text="B"),
            ],
            blockchain_id=10,
            is_synced=True
        )
        question_repo.save(question)
        
        # Agregar votos: 3 para opción 0, 1 para opción 1
        for i in range(3):
            vote_repo.save(Vote(
                question_id=1, choice_index=0, voter_address=f"0x{i}",
                transaction_hash=f"0x{i}", block_number=1, log_index=i
            ))
        vote_repo.save(Vote(
            question_id=1, choice_index=1, voter_address="0x999",
            transaction_hash="0x999", block_number=1, log_index=999
        ))
        
        use_case = GetQuestionResultsUseCase(question_repo, vote_repo)
        
        # Act
        results = use_case.execute(1)
        
        # Assert
        assert results['total_votes'] == 4
        assert results['choices'][0]['votes'] == 3
        assert results['choices'][0]['percentage'] == 75.0
        assert results['choices'][1]['votes'] == 1
        assert results['choices'][1]['percentage'] == 25.0
    
    def test_get_results_question_not_found(self):
        """Test error cuando la pregunta no existe"""
        # Arrange
        question_repo = InMemoryQuestionRepository()
        vote_repo = InMemoryVoteRepository()
        use_case = GetQuestionResultsUseCase(question_repo, vote_repo)
        
        # Act & Assert
        with self.assertRaisesRegex(ValueError, "not found"):
            use_case.execute(999)


class TestMockBlockchainGateway(TestCase):
    """Tests para el gateway mock de blockchain"""
    
    def test_create_question(self):
        """Test creación de pregunta mock"""
        # Arrange
        gateway = MockBlockchainGateway()
        
        # Act
        result = gateway.create_question("Test?", ["A", "B", "C"])
        
        # Assert
        assert result['success'] is True
        assert 'question_id' in result
        assert 'transaction_hash' in result
        assert result['transaction_hash'].startswith('0x')
    
    def test_fetch_vote_events_empty(self):
        """Test obtener eventos cuando no hay votos"""
        # Arrange
        gateway = MockBlockchainGateway()
        
        # Act
        events = gateway.fetch_vote_events(from_block=0)
        
        # Assert
        assert events == []
    
    def test_add_and_fetch_vote_events(self):
        """Test agregar y obtener eventos de voto"""
        # Arrange
        gateway = MockBlockchainGateway()
        gateway.add_mock_vote_event(1, 0, "0xabc")
        gateway.add_mock_vote_event(1, 1, "0xdef")
        
        # Act
        events = gateway.fetch_vote_events(from_block=0)
        
        # Assert
        assert len(events) == 2
        assert events[0]['question_id'] == 1
        assert events[0]['voter'] == "0xabc"
    
    def test_reset_clears_state(self):
        """Test que reset limpia el estado del gateway"""
        # Arrange
        gateway = MockBlockchainGateway()
        gateway.add_mock_vote_event(1, 0, "0xabc")
        gateway.create_question("Test", ["A", "B"])
        
        # Act
        gateway.reset()
        
        # Assert
        events = gateway.fetch_vote_events(from_block=0)
        assert events == []
        assert gateway.get_current_block_number() == 0
