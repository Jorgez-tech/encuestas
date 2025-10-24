import hre from "hardhat";

async function main() {
  console.log("🚀 Desplegando VotingContract (versión de aprendizaje)...\n");

  // 📚 EXPLICACIÓN: Obtener cliente público (para leer blockchain)
  const publicClient = await hre.viem.getPublicClient();
  console.log("🔗 Conectado a red:", publicClient.chain.name);

  // 📚 EXPLICACIÓN: Obtener cliente wallet (para hacer transacciones)  
  const [deployer] = await hre.viem.getWalletClients();
  console.log("📝 Desplegando con cuenta:", deployer.account.address);

  // 📚 EXPLICACIÓN: Verificar balance de la cuenta
  const balance = await publicClient.getBalance({ 
    address: deployer.account.address 
  });
  console.log("💰 Balance:", hre.viem.formatEther(balance), "ETH\n");

  // 📚 EXPLICACIÓN: Desplegar el contrato
  console.log("🚀 Desplegando contrato...");
  const votingContract = await hre.viem.deployContract("VotingContract", []);
  
  console.log("✅ ¡Contrato desplegado exitosamente!");
  console.log("📍 Dirección:", votingContract.address);

  // 📚 EXPLICACIÓN: Probar funciones del contrato
  console.log("\n🔍 Probando funcionalidad...");
  const questionCounter = await votingContract.read.questionCounter();
  const owner = await votingContract.read.owner();
  
  console.log("📊 Contador inicial:", questionCounter.toString());
  console.log("👑 Propietario:", owner);
  console.log("✅ Deployer es owner:", owner === deployer.account.address);

  // 📚 INFORMACIÓN PARA DJANGO
  console.log("\n🎯 Información para Django:");
  console.log("   📋 Contract Address:", votingContract.address);
  console.log("   🔧 Network URL:", "http://localhost:8545");
  console.log("   🆔 Chain ID:", "31337");
  
  console.log("\n✨ ¡Listo para conectar Django!");
  
  return votingContract.address;
}

main()
  .then(() => {
    console.log("\n🎉 ¡Despliegue completado!");
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ Error:", error);
    process.exit(1);
  });