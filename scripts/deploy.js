const hre = require("hardhat");

async function main() {
  console.log("Deploying LogRegistry contract...");

  const LogRegistry = await hre.ethers.getContractFactory("LogRegistry");
  const logRegistry = await LogRegistry.deploy();

  await logRegistry.waitForDeployment();

  const address = await logRegistry.getAddress();
  console.log("LogRegistry deployed to:", address);
  
  // Simpan address ke file
  const fs = require("fs");
  fs.writeFileSync("./config/contract-address.txt", address);
  console.log("Contract address saved to config/contract-address.txt");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
