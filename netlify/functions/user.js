const fetch = require('node-fetch');

const FIREBASE_URL = 'https://bot-discord-4d74d-default-rtdb.firebaseio.com';

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    try {
        const userId = event.queryStringParameters?.id;
        
        if (!userId) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'ID não fornecido' })
            };
        }

        // Buscar usuário no Firebase
        const response = await fetch(`${FIREBASE_URL}/users/${userId}.json`);
        const data = await response.json();

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(data || {
                user_id: userId,
                username: '',
                balance: 0,
                daily_streak: 0,
                total_earned: 0
            })
        };
    } catch (error) {
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: error.message })
        };
    }
};
