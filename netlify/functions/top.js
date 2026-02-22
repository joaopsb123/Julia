exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 204, headers, body: '' };
    }

    try {
        const { Blobs } = require('@netlify/blobs');
        const userStore = Blobs.store('users');
        
        // Listar todas as chaves (IDs dos usuários)
        const { blobs } = await userStore.list();
        
        if (!blobs || blobs.length === 0) {
            return { statusCode: 200, headers, body: JSON.stringify([]) };
        }

        // Buscar dados de cada usuário
        const usersList = [];
        
        for (const blob of blobs) {
            const userData = await userStore.get(blob.key, { type: 'json' });
            if (userData && userData.username && userData.username !== 'Usuário') {
                usersList.push({
                    username: userData.username,
                    balance: userData.balance || 0
                });
            }
        }

        // Ordenar por saldo (maior para menor)
        usersList.sort((a, b) => b.balance - a.balance);
        
        // Limitar a 10
        const top10 = usersList.slice(0, 10);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(top10)
        };

    } catch (error) {
        console.error('Erro top:', error);
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify([])
        };
    }
};
