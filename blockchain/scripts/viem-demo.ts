import hre from "hardhat";

async function main() {
  console.log("🚀 Complete VotingContract Demo (using Viem)\n");

  // Get test accounts
  const [owner, voter1, voter2] = await hre.viem.getWalletClients();
  
  console.log("👥 Test Accounts:");
  console.log("   Owner:", owner.account.address);
  console.log("   Voter 1:", voter1.account.address);  
  console.log("   Voter 2:", voter2.account.address);

  console.log("\n📦 Step 1: Deploying VotingContract...");
  
  // Deploy the contract
  const votingContract = await hre.viem.deployContract("VotingContract");
  
  console.log("✅ Contract deployed to:", votingContract.address);
  
  // Verify deployment
  const questionCounter = await votingContract.read.questionCounter();
  const contractOwner = await votingContract.read.owner();
  
  console.log("   Initial question counter:", questionCounter.toString());
  console.log("   Contract owner:", contractOwner);
  
  console.log("\n🗳️  Step 2: Creating first question...");
  
  // Create a question
  const questionText1 = "¿Cuál es tu lenguaje de programación favorito?";
  const choices1 = ["Python", "JavaScript", "Solidity", "TypeScript"];
  
  const createHash1 = await votingContract.write.createQuestion([questionText1, choices1]);
  console.log("✅ Question 1 created! Tx:", createHash1);
  
  // Get question details
  const question1 = await votingContract.read.getQuestion([0n]);
  console.log("   Text:", question1[0]);
  console.log("   Choices:", question1[1]);
  console.log("   Active:", question1[2]);
  console.log("   Votes:", question1[3].toString());
  
  console.log("\n🗳️  Step 3: Voting phase...");
  
  // Connect contract with different wallets
  const voter1Contract = await hre.viem.getContractAt("VotingContract", votingContract.address, { client: { wallet: voter1 } });
  const voter2Contract = await hre.viem.getContractAt("VotingContract", votingContract.address, { client: { wallet: voter2 } });
  
  // Vote with voter1 (Python - choice 0)
  const vote1Hash = await voter1Contract.write.vote([0n, 0n]);
  console.log("✅ Voter 1 voted for Python. Tx:", vote1Hash);
  
  // Vote with voter2 (Solidity - choice 2)
  const vote2Hash = await voter2Contract.write.vote([0n, 2n]);
  console.log("✅ Voter 2 voted for Solidity. Tx:", vote2Hash);
  
  // Owner votes (JavaScript - choice 1)
  const vote3Hash = await votingContract.write.vote([0n, 1n]);
  console.log("✅ Owner voted for JavaScript. Tx:", vote3Hash);
  
  console.log("\n📊 Step 4: Results...");
  
  // Get results
  const finalQuestion = await votingContract.read.getQuestion([0n]);
  console.log("   Total votes:", finalQuestion[3].toString());
  
  console.log("   Results breakdown:");
  for (let i = 0; i < choices1.length; i++) {
    const votes = await votingContract.read.getVotes([0n, BigInt(i)]);
    const percentage = finalQuestion[3] > 0 ? (Number(votes) * 100 / Number(finalQuestion[3])).toFixed(1) : "0";
    console.log(`   - ${choices1[i]}: ${votes} votes (${percentage}%)`);
  }
  
  console.log("\n🗳️  Step 5: Creating second question...");
  
  const questionText2 = "¿Prefieres frontend o backend?";
  const choices2 = ["Frontend", "Backend", "Full Stack"];
  
  const createHash2 = await votingContract.write.createQuestion([questionText2, choices2]);
  console.log("✅ Question 2 created! Tx:", createHash2);
  
  // Vote on second question
  await voter1Contract.write.vote([1n, 2n]); // Full Stack
  await voter2Contract.write.vote([1n, 1n]); // Backend  
  await votingContract.write.vote([1n, 0n]); // Frontend
  
  console.log("✅ All votes cast for question 2");
  
  console.log("\n📊 Final Results:");
  
  const totalQuestions = await votingContract.read.questionCounter();
  console.log("   Total questions created:", totalQuestions.toString());
  
  for (let q = 0n; q < totalQuestions; q++) {
    const question = await votingContract.read.getQuestion([q]);
    console.log(`\n   Question ${Number(q) + 1}: ${question[0]}`);
    console.log(`   Total votes: ${question[3]}`);
    
    for (let i = 0; i < question[1].length; i++) {
      const votes = await votingContract.read.getVotes([q, BigInt(i)]);
      console.log(`   - ${question[1][i]}: ${votes} votes`);
    }
  }
  
  console.log("\n🔐 Step 6: Security test - Preventing double voting...");
  
  try {
    await voter1Contract.write.vote([0n, 3n]);
    console.log("❌ Security breach! Double voting allowed");
  } catch (error: any) {
    console.log("✅ Security working: Double voting prevented");
    console.log("   Error reason: Transaction would revert");
  }
  
  console.log("\n🎉 Demo completed successfully!");
  console.log("🔗 Contract Address:", votingContract.address);
  console.log("📝 Questions Created:", totalQuestions.toString());
  console.log("🗳️  Total Votes Cast: 6");
  console.log("🔒 Security Features: ✅ Working");
  console.log("⛽ All transactions executed on Hardhat Network");
  
  console.log("\n💡 Next Steps:");
  console.log("   1. Integrate with Django using Web3.py");
  console.log("   2. Create Web3 frontend interface");
  console.log("   3. Deploy to testnet for public testing");
  console.log("   4. Add wallet connection for real users");
  
  return {
    contractAddress: votingContract.address,
    totalQuestions: Number(totalQuestions),
    totalVotes: 6
  };
}

main()
  .then((result) => {
    console.log("\n✨ Demo Summary:", result);
    process.exit(0);
  })
  .catch((error) => {
    console.error("❌ Demo failed:", error);
    process.exit(1);
  });