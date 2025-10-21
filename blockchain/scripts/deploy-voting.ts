import hre from "hardhat";

async function main() {
  console.log("🚀 Deploying VotingContract...\n");

  // Get the deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 Deploying with account:", deployer.address);
  console.log("💰 Account balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\n");

  // Deploy the contract
  const VotingContract = await hre.ethers.getContractFactory("VotingContract");
  const votingContract = await VotingContract.deploy();
  
  await votingContract.waitForDeployment();
  const contractAddress = await votingContract.getAddress();

  console.log("✅ VotingContract deployed to:", contractAddress);
  console.log("🔗 Transaction hash:", votingContract.deploymentTransaction()?.hash);
  console.log("⛽ Gas used:", votingContract.deploymentTransaction()?.gasLimit.toString());
  
  // Verify deployment
  const questionCounter = await votingContract.questionCounter();
  const owner = await votingContract.owner();
  
  console.log("\n📊 Contract verification:");
  console.log("   - Question counter:", questionCounter.toString());
  console.log("   - Contract owner:", owner);
  console.log("   - Deployer is owner:", owner === deployer.address);
  
  console.log("\n🎯 Next steps:");
  console.log("   1. Use the contract address:", contractAddress);
  console.log("   2. Run interaction script: npx hardhat run scripts/interact-voting.ts --network localhost");
  
  return contractAddress;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });