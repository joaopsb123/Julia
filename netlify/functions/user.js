// netlify/functions/user.js
const { Blobs } = require('@netlify/blobs');

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    };

    try {
        const userId = event.queryStringParameters?.id;
        
        if (!userId) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'ID não fornecido' })
            };
        }

        // Usar store local
        const userStore = Blobs.store('users');
        let userData = await userStore.get(userId, { type: 'json' });
        
        if (!userData) {
            userData = {
                user_id: userId,
                username: '',
                balance: 0,
                last_daily: null,
                total_earned: 0,
                daily_streak: 0
            };
        }

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(userData)
        };
    } catch (error) {
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ error: error.message })
        };
    }
};
