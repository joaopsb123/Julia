// netlify/functions/claim.js
const { Blobs } = require('@netlify/blobs');

const DAILY_AMOUNT = 100;

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    };

    try {
        const { userId, username } = JSON.parse(event.body);
        const userStore = Blobs.store('users');
        
        let user = await userStore.get(userId, { type: 'json' });
        const now = new Date();

        if (!user) {
            user = {
                user_id: userId,
                username: username || 'Usuário',
                balance: 0,
                last_daily: null,
                total_earned: 0,
                daily_streak: 0
            };
        }

        // Verificar se já resgatou hoje
        if (user.last_daily) {
            const last = new Date(user.last_daily);
            const diff = (now - last) / 1000;
            if (diff < 86400) {
                return {
                    statusCode: 200,
                    headers,
                    body: JSON.stringify({
                        success: false,
                        message: '⏰ Já resgatou hoje!'
                    })
                };
            }
        }

        // Calcular streak e bônus
        let streak = 1;
        if (user.last_daily) {
            const last = new Date(user.last_daily);
            const hours = (now - last) / (1000 * 60 * 60);
            streak = hours < 48 ? (user.daily_streak || 0) + 1 : 1;
        }

        const bonus = 1 + (Math.min(streak, 7) * 0.1);
        const amount = Math.floor(DAILY_AMOUNT * bonus);

        // Atualizar usuário
        user = {
            ...user,
            username: username || user.username,
            balance: (user.balance || 0) + amount,
            last_daily: now.toISOString(),
            daily_streak: streak,
            total_earned: (user.total_earned || 0) + amount
        };

        await userStore.set(userId, JSON.stringify(user));

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                success: true,
                amount,
                streak,
                message: `🎉 Ganhou ${amount} moedas!`
            })
        };
    } catch (error) {
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({ 
                success: false, 
                error: error.message 
            })
        };
    }
};
