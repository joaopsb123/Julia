// netlify/functions/top.js
const { Blobs } = require('@netlify/blobs');

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    };

    try {
        const userStore = Blobs.store('users');
        const { blobs } = await userStore.list();
        
        if (!blobs || blobs.length === 0) {
            return { statusCode: 200, headers, body: JSON.stringify([]) };
        }

        const usersList = [];
        for (const blob of blobs) {
            const user = await userStore.get(blob.key, { type: 'json' });
            if (user && user.username) {
                usersList.push({
                    username: user.username,
                    balance: user.balance || 0
                });
            }
        }

        usersList.sort((a, b) => b.balance - a.balance);
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(usersList.slice(0, 10))
        };
    } catch (error) {
        return {
            statusCode: 200,
            headers,
            body: JSON.stringify([])
        };
    }
};
