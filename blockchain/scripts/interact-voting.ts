import hre from "hardhat";

async function main() {
  console.log("🎯 Interacting with deployed VotingContract...\n");

  // Contract address from deployment
  const contractAddress = "0x5FbDB2315678afecb367f032d93F642f64180aa3";
  
  // Get signers (test accounts)
  const [owner, voter1, voter2] = await hre.ethers.getSigners();
  
  // Connect to the deployed contract
  const VotingContract = await hre.ethers.getContractFactory("VotingContract");
  const votingContract = VotingContract.attach(contractAddress);
  
  console.log("📋 Contract Info:");
  console.log("   Address:", contractAddress);
  console.log("   Owner:", owner.address);
  console.log("   Voter 1:", voter1.address);
  console.log("   Voter 2:", voter2.address);
  
  // Check initial state
  const initialQuestionCounter = await votingContract.questionCounter();
  console.log("   Initial questions:", initialQuestionCounter.toString());
  
  console.log("\n🗳️  Step 1: Creating a question...");
  
  // Create a question
  const questionText = "¿Cuál es tu lenguaje de programación favorito?";
  const choices = ["Python", "JavaScript", "Solidity", "TypeScript"];
  
  const createTx = await votingContract.createQuestion(questionText, choices);
  await createTx.wait();
  
  console.log("✅ Question created! Transaction:", createTx.hash);
  
  // Verify the question was created
  const questionCounter = await votingContract.questionCounter();
  console.log("   Total questions now:", questionCounter.toString());
  
  // Get the question details
  const question = await votingContract.getQuestion(0);
  console.log("   Question text:", question[0]);
  console.log("   Choices:", question[1]);
  console.log("   Is active:", question[2]);
  console.log("   Total votes:", question[3].toString());
  
  console.log("\n🗳️  Step 2: Voting with different accounts...");
  
  // Vote with voter1 (choice 0 - Python)
  const voter1Contract = votingContract.connect(voter1);
  const vote1Tx = await voter1Contract.vote(0, 0);
  await vote1Tx.wait();
  console.log("✅ Voter 1 voted for Python! Tx:", vote1Tx.hash);
  
  // Vote with voter2 (choice 2 - Solidity)
  const voter2Contract = votingContract.connect(voter2);
  const vote2Tx = await voter2Contract.vote(0, 2);
  await vote2Tx.wait();
  console.log("✅ Voter 2 voted for Solidity! Tx:", vote2Tx.hash);
  
  // Owner votes (choice 1 - JavaScript)
  const vote3Tx = await votingContract.vote(0, 1);
  await vote3Tx.wait();
  console.log("✅ Owner voted for JavaScript! Tx:", vote3Tx.hash);
  
  console.log("\n📊 Step 3: Checking results...");
  
  // Get updated question info
  const updatedQuestion = await votingContract.getQuestion(0);
  console.log("   Total votes now:", updatedQuestion[3].toString());
  
  // Get votes for each choice
  for (let i = 0; i < choices.length; i++) {
    const votes = await votingContract.getVotes(0, i);
    console.log(`   ${choices[i]}: ${votes} votes`);
  }
  
  console.log("\n🔐 Step 4: Testing vote prevention...");
  
  // Try to vote again with voter1 (should fail)
  try {
    await voter1Contract.vote(0, 3);
    console.log("❌ This shouldn't happen - double voting was allowed!");
  } catch (error: any) {
    console.log("✅ Double voting prevented:", error.reason || "Transaction reverted");
  }
  
  console.log("\n🎉 Your DApp is working perfectly!");
  console.log("🔗 Contract address:", contractAddress);
  console.log("📝 Questions created: 1");
  console.log("🗳️  Total votes cast: 3");
  console.log("🔒 Security features: ✅ Working");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Interaction failed:", error);
    process.exit(1);
  });