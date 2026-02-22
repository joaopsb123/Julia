// Função para buscar usuário no Netlify Blobs
exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 204, headers, body: '' };
    }

    try {
        const { Blobs } = require('@netlify/blobs');
        const userId = event.queryStringParameters?.id;
        
        if (!userId) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'ID não fornecido' })
            };
        }

        // Conectar ao store de usuários
        const userStore = Blobs.store('users');
        
        // Buscar usuário
        let userData = await userStore.get(userId, { type: 'json' });
        
        if (!userData) {
            // Se não existir, retorna estrutura vazia
            userData = {
                user_id: userId,
                username: '',
                balance: 0,
                last_daily: null,
                total_earned: 0,
                daily_streak: 0,
                created_at: new Date().toISOString()
            };
        }

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(userData)
        };
    } catch (error) {
        console.error('Erro:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: 'Erro interno do servidor' })
        };
    }
};
