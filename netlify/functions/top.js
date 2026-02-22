const fetch = require('node-fetch');

const FIREBASE_URL = 'https://bot-discord-4d74d-default-rtdb.firebaseio.com';

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    try {
        // Buscar todos os usuários
        const response = await fetch(`${FIREBASE_URL}/users.json`);
        const users = await response.json();

        if (!users) {
            return { statusCode: 200, headers, body: JSON.stringify([]) };
        }

        // Converter para array e ordenar
        const userList = Object.entries(users)
            .map(([id, data]) => ({
                username: data.username || 'Anônimo',
                balance: data.balance || 0
            }))
            .filter(user => user.username !== 'Anônimo' || user.balance > 0)
            .sort((a, b) => b.balance - a.balance)
            .slice(0, 10);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(userList)
        };

    } catch (error) {
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify([])
        };
    }
};
