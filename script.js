document.addEventListener('DOMContentLoaded', () => {
    // 1. Seleciona o formulário e o elemento de resultado
    const form = document.getElementById('dataForm');
    const resultadoPre = document.getElementById('resultado');

    // 2. Adiciona um "ouvinte" para quando o formulário for enviado
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o envio padrão do formulário (que recarregaria a página)

        // 3. Coleta os dados do formulário
        const valorInput = document.getElementById('valor');
        const dadosParaPython = {
            valor: parseInt(valorInput.value, 10) // Converte o valor para número inteiro
            // Se você tivesse mais campos, adicionaria-os aqui
        };

        resultadoPre.textContent = 'Processando...'; // Mostra que está trabalhando

        try {
            // 4. Envia os dados para a rota API que você criou no Flask (app.py)
            const response = await fetch('/api/processar', {
                method: 'POST', // Usa o método POST, como configurado no app.py
                headers: {
                    'Content-Type': 'application/json' // Diz ao servidor que estamos enviando JSON
                },
                body: JSON.stringify(dadosParaPython) // Converte o objeto JS para uma string JSON
            });

            // 5. Verifica se a resposta foi bem-sucedida
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            // 6. Recebe e exibe a resposta do Flask
            const resultadoJson = await response.json();
            
            // Exibe o JSON formatado na tela
            resultadoPre.textContent = JSON.stringify(resultadoJson, null, 2);

        } catch (error) {
            console.error('Erro ao comunicar com a API:', error);
            resultadoPre.textContent = `ERRO: Não foi possível processar os dados. ${error.message}`;
        }
    });
});