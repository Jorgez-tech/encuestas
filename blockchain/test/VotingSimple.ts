import { expect } from "chai";
import hre from "hardhat";

describe("VotingContract - Simple Tests", function() {
  let votingContract: any;
  let owner: any;

  before(async function() {
    [owner] = await hre.ethers.getSigners();
    const VotingContract = await hre.ethers.getContractFactory("VotingContract");
    votingContract = await VotingContract.deploy();
    await votingContract.waitForDeployment();
  });

  it("Should deploy successfully", async function() {
    expect(await votingContract.getAddress()).to.properAddress;
  });

  it("Should have initial question counter as 0", async function() {
    expect(await votingContract.questionCounter()).to.equal(0);
  });

  it("Should create a question", async function() {
    const questionText = "¿Cuál es tu color favorito?";
    const choices = ["Rojo", "Azul", "Verde"];

    await votingContract.createQuestion(questionText, choices);
    
    expect(await votingContract.questionCounter()).to.equal(1);
    
    const question = await votingContract.getQuestion(0);
    expect(question[0]).to.equal(questionText); // questionText
    expect(question[2]).to.equal(true);        // isActive
    expect(question[3]).to.equal(0n);          // totalVotes
  });

  it("Should allow voting", async function() {
    // Vote on the question we created
    await votingContract.vote(0, 0); // question 0, choice 0 (Rojo)
    
    const votes = await votingContract.getVotes(0, 0);
    expect(votes).to.equal(1);
    
    const question = await votingContract.getQuestion(0);
    expect(question[3]).to.equal(1n); // totalVotes should be 1
  });

  it("Should prevent double voting", async function() {
    await expect(
      votingContract.vote(0, 1) // Try to vote again
    ).to.be.revertedWith("Ya votaste en esta pregunta");
  });
});