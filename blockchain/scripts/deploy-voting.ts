import hre from "hardhat";

async function main() {
  console.log("🚀 Desplegando VotingContract (¡Aprendamos juntos!)...\n");

  // 📚 PASO 1: Obtener la cuenta que desplegará el contrato
  console.log("📝 PASO 1: Obteniendo cuenta de despliegue...");
  const [deployer] = await hre.ethers.getSigners();
  console.log("✅ Cuenta encontrada:", deployer.address);
  
  // 📚 PASO 2: Verificar que tenemos suficiente ETH
  console.log("💰 PASO 2: Verificando balance...");
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("✅ Balance disponible:", hre.ethers.formatEther(balance), "ETH\n");

  // 📚 PASO 3: Preparar el contrato para despliegue
  console.log("🔧 PASO 3: Preparando contrato VotingContract...");
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