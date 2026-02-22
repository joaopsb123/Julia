const fetch = require('node-fetch');

const FIREBASE_URL = 'https://bot-discord-4d74d-default-rtdb.firebaseio.com';
const DAILY_AMOUNT = 100;

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    try {
        const { userId, username } = JSON.parse(event.body);

        if (!userId) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ success: false, message: 'ID não fornecido' })
            };
        }

        // Buscar usuário
        const userRes = await fetch(`${FIREBASE_URL}/users/${userId}.json`);
        let user = await userRes.json();
        const now = new Date();

        if (!user) {
            user = {
                username: username || 'Usuário',
                balance: 0,
                last_daily: null,
                total_earned: 0,
                daily_streak: 0,
                created_at: now.toISOString()
            };
        }

        // Verificar se já resgatou hoje
        if (user.last_daily) {
            const lastDaily = new Date(user.last_daily);
            const timeDiff = (now - lastDaily) / 1000; // em segundos
            
            if (timeDiff < 86400) {
                return {
                    statusCode: 200,
                    headers,
                    body: JSON.stringify({
                        success: false,
                        message: '⏰ Você já resgatou hoje!',
                        timeLeft: 86400 - timeDiff
                    })
                };
            }
        }

        // Calcular streak
        let streak = 1;
        if (user.last_daily) {
            const last = new Date(user.last_daily);
            const hoursSince = (now - last) / (1000 * 60 * 60);
            streak = hoursSince < 48 ? (user.daily_streak || 0) + 1 : 1;
        }

        // Calcular bônus
        const bonus = 1 + (Math.min(streak, 7) * 0.1);
        const amount = Math.floor(DAILY_AMOUNT * bonus);

        // Atualizar usuário
        const updatedUser = {
            ...user,
            username: username || user.username,
            balance: (user.balance || 0) + amount,
            last_daily: now.toISOString(),
            daily_streak: streak,
            total_earned: (user.total_earned || 0) + amount
        };

        // Salvar no Firebase
        await fetch(`${FIREBASE_URL}/users/${userId}.json`, {
            method: 'PUT',
            body: JSON.stringify(updatedUser)
        });

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                amount,
                streak,
                message: `🎉 Ganhou ${amount} moedas! Streak: ${streak}`
            })
        };

    } catch (error) {
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ success: false, error: error.message })
        };
    }
};
