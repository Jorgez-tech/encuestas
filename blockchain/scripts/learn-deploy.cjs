const hre = require("hardhat");

async function main() {
    console.log("🎓 DESPLIEGUE EDUCATIVO - Paso a Paso\n");
    
    // 📚 EXPLICACIÓN: Conexión a la red
    console.log("🔗 PASO 1: Conectando a la red local...");
    console.log("   URL:", "http://127.0.0.1:8545");
    console.log("   Chain ID:", 31337);
    
    // 📚 EXPLICACIÓN: Obtener signers (cuentas)
    console.log("\n👤 PASO 2: Obteniendo cuentas disponibles...");
    const signers = await hre.ethers.getSigners();
    console.log("   Cuentas encontradas:", signers.length);
    console.log("   Deployer (Cuenta #0):", signers[0].address);
    
    // 📚 EXPLICACIÓN: Verificar balance
    console.log("\n💰 PASO 3: Verificando balance del deployer...");
    const balance = await hre.ethers.provider.getBalance(signers[0].address);
    console.log("   Balance:", hre.ethers.formatEther(balance), "ETH");
    
    // 📚 EXPLICACIÓN: Preparar contrato
    console.log("\n📄 PASO 4: Preparando contrato VotingContract...");
    const VotingContractFactory = await hre.ethers.getContractFactory("VotingContract");
    console.log("   ✅ Contract Factory obtenido");
    
    // 📚 EXPLICACIÓN: Desplegar
    console.log("\n🚀 PASO 5: Desplegando contrato...");
    console.log("   ⏳ Enviando transacción de deploy...");
    
    const votingContract = await VotingContractFactory.deploy();
    console.log("   ⏳ Esperando confirmación...");
    
    await votingContract.waitForDeployment();
    const contractAddress = await votingContract.getAddress();
    
    console.log("   ✅ ¡Contrato desplegado exitosamente!");
    console.log("   📍 Dirección del contrato:", contractAddress);
    
    // 📚 EXPLICACIÓN: Probar el contrato
    console.log("\n🧪 PASO 6: Probando funciones del contrato...");
    const questionCounter = await votingContract.questionCounter();
    const owner = await votingContract.owner();
    
    console.log("   📊 Contador inicial de preguntas:", questionCounter.toString());
    console.log("   👑 Propietario del contrato:", owner);
    console.log("   ✅ El deployer es el propietario:", owner === signers[0].address);
    
    // 📚 INFORMACIÓN PARA DJANGO
    console.log("\n🎯 INFORMACIÓN PARA CONECTAR DJANGO:");
    console.log("   ==========================================");
    console.log("   📋 CONTRACT_ADDRESS:", contractAddress);
    console.log("   🌐 WEB3_PROVIDER_URL: http://localhost:8545");
    console.log("   🆔 CHAIN_ID: 31337");
    console.log("   👤 DEPLOYER_ADDRESS:", signers[0].address);
    console.log("   ==========================================");
    
    console.log("\n✨ ¡LISTO! Ahora puedes usar Django con blockchain real!");
    
    return contractAddress;
}

main()
    .then(() => {
        console.log("\n🎉 Tutorial completado exitosamente!");
        process.exit(0);
    })
    .catch((error) => {
        console.error("\n❌ Error en el tutorial:", error);
        process.exit(1);
    });