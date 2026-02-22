const admin = require('firebase-admin');

// Inicializar Firebase (apenas uma vez)
if (!admin.apps.length) {
    admin.initializeApp({
        credential: admin.credential.cert({
            projectId: process.env.FIREBASE_PROJECT_ID,
            clientEmail: process.env.FIREBASE_CLIENT_EMAIL,
            privateKey: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n')
        }),
        databaseURL: process.env.FIREBASE_DATABASE_URL || "https://bot-discord-4d74d-default-rtdb.firebaseio.com"
    });
}

const db = admin.database();

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    // Responder a requisições OPTIONS (CORS preflight)
    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 204, headers, body: '' };
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

        // Buscar usuário do Firebase Realtime Database
        const snapshot = await db.ref(`users/${userId}`).once('value');
        const userData = snapshot.val();

        if (!userData) {
            // Se não existir, retorna estrutura vazia
            return {
                statusCode: 200,
                headers,
                body: JSON.stringify({
                    user_id: userId,
                    username: '',
                    balance: 0,
                    last_daily: null,
                    total_earned: 0,
                    daily_streak: 0
                })
            };
        }

        // Garantir que todos os campos existam
        const responseData = {
            user_id: userId,
            username: userData.username || '',
            balance: userData.balance || 0,
            last_daily: userData.last_daily || null,
            total_earned: userData.total_earned || 0,
            daily_streak: userData.daily_streak || 0,
            created_at: userData.created_at || null
        };

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(responseData)
        };
    } catch (error) {
        console.error('Erro na função user:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ 
                error: 'Erro interno do servidor',
                details: error.message 
            })
        };
    }
};
