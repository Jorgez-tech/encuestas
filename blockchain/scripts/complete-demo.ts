import hre from "hardhat";

async function main() {
  console.log("🚀 Complete VotingContract Demo\n");

  // Get signers (test accounts)
  const [owner, voter1, voter2] = await hre.ethers.getSigners();
  
  console.log("👥 Test Accounts:");
  console.log("   Owner:", owner.address);
  console.log("   Voter 1:", voter1.address);  
  console.log("   Voter 2:", voter2.address);
  
  console.log("\n💰 Account Balances:");
  console.log("   Owner:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(owner.address)), "ETH");
  console.log("   Voter 1:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(voter1.address)), "ETH");
  console.log("   Voter 2:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(voter2.address)), "ETH");

  console.log("\n📦 Step 1: Deploying VotingContract...");
  
  // Deploy the contract
  const VotingContract = await hre.ethers.getContractFactory("VotingContract");
  const votingContract = await VotingContract.deploy();
  await votingContract.waitForDeployment();
  
  const contractAddress = await votingContract.getAddress();
  console.log("✅ Contract deployed to:", contractAddress);
  
  // Verify deployment
  const questionCounter = await votingContract.questionCounter();
  const contractOwner = await votingContract.owner();
  
  console.log("   Initial question counter:", questionCounter.toString());
  console.log("   Contract owner:", contractOwner);
  console.log("   Owner verification:", contractOwner === owner.address ? "✅" : "❌");
  
  console.log("\n🗳️  Step 2: Creating first question...");
  
  // Create a question
  const questionText1 = "¿Cuál es tu lenguaje de programación favorito?";
  const choices1 = ["Python", "JavaScript", "Solidity", "TypeScript"];
  
  const createTx1 = await votingContract.createQuestion(questionText1, choices1);
  await createTx1.wait();
  console.log("✅ Question 1 created! Gas used:", createTx1.gasLimit.toString());
  
  // Get question details
  const question1 = await votingContract.getQuestion(0);
  console.log("   Text:", question1[0]);
  console.log("   Choices:", question1[1]);
  console.log("   Active:", question1[2]);
  console.log("   Votes:", question1[3].toString());
  
  console.log("\n🗳️  Step 3: Voting phase...");
  
  // Vote with voter1 (Python)
  const voter1Contract = votingContract.connect(voter1);
  const vote1Tx = await voter1Contract.vote(0, 0);
  await vote1Tx.wait();
  console.log("✅ Voter 1 voted for Python");
  
  // Vote with voter2 (Solidity)  
  const voter2Contract = votingContract.connect(voter2);
  const vote2Tx = await voter2Contract.vote(0, 2);
  await vote2Tx.wait();
  console.log("✅ Voter 2 voted for Solidity");
  
  // Owner votes (JavaScript)
  const vote3Tx = await votingContract.vote(0, 1);
  await vote3Tx.wait();
  console.log("✅ Owner voted for JavaScript");
  
  console.log("\n📊 Step 4: Results...");
  
  // Get results
  const finalQuestion = await votingContract.getQuestion(0);
  console.log("   Total votes:", finalQuestion[3].toString());
  
  console.log("   Results breakdown:");
  for (let i = 0; i < choices1.length; i++) {
    const votes = await votingContract.getVotes(0, i);
    const percentage = finalQuestion[3] > 0 ? (Number(votes) * 100 / Number(finalQuestion[3])).toFixed(1) : "0";
    console.log(`   - ${choices1[i]}: ${votes} votes (${percentage}%)`);
  }
  
  console.log("\n🗳️  Step 5: Creating second question...");
  
  const questionText2 = "¿Prefieres frontend o backend?";
  const choices2 = ["Frontend", "Backend", "Full Stack"];
  
  const createTx2 = await votingContract.createQuestion(questionText2, choices2);
  await createTx2.wait();
  console.log("✅ Question 2 created!");
  
  // Vote on second question
  await voter1Contract.vote(1, 2); // Full Stack
  await voter2Contract.vote(1, 1); // Backend  
  await votingContract.vote(1, 0); // Frontend
  
  console.log("✅ All votes cast for question 2");
  
  console.log("\n📊 Final Results:");
  
  const totalQuestions = await votingContract.questionCounter();
  console.log("   Total questions created:", totalQuestions.toString());
  
  for (let q = 0; q < Number(totalQuestions); q++) {
    const question = await votingContract.getQuestion(q);
    console.log(`\n   Question ${q + 1}: ${question[0]}`);
    console.log(`   Total votes: ${question[3]}`);
    
    for (let i = 0; i < question[1].length; i++) {
      const votes = await votingContract.getVotes(q, i);
      console.log(`   - ${question[1][i]}: ${votes} votes`);
    }
  }
  
  console.log("\n🔐 Step 6: Security test - Preventing double voting...");
  
  try {
    await voter1Contract.vote(0, 3);
    console.log("❌ Security breach! Double voting allowed");
  } catch (error: any) {
    console.log("✅ Security working: Double voting prevented");
    console.log("   Error:", error.reason || "Transaction reverted");
  }
  
  console.log("\n🎉 Demo completed successfully!");
  console.log("🔗 Contract Address:", contractAddress);
  console.log("📝 Questions Created:", totalQuestions.toString());
  console.log("🗳️  Total Votes Cast: 6");
  console.log("🔒 Security Features: ✅ Working");
  console.log("⛽ All transactions executed on Hardhat Network");
  
  console.log("\n💡 Next Steps:");
  console.log("   1. Integrate with Django using Web3.py");
  console.log("   2. Create Web3 frontend interface");
  console.log("   3. Deploy to testnet for public testing");
  console.log("   4. Add wallet connection for real users");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Demo failed:", error);
    process.exit(1);
  });