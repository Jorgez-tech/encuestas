import { expect } from "chai";
import hre from "hardhat";

describe("VotingContract", function() {
  let votingContract: any;
  let owner: any;
  let voter1: any;
  let voter2: any;

  beforeEach(async function() {
    // Get signers (test accounts)
    [owner, voter1, voter2] = await hre.ethers.getSigners();
    
    // Deploy contract
    const VotingContract = await hre.ethers.getContractFactory("VotingContract");
    votingContract = await VotingContract.deploy();
    await votingContract.waitForDeployment();
  });

  describe("Question Creation", function() {
    it("Should allow owner to create a question", async function() {
      const questionText = "¿Cuál es tu color favorito?";
      const choices = ["Rojo", "Azul", "Verde"];

      await votingContract.write.createQuestion([questionText, choices]);
      
      const question = await votingContract.read.getQuestion([0n]);
      expect(question[0]).to.equal(questionText);
      expect(question[1]).to.deep.equal(choices);
      expect(question[2]).to.equal(true); // isActive
      expect(question[3]).to.equal(0n); // totalVotes
    });

    it("Should reject questions with less than 2 choices", async function() {
      const questionText = "Pregunta inválida";
      const choices = ["Solo una opción"];

      await expect(
        votingContract.write.createQuestion([questionText, choices])
      ).to.be.revertedWith("Debe haber al menos 2 opciones");
    });

    it("Should reject non-owner creating questions", async function() {
      const questionText = "Pregunta no autorizada";
      const choices = ["Opción 1", "Opción 2"];

      const nonOwnerContract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter1 } }
      );

      await expect(
        nonOwnerContract.write.createQuestion([questionText, choices])
      ).to.be.rejected;
    });
  });

  describe("Voting", function() {
    beforeEach(async function() {
      // Create a test question
      const questionText = "¿Prefieres café o té?";
      const choices = ["Café", "Té"];
      await votingContract.write.createQuestion([questionText, choices]);
    });

    it("Should allow voting on active question", async function() {
      const voter1Contract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter1 } }
      );

      await voter1Contract.write.vote([0n, 0n]); // Vote for choice 0

      const votes = await votingContract.read.getVotes([0n, 0n]);
      expect(votes).to.equal(1n);
      
      const question = await votingContract.read.getQuestion([0n]);
      expect(question[3]).to.equal(1n); // totalVotes
    });

    it("Should prevent double voting", async function() {
      const voter1Contract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter1 } }
      );

      await voter1Contract.write.vote([0n, 0n]); // First vote

      await expect(
        voter1Contract.write.vote([0n, 1n]) // Try to vote again
      ).to.be.revertedWith("Ya votaste en esta pregunta");
    });

    it("Should allow multiple users to vote", async function() {
      const voter1Contract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter1 } }
      );

      const voter2Contract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter2 } }
      );

      await voter1Contract.write.vote([0n, 0n]); // Voter1 votes choice 0
      await voter2Contract.write.vote([0n, 1n]); // Voter2 votes choice 1

      const votes0 = await votingContract.read.getVotes([0n, 0n]);
      const votes1 = await votingContract.read.getVotes([0n, 1n]);
      
      expect(votes0).to.equal(1n);
      expect(votes1).to.equal(1n);
      
      const question = await votingContract.read.getQuestion([0n]);
      expect(question[3]).to.equal(2n); // totalVotes
    });

    it("Should reject voting on inactive question", async function() {
      // Deactivate question
      await votingContract.write.setQuestionActive([0n, false]);

      const voter1Contract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter1 } }
      );

      await expect(
        voter1Contract.write.vote([0n, 0n])
      ).to.be.revertedWith("Pregunta no activa");
    });
  });

  describe("Question Management", function() {
    it("Should allow owner to activate/deactivate questions", async function() {
      const questionText = "Pregunta de prueba";
      const choices = ["Sí", "No"];
      await votingContract.write.createQuestion([questionText, choices]);

      // Initially active
      let question = await votingContract.read.getQuestion([0n]);
      expect(question[2]).to.equal(true);

      // Deactivate
      await votingContract.write.setQuestionActive([0n, false]);
      question = await votingContract.read.getQuestion([0n]);
      expect(question[2]).to.equal(false);

      // Reactivate
      await votingContract.write.setQuestionActive([0n, true]);
      question = await votingContract.read.getQuestion([0n]);
      expect(question[2]).to.equal(true);
    });
  });

  describe("Helper Functions", function() {
    it("Should correctly track voting status", async function() {
      const questionText = "Pregunta de prueba";
      const choices = ["A", "B"];
      await votingContract.write.createQuestion([questionText, choices]);

      const voter1Address = voter1.account.address;
      
      // Initially not voted
      let hasVoted = await votingContract.read.hasUserVoted([voter1Address, 0n]);
      expect(hasVoted).to.equal(false);

      // Vote
      const voter1Contract = await viem.getContractAt(
        "VotingContract", 
        votingContract.address,
        { client: { wallet: voter1 } }
      );
      await voter1Contract.write.vote([0n, 0n]);

      // Now has voted
      hasVoted = await votingContract.read.hasUserVoted([voter1Address, 0n]);
      expect(hasVoted).to.equal(true);
    });
  });
});