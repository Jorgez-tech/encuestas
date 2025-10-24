// Deploy script para VotingContract - Versión de aprendizaje
// 📚 EXPLICACIÓN: hre = Hardhat Runtime Environment (entorno de ejecución)
import hre from "hardhat";

async function main() {
    console.log("🚀 Desplegando VotingContract...\n");

    // 📚 EXPLICACIÓN: Obtener la cuenta que desplegará el contrato
    const [deployer] = await hre.ethers.getSigners();
    console.log("📝 Desplegando con cuenta:", deployer.address);
    
    // 📚 EXPLICACIÓN: Verificar balance de la cuenta
    const balance = await hre.ethers.provider.getBalance(deployer.address);
    console.log("💰 Balance de la cuenta:", hre.ethers.formatEther(balance), "ETH\n");

    // 📚 EXPLICACIÓN: Obtener la fábrica del contrato (Contract Factory)
    console.log("🔧 Obteniendo Contract Factory...");
    const VotingContract = await hre.ethers.getContractFactory("VotingContract");
    
    // 📚 EXPLICACIÓN: Desplegar el contrato a la blockchain
    console.log("🚀 Desplegando contrato...");
    const votingContract = await VotingContract.deploy();
    
    // 📚 EXPLICACIÓN: Esperar confirmación del despliegue
    console.log("⏳ Esperando confirmación...");
    await votingContract.waitForDeployment();
    
    // 📚 EXPLICACIÓN: Obtener la dirección del contrato desplegado
    const contractAddress = await votingContract.getAddress();
    
    console.log("\n✅ ¡Contrato desplegado exitosamente!");
    console.log("📍 Dirección del contrato:", contractAddress);
    
    // 📚 EXPLICACIÓN: Obtener información de la transacción
    const deployTx = votingContract.deploymentTransaction();
    console.log("🔗 Hash de transacción:", deployTx?.hash);
    console.log("⛽ Gas usado:", deployTx?.gasLimit?.toString());
    
    // 📚 EXPLICACIÓN: Verificar que el contrato funciona
    console.log("\n🔍 Verificando funcionalidad del contrato...");
    const questionCounter = await votingContract.questionCounter();
    const owner = await votingContract.owner();
    
    console.log("📊 Contador de preguntas inicial:", questionCounter.toString());
    console.log("👑 Propietario del contrato:", owner);
    console.log("✅ El deployer es el owner:", owner === deployer.address);
    
    // 📚 EXPLICACIÓN: Información importante para Django
    console.log("\n🎯 Información para Django:");
    console.log("   📋 Copia esta dirección:", contractAddress);
    console.log("   🔧 Red local Hardhat:", "http://localhost:8545");
    console.log("   🆔 Chain ID:", "31337");
    
    console.log("\n✨ ¡Listo para usar con Django!");
    return contractAddress;
}

// 📚 EXPLICACIÓN: Ejecutar la función y manejar errores
main()
    .then(() => {
        console.log("\n🎉 Despliegue completado exitosamente!");
        process.exit(0);
    })
    .catch((error) => {
        console.error("\n❌ Error durante el despliegue:", error);
        process.exit(1);
    });