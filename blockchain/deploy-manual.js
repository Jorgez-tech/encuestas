// Script manual de deploy - Método de aprendizaje
// Este script lo ejecutaremos paso a paso para entender el proceso

console.log("🎓 TUTORIAL DE DESPLIEGUE - ¡Aprendamos blockchain!");
console.log("================================================\n");

console.log("📚 PASO 1: Red Hardhat activa");
console.log("   ✅ La red local está corriendo en puerto 8545");
console.log("   ✅ Tenemos 20 cuentas con 10,000 ETH cada una\n");

console.log("📚 PASO 2: Contrato compilado");
console.log("   ✅ VotingContract.sol está listo");
console.log("   ✅ Hardhat ya compiló el contrato\n");

console.log("📚 PASO 3: Lo que vamos a hacer ahora:");
console.log("   1. Usar Hardhat console para desplegar manualmente");
console.log("   2. Copiar la dirección del contrato");
console.log("   3. Configurar Django para usar esa dirección\n");

console.log("🚀 COMANDO PARA EJECUTAR:");
console.log("   npx hardhat console --network localhost\n");

console.log("📝 LUEGO EN LA CONSOLA, EJECUTAR:");
console.log("   const VotingContract = await ethers.getContractFactory('VotingContract')");
console.log("   const contract = await VotingContract.deploy()");
console.log("   await contract.deployed()");
console.log("   console.log('Contract address:', contract.address)");
console.log("   console.log('Deployer:', await ethers.getSigners()[0].address)\n");

console.log("💡 ¿Listo para probar? ¡Vamos paso a paso!");