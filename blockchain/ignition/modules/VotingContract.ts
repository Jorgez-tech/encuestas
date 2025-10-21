import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("VotingContractModule", (m) => {
  // Deploy the VotingContract
  const votingContract = m.contract("VotingContract");

  return { votingContract };
});