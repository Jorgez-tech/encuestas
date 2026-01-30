document.addEventListener('DOMContentLoaded', async () => {
    const statusDiv = document.getElementById('wallet-status');
    const voteButton = document.getElementById('vote-button');
    let provider;
    let signer;
    let contract;

    // Check if ethers is loaded
    if (typeof ethers === 'undefined') {
        statusDiv.textContent = "Error: Librería Ethers.js no cargada.";
        statusDiv.className = 'status-message status-error';
        return;
    }

    if (window.ethereum) {
        try {
            // Ethers v6 syntax
            provider = new ethers.BrowserProvider(window.ethereum);

            // Request account access
            await provider.send("eth_requestAccounts", []);

            signer = await provider.getSigner();
            const address = await signer.getAddress();

            statusDiv.textContent = `Wallet conectada: ${address.substring(0,6)}...${address.substring(38)}`;
            statusDiv.className = 'status-message status-success';

            // Check if already voted
            contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, signer);

            try {
                const hasVoted = await contract.hasUserVoted(address, QUESTION_ID);

                if (hasVoted) {
                    voteButton.textContent = "Ya has votado";
                    voteButton.disabled = true;
                    statusDiv.textContent += " (Voto registrado)";
                } else {
                    voteButton.disabled = false;
                }
            } catch (err) {
                console.error("Error checking vote status:", err);
                // Might fail if contract not deployed on current network
                statusDiv.textContent += " (Nota: Asegúrate de estar en la red correcta)";
                voteButton.disabled = false;
            }

        } catch (error) {
            console.error(error);
            statusDiv.textContent = `Error conectando wallet: ${error.message}`;
            statusDiv.className = 'status-message status-error';
        }
    } else {
        statusDiv.textContent = "MetaMask no detectado. Por favor instala una wallet Web3.";
        statusDiv.className = 'status-message status-error';
    }

    voteButton.addEventListener('click', async () => {
        const selected = document.querySelector('input[name="choice"]:checked');
        if (!selected) {
            alert("Por favor selecciona una opción");
            return;
        }

        const choiceIndex = selected.value;
        voteButton.disabled = true;
        voteButton.textContent = "Confirmando...";

        try {
            const tx = await contract.vote(QUESTION_ID, choiceIndex);
            statusDiv.textContent = "Transacción enviada. Esperando confirmación...";
            statusDiv.className = 'status-message status-info';

            await tx.wait();

            statusDiv.textContent = "¡Voto confirmado exitosamente!";
            statusDiv.className = 'status-message status-success';
            voteButton.textContent = "Voto Enviado";

            // Redirect to results after delay
            setTimeout(() => {
                // Construct results URL
                // Assumes current url is .../web3/<id>/
                const currentUrl = window.location.href;
                const resultsUrl = currentUrl.endsWith('/') ? currentUrl + 'results/' : currentUrl + '/results/';
                window.location.href = resultsUrl;
            }, 2000);

        } catch (error) {
            console.error(error);
            let errorMessage = error.reason || error.message;
            if (error.code === 'ACTION_REJECTED') {
                errorMessage = "Usuario rechazó la transacción";
            }
            statusDiv.textContent = `Error al votar: ${errorMessage}`;
            statusDiv.className = 'status-message status-error';
            voteButton.disabled = false;
            voteButton.textContent = "Votar en Blockchain";
        }
    });
});
